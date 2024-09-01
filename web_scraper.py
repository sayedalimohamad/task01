# Mohamad Sayed Ali - ID: 10119295
# This script scrapes articles from Al Mayadeen website and saves the data to a JSON file.
# The script fetches all URLs from the sitemap, then fetches the article URLs from each sitemap URL.
# It then scrapes the article data from each article URL and saves it to a JSON file.
# The script is designed to scrape 10000 articles as required.

# The script is designed to scrape the following data for each article:
# - URL
# - Post ID
# - Title
# - Keywords
# - Thumbnail
# - Word count
# - Language
# - Published time
# - Last updated time
# - Description
# - Author
# - Classes


# The script also prints the number of articles collected so far to keep track of the progress.
# The script saves the data to a JSON file named 'articles.json' in the same directory as the script.


import requests
from bs4 import BeautifulSoup as bs
import json
import sys

# Set default encoding to UTF-8
sys.stdout.reconfigure(encoding="utf-8")

__urlAll = "https://www.almayadeen.net/sitemaps/all.xml"
__numberOfUrls = 10000


def get_xml(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching the URL: {e}"


def parse_xml(xml_content):
    soup = bs(xml_content, "xml")
    urls = [loc.text for loc in soup.find_all("loc")]
    return urls


def get_all():
    xml_content = get_xml(__urlAll)
    if not xml_content.startswith("Error"):
        urls = parse_xml(xml_content)
        if len(urls) > __numberOfUrls:
            return urls[:__numberOfUrls]
        else:
            return urls
    else:
        return xml_content


def get_all_article_links():
    sitemap_urls = get_all()
    if not isinstance(sitemap_urls, list):
        return sitemap_urls  # return the error message if any

    article_urls = []
    for sitemap_url in sitemap_urls:
        xml_content = get_xml(sitemap_url)
        if not xml_content.startswith("Error"):
            article_urls.extend(
                parse_xml(xml_content)
            )  # Flatten the list of article URLs
    return article_urls


def scrape_article(url):

    html_content = get_xml(url)
    if html_content.startswith("Error"):
        return html_content

    soup = bs(html_content, "html.parser")

    # Initialize article data with URL
    article_data = {"url": url}

    # Extract data from Tawsiyat Metadata
    tawsiyat_metadata = soup.find("script", {"id": "tawsiyat-metadata"})
    if tawsiyat_metadata:
        try:
            tawsiyat_json = json.loads(tawsiyat_metadata.string)
            article_data["post_id"] = tawsiyat_json.get("postid", "No post ID found")
            article_data["title"] = tawsiyat_json.get("title", "No title found")
            article_data["url"] = tawsiyat_json.get("url", "No URL found")
            article_data["keywords"] = tawsiyat_json.get(
                "keywords", "No keywords found"
            ).split(",")
            article_data["thumbnail"] = tawsiyat_json.get(
                "thumbnail", "No thumbnail found"
            )
            article_data["word_count"] = tawsiyat_json.get(
                "word_count", "No word count found"
            )
            article_data["lang"] = tawsiyat_json.get("lang", "No language found")
            article_data["published_time"] = tawsiyat_json.get(
                "published_time", "No published time found"
            )
            article_data["last_updated"] = tawsiyat_json.get(
                "last_updated", "No last updated time found"
            )
            article_data["description"] = tawsiyat_json.get(
                "description", "No description found"
            )
            article_data["author"] = tawsiyat_json.get("author", "No author found")
            article_data["classes"] = tawsiyat_json.get("classes", "No classes found")
        except json.JSONDecodeError:
            return "Error parsing Tawsiyat metadata"
    else:
        return "No tawsiyat-metadata found"

    return article_data


def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Example usage

if __name__ == "__main__":
    print(f"Scraping {__numberOfUrls} articles data from Al Mayadeen website.")
    print("Wait to start the process...")
    article_urls = get_all_article_links()
    all_articles = []
    if isinstance(article_urls, list):
        for idx, url in enumerate(article_urls[:__numberOfUrls], start=1):
            article_data = scrape_article(url)
            all_articles.append(article_data)

            # Print the number of articles collected so far
            print(f"Article {idx} collected.")

        # Save to JSON file
        save_to_json(all_articles, "articles.json")

        # Print the total number of collected articles
        print("---------------------------------------")
        if len(all_articles) < __numberOfUrls:
            print(f"Only {len(all_articles)} articles collected.")
        else:
            print(f"Total number of articles collected: {len(all_articles)}")
        print("Data saved to articles.json")
    else:
        print(article_urls)
