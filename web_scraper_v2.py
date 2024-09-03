import os
import json
import requests
import logging
import re
import time
from dataclasses import dataclass
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

__numberOfArticles = 20000
__ratioPercentThreshold = .9
RETRY_ATTEMPTS = 5
RETRY_DELAY = 10  # seconds

@dataclass
class Article:
    url: str
    post_id: str
    title: str
    keywords: list
    thumbnail: str
    published_time: str
    last_updated: str
    author: str
    full_text: str
    video_duration: str
    lang: str
    word_count: int
    description: str
    classes: list

class SitemapParser:
    def __init__(self, sitemap_url):
        self.sitemap_url = sitemap_url

    def _get_response(self, url):
        for attempt in range(RETRY_ATTEMPTS):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return response
            except RequestException as e:
                logging.error(f"Error fetching {url}: {e}. Attempt {attempt + 1}/{RETRY_ATTEMPTS}")
                time.sleep(RETRY_DELAY)
        return None

    def get_monthly_sitemap(self):
        response = self._get_response(self.sitemap_url)
        if response:
            soup = BeautifulSoup(response.content, "lxml")
            return [loc.text for loc in soup.find_all("loc")]
        return []

    def get_article_urls(self, sitemap_url):
        response = self._get_response(sitemap_url)
        if response:
            soup = BeautifulSoup(response.content, "lxml")
            return [loc.text for loc in soup.find_all("loc")]
        return []

class ArticleScraper:
    def __init__(self, url):
        self.url = url

    def _calculate_word_count(self, text):
        words = re.findall(r"\w+", text)
        return len(words)

    def _get_video_duration_from_play(self, soup):
        try:
            duration_div = soup.find("div", class_="ytp-cued-thumbnail-overlay-image")
            if duration_div:
                play_button = soup.find("button", class_="ytp-large-play-button ytp-button ytp-large-play-button-red-bg")
                if play_button:
                    duration_span = soup.find("span", class_="ytp-time-duration")
                    if duration_span:
                        return duration_span.get_text().strip()
            return None
        except Exception as e:
            logging.error(f"Error getting video duration by playing video: {e}")
            return None

    def scrape(self):
        for attempt in range(RETRY_ATTEMPTS):
            try:
                response = requests.get(self.url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "lxml")
                tawsiyat_metadata = soup.find("script", {"id": "tawsiyat-metadata"})
                if tawsiyat_metadata:
                    try:
                        tawsiyat_json = json.loads(tawsiyat_metadata.string)
                        post_id = tawsiyat_json.get("postid", "No post ID found")
                        title = tawsiyat_json.get("title", "No title found")
                        url = tawsiyat_json.get("url", "No URL found")
                        keywords = tawsiyat_json.get("keywords", "No keywords found").split(",")
                        thumbnail = tawsiyat_json.get("thumbnail", "No thumbnail found")
                        word_count = tawsiyat_json.get("word_count", 0)
                        lang = tawsiyat_json.get("lang", "No language found")
                        published_time = tawsiyat_json.get("published_time", "No published time found")
                        last_updated = tawsiyat_json.get("last_updated", "No last updated time found")
                        description = tawsiyat_json.get("description", "No description found")
                        author = tawsiyat_json.get("author", "No author found")
                        classes = tawsiyat_json.get("classes", "No classes found")
                    except json.JSONDecodeError:
                        logging.error("Error parsing Tawsiyat metadata")
                        return None
                else:
                    logging.error("No tawsiyat-metadata found")
                    return None
                paragraphs = soup.find_all("p")
                full_text = " ".join([p.get_text().replace("\n", " ") for p in paragraphs]) if paragraphs else None
                video_duration = self._get_video_duration_from_play(soup)
                return Article(
                    url=url,
                    post_id=post_id,
                    title=title,
                    keywords=keywords,
                    thumbnail=thumbnail,
                    published_time=published_time,
                    last_updated=last_updated,
                    author=author,
                    full_text=full_text,
                    video_duration=video_duration,
                    lang=lang,
                    word_count=word_count,
                    description=description,
                    classes=classes,
                )
            except RequestException as e:
                logging.error(f"Error scraping article {self.url}: {e}. Attempt {attempt + 1}/{RETRY_ATTEMPTS}")
                time.sleep(RETRY_DELAY)
        return None

class FileUtility:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def load_existing_articles(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def save_to_json(self, article, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r+", encoding="utf-8") as file:
                data = json.load(file)
                data.append(article.__dict__)
                file.seek(0)
                json.dump(data, file, ensure_ascii=False, indent=4)
        else:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump([article.__dict__], file, ensure_ascii=False, indent=4)

def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s", encoding="utf-8")
    logger = logging.getLogger()
    sitemap_parser = SitemapParser("https://www.almayadeen.net/sitemaps/all.xml")
    file_utility = FileUtility(output_dir="dbJSON")
    monthly_sitemaps = sitemap_parser.get_monthly_sitemap()
    logger.info(f"Found {len(monthly_sitemaps)} monthly sitemaps.")
    total_articles_scraped = 0
    for sitemap in monthly_sitemaps:
        if total_articles_scraped >= __numberOfArticles:
            break
        logger.info(f"Processing sitemap: {sitemap}")
        article_urls = sitemap_parser.get_article_urls(sitemap)
        logger.info(f"Found {len(article_urls)} articles in this sitemap.")
        year, month = sitemap.split("/")[-1].split("-")[1:3]
        file_path = os.path.join(file_utility.output_dir, f"articles_{year}_{month}.json")
        existing_articles = file_utility.load_existing_articles(file_path)
        already_scraped_urls = {article["url"] for article in existing_articles}
        remaining_urls = [url for url in article_urls if url not in already_scraped_urls]
        ratio_percent_threshold = int(len(article_urls) * __ratioPercentThreshold)
        if len(existing_articles) >= ratio_percent_threshold:
            logger.info(f"{int(__ratioPercentThreshold*100)}% or more articles already scraped for {year}-{month}. Skipping.")
            continue
        logger.info(f"Resuming from article {len(existing_articles) + 1} for {year}-{month}.")
        for index, url in enumerate(remaining_urls, start=len(existing_articles) + 1):
            if total_articles_scraped >= __numberOfArticles:
                break
            logger.info(f"Scraping article {index}")
            scraper = ArticleScraper(url)
            article = scraper.scrape()
            if article is not None:
                file_utility.save_to_json(article, file_path)
                total_articles_scraped += 1
        logger.info(f"Saved articles for {year}-{month}")
    logger.info(f"Total articles scraped: {total_articles_scraped}")

if __name__ == "__main__":
    main()
