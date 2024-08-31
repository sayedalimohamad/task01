import os, json, requests, logging, re
from dataclasses import dataclass
from bs4 import BeautifulSoup

__numberOfArticles = 20000


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

    def get_monthly_sitemap(self):
        try:
            response = requests.get(self.sitemap_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")
            return [loc.text for loc in soup.find_all("loc")]
        except requests.RequestException as e:
            logging.error(f"Error fetching sitemap: {e}")
            return []

    def get_article_urls(self, sitemap_url):
        try:
            response = requests.get(sitemap_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")
            return [loc.text for loc in soup.find_all("loc")]
        except requests.RequestException as e:
            logging.error(f"Error fetching {sitemap_url}: {e}")
            return []


class ArticleScraper:
    def __init__(self, url):
        self.url = url

    def _calculate_word_count(self, text):
        words = re.findall(r"\w+", text)
        return len(words)

    def scrape(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")
            title_tag = soup.find("h2")
            title = title_tag.get_text().replace("\n", " ") if title_tag else None
            meta_keywords = soup.find("meta", attrs={"name": "keywords"})
            keywords = (
                meta_keywords.get("content").replace("\n", " ").split(",")
                if meta_keywords
                else None
            )
            postid_meta_tag = soup.find("meta", attrs={"name": "postid"})
            post_id = (
                postid_meta_tag["content"].replace("\n", " ")
                if postid_meta_tag
                else None
            )
            thumbnail_tag = soup.find("meta", property="og:image")
            thumbnail = (
                thumbnail_tag["content"].replace("\n", " ") if thumbnail_tag else None
            )
            published_time_tag = soup.find("meta", property="article:published_time")
            published_time = (
                published_time_tag["content"].replace("\n", " ")
                if published_time_tag
                else None
            )
            modified_time_meta_tag = soup.find(
                "meta", attrs={"property": "article:modified_time"}
            )
            modified_time = (
                modified_time_meta_tag["content"].replace("\n", " ")
                if modified_time_meta_tag
                else None
            )
            author_meta = soup.find("meta", attrs={"name": "author"})
            author = author_meta["content"].replace("\n", " ") if author_meta else None
            paragraphs = soup.find_all("p")
            full_text = (
                " ".join([p.get_text().replace("\n", " ") for p in paragraphs])
                if paragraphs
                else None
            )
            video_meta = soup.find("meta", attrs={"property": "og:video_duration"})
            video_duration = (
                video_meta["content"].replace("\n", " ") if video_meta else None
            )
            language_tag = soup.find("html")
            lang = language_tag.get("lang").replace("\n", " ") if language_tag else None
            word_count = self._calculate_word_count(full_text) if full_text else None
            meta_description = soup.find("meta", attrs={"name": "description"})
            description = (
                meta_description["content"].replace("\n", " ")
                if meta_description
                else None
            )
            classes_content = soup.find("script", attrs={"type": "text/tawsiyat"})
            classes = (
                json.loads(classes_content.string)["classes"]
                if classes_content
                else None
            )
            return Article(
                url=self.url,
                post_id=post_id,
                title=title,
                keywords=keywords,
                thumbnail=thumbnail,
                published_time=published_time,
                last_updated=modified_time,
                author=author,
                full_text=full_text,
                video_duration=video_duration,
                lang=lang,
                word_count=word_count,
                description=description,
                classes=classes,
            )
        except requests.RequestException as e:
            logging.error(f"Error scraping article {self.url}: {e}")
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
        file_path = os.path.join(
            file_utility.output_dir, f"articles_{year}_{month}.json"
        )
        existing_articles = file_utility.load_existing_articles(file_path)
        already_scraped_urls = {article["url"] for article in existing_articles}
        remaining_urls = [
            url for url in article_urls if url not in already_scraped_urls
        ]
        ninety_percent_threshold = int(len(article_urls) * 0.9)
        if len(existing_articles) >= ninety_percent_threshold:
            logger.info(
                f"90% or more articles already scraped for {year}-{month}. Skipping."
            )
            continue
        logger.info(
            f"Resuming from article {len(existing_articles) + 1} for {year}-{month}."
        )
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
    print(f"Total articles scraped: {total_articles_scraped}")


if __name__ == "__main__":
    main()
