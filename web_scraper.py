# Mohamad Sayed Ali - ID: 10119295
# This script scrapes articles from Al Mayadeen website and saves the data to a JSON file.
# The script fetches all URLs from the sitemap, then fetches the article URLs from each sitemap URL.
# It then scrapes the article data from each article URL and saves it to a JSON file.
# The script is designed to scrape 100 articles for testing purposes, but it can be easily modified to scrape 10000 articles as required.
# The script is designed to scrape the following data for each article:
# - URL
# - Post ID
# - Title
# - Keywords
# - Thumbnail
# - Publication Date
# - Last Updated Date
# - Author
# - Full Article Text
# The script saves the data to a JSON file named 'articles.json' in the same directory as the script.


import requests
from bs4 import BeautifulSoup as bs
import json
import sys

# Set default encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

__urlAll = "https://www.almayadeen.net/sitemaps/all.xml"
__numberOfUrls = 100  # It must be 10000 as required, but for testing purposes,and fast output, I set it to 100

def get_xml(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching the URL: {e}"

def parse_xml(xml_content):
    soup = bs(xml_content, 'xml')
    urls = [loc.text for loc in soup.find_all('loc')]
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
            article_urls.extend(parse_xml(xml_content))  # Flatten the list of article URLs
    return article_urls

def scrape_article(url):
    html_content = get_xml(url)
    if html_content.startswith("Error"):
        return html_content

    soup = bs(html_content, 'html.parser')
    
    # URL
    article_data = {"url": url}
    
    # Post ID
    post_id = None
    post_id_meta = soup.find('meta', {'name': 'postid'})
    if post_id_meta:
        post_id = post_id_meta['content']
    else:
        post_id = 'No post ID found'
    article_data["post_id"] = post_id

    # Title
    details_white_box = soup.find('div', class_='details-white-box')
    title = details_white_box.find('h2').text if details_white_box and details_white_box.find('h2') else 'No title found'
    article_data["title"] = title

    # Keywords
    keywords_meta = soup.find('meta', {'name': 'keywords'})
    keywords = keywords_meta['content'].split(',') if keywords_meta else 'No keywords found'
    article_data["keywords"] = keywords

    # Thumbnail - checking common places like meta tags
    thumbnail_meta = soup.find('meta', {'property': 'og:image'})
    thumbnail = thumbnail_meta['content'] if thumbnail_meta else 'No thumbnail found'
    article_data["thumbnail"] = thumbnail

    # Publication Date
    pub_date_meta = soup.find('meta', {'property': 'article:published_time'})
    pub_date = pub_date_meta['content'] if pub_date_meta else 'No publication date found'
    article_data["publication_date"] = pub_date

    # Last Updated Date
    last_updated_meta = soup.find('meta', {'property': 'article:modified_time'})
    last_updated = last_updated_meta['content'] if last_updated_meta else 'No last updated date found'
    article_data["last_updated_date"] = last_updated

    # Author
    author_meta = soup.find('meta', {'name': 'author'})
    author = author_meta['content'] if author_meta else 'No author found'
    article_data["author"] = author

    # Full Article Text
    paragraphs = soup.find_all('p')
    full_text = "\n".join([para.text for para in paragraphs])
    article_data["full_text"] = full_text

    return article_data

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Example usage
if __name__ == "__main__":
    article_urls = get_all_article_links()
    all_articles = []
    if isinstance(article_urls, list):
        for url in article_urls[:__numberOfUrls]:
            article_data = scrape_article(url)
            all_articles.append(article_data)
            print(json.dumps(article_data, ensure_ascii=False, indent=4))
        save_to_json(all_articles, 'articles.json')
        print("---------------------------------------")
        print("Data saved to articles.json")
    else:
        print(article_urls)
