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
    publication_date: str
    last_updated: str
    author: str
    full_text: str
    video_duration: str
    language: str
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

            # Extracting title
            title_tag = soup.find("h2")
            title = title_tag.get_text() if title_tag else "No Title Found"

            # Extracting keywords
            meta_keywords = soup.find("meta", attrs={"name": "keywords"})
            keywords = meta_keywords.get("content").split(",") if meta_keywords else []

            # Extracting post_id
            postid_meta_tag = soup.find("meta", attrs={"name": "postid"})
            post_id = postid_meta_tag["content"] if postid_meta_tag else None

            # Extracting thumbnail
            thumbnail_tag = soup.find("meta", property="og:image")
            thumbnail = thumbnail_tag["content"] if thumbnail_tag else ""

            # Extracting publication date
            publication_date_tag = soup.find("meta", property="article:published_time")
            publication_date = (
                publication_date_tag["content"] if publication_date_tag else ""
            )

            # Extracting last updated date
            modified_time_meta_tag = soup.find(
                "meta", attrs={"property": "article:modified_time"}
            )
            modified_time = (
                modified_time_meta_tag["content"] if modified_time_meta_tag else None
            )

            # Extracting author
            author_meta = soup.find("meta", attrs={"name": "author"})
            author = author_meta["content"] if author_meta else "No author available"

            # Extracting full text
            paragraphs = soup.find_all("p")
            full_text = " ".join([p.get_text() for p in paragraphs])

            # Extract video duration
            video_meta = soup.find("meta", attrs={"property": "og:video_duration"})
            video_duration = (
                video_meta["content"] if video_meta else "No video duration available"
            )

            # Extracting language
            language_tag = soup.find("html")
            language = (
                language_tag.get("lang") if language_tag else "No language available"
            )

            # Extracting word count
            word_count = self._calculate_word_count(full_text)

            # Extracting description
            meta_description = soup.find("meta", attrs={"name": "description"})
            description = meta_description["content"] if meta_description else None

            # Extracting classes
            classes_content = soup.find("script", attrs={"type": "text/tawsiyat"})
            classes = (
                json.loads(classes_content.string)["classes"] if classes_content else []
            )

            return Article(
                url=self.url,
                post_id=post_id,
                title=title,
                keywords=keywords,
                thumbnail=thumbnail,
                publication_date=publication_date,
                last_updated=modified_time,
                author=author,
                full_text=full_text,
                video_duration=video_duration,
                language=language,
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

    def save_to_json(self, articles, year, month):
        file_path = os.path.join(self.output_dir, f"articles_{year}_{month}.json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                [article.__dict__ for article in articles],
                file,
                ensure_ascii=False,
                indent=4,
            )

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(message)s", encoding="utf-8")
    logger = logging.getLogger()

    sitemap_parser = SitemapParser("https://www.almayadeen.net/sitemaps/all.xml")
    file_utility = FileUtility(output_dir="dbJSON")
    monthly_sitemaps = sitemap_parser.get_monthly_sitemap()
    logger.info(f"Found {len(monthly_sitemaps)} monthly sitemaps.")
    total_articles_scraped = 0

    for sitemap in monthly_sitemaps:
        if total_articles_scraped >= 1:
            break
        logger.info(f"Processing sitemap: {sitemap}")
        article_urls = sitemap_parser.get_article_urls(sitemap)
        logger.info(f"Found {len(article_urls)} articles in this sitemap.")
        articles = []
        for index, url in enumerate(article_urls, start=1):
            if total_articles_scraped >= __numberOfArticles:
                break
            logger.info(f"Scraping article {index}")
            scraper = ArticleScraper(url)
            article = scraper.scrape()
            if article is not None:
                articles.append(article)
                total_articles_scraped += 1
                logger.info(f"Articles scraped so far: {total_articles_scraped}")
        year, month = sitemap.split("/")[-1].split("-")[1:3]
        file_utility.save_to_json(articles, year, month)
        logger.info(f"Saved {len(articles)} articles for {year}-{month}")

    # Print the total number of articles scraped to the console
    print(f"Total articles scraped: {total_articles_scraped}")
    logger.info(f"Total articles scraped: {total_articles_scraped}")

if __name__ == "__main__":
    main()
