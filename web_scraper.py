# Mohamad Sayed Ali - ID: 10119295
# This script scrapes articles from Al Mayadeen website and saves the data to a JSON file.
# The script fetches all URLs from the sitemap, then fetches the article URLs from each sitemap URL.
# It then scrapes the article data from each article URL and saves it to a JSON file.
# The script is designed to scrape 1000 articles for testing purposes, but it can be easily modified to scrape 10000 articles as required.

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
# - Language
# - Classes
# - Twitter Card
# - Twitter Creator
# - Facebook Publisher
# - Comments
# - Related Articles
# - Embedded Videos
# - Structured Data (JSON-LD)
# - Canonical URL
# - Favicon
# - Site Name
# - Publisher
# - Viewport
# - Article Tags
# - Open Graph Data
# - Twitter Card Data
# - Article Word Count

# The script also prints the number of articles collected so far to keep track of the progress.
# The script saves the data to a JSON file named 'articles.json' in the same directory as the script.


import requests
from bs4 import BeautifulSoup as bs
import json
import sys

# Set default encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

__urlAll = "https://www.almayadeen.net/sitemaps/all.xml"
__numberOfUrls = 1000

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
    
    # Initialize article data with URL
    article_data = {"url": url}

    # Post ID
    post_id_meta = soup.find('meta', {'name': 'postid'})
    article_data["post_id"] = post_id_meta['content'] if post_id_meta else 'No post ID found'

    # Title
    title_meta = soup.find('meta', {'property': 'og:title'})
    article_data["title"] = title_meta['content'] if title_meta else 'No title found'

    # Description
    description_meta = soup.find('meta', {'name': 'description'})
    article_data["description"] = description_meta['content'] if description_meta else 'No description found'

    # Keywords
    keywords_meta = soup.find('meta', {'name': 'keywords'})
    article_data["keywords"] = keywords_meta['content'].split(',') if keywords_meta else 'No keywords found'

    # Thumbnail
    thumbnail_meta = soup.find('meta', {'property': 'og:image'})
    article_data["thumbnail"] = thumbnail_meta['content'] if thumbnail_meta else 'No thumbnail found'

    # Publication Date
    pub_date_meta = soup.find('meta', {'property': 'article:published_time'})
    article_data["publication_date"] = pub_date_meta['content'] if pub_date_meta else 'No publication date found'

    # Last Updated Date
    last_updated_meta = soup.find('meta', {'property': 'article:modified_time'})
    article_data["last_updated_date"] = last_updated_meta['content'] if last_updated_meta else 'No last updated date found'

    # Author
    author_meta = soup.find('meta', {'name': 'author'})
    article_data["author"] = author_meta['content'] if author_meta else 'No author found'

    # Section
    section_meta = soup.find('meta', {'property': 'article:section'})
    article_data["section"] = section_meta['content'] if section_meta else 'No section found'

    # Breadcrumbs (if present)
    breadcrumbs = []
    breadcrumb_list = soup.find_all('li', {'class': 'breadcrumb-item'})
    for item in breadcrumb_list:
        breadcrumbs.append(item.text.strip())
    article_data["breadcrumbs"] = breadcrumbs if breadcrumbs else 'No breadcrumbs found'

    # Primary Image of the Page
    primary_image_meta = soup.find('meta', {'property': 'og:image'})
    article_data["primary_image"] = primary_image_meta['content'] if primary_image_meta else 'No primary image found'

    # Full Article Text
    paragraphs = soup.find_all('p')
    full_text = "\n".join([para.text for para in paragraphs])
    article_data["full_text"] = full_text if full_text.strip() else 'No full text found'

    # Language
    lang = soup.find('html')['lang'] if soup.find('html') and 'lang' in soup.find('html').attrs else 'No language found'
    article_data["language"] = lang

    # Extract Classes from Tawsiyat-Metadata
    tawsiyat_metadata = soup.find('script', {'id': 'tawsiyat-metadata'})
    if tawsiyat_metadata:
        try:
            tawsiyat_json = json.loads(tawsiyat_metadata.string)
            classes = tawsiyat_json.get('classes', [])
            article_data["classes"] = classes if classes else 'No classes found'
        except json.JSONDecodeError:
            article_data["classes"] = 'Error parsing classes'
    else:
        article_data["classes"] = 'No tawsiyat-metadata found'

    # Social Media Data
    twitter_card_meta = soup.find('meta', {'name': 'twitter:card'})
    article_data["twitter_card"] = twitter_card_meta['content'] if twitter_card_meta else 'No Twitter card found'
    
    twitter_creator_meta = soup.find('meta', {'name': 'twitter:creator'})
    article_data["twitter_creator"] = twitter_creator_meta['content'] if twitter_creator_meta else 'No Twitter creator found'
    
    facebook_publisher_meta = soup.find('meta', {'property': 'article:publisher'})
    article_data["facebook_publisher"] = facebook_publisher_meta['content'] if facebook_publisher_meta else 'No Facebook publisher found'
    
    # Comments (if available)
    comments = []
    comment_sections = soup.find_all('div', {'class': 'comment'})
    for comment in comment_sections:
        comment_text = comment.get_text(strip=True)
        if comment_text:
            comments.append(comment_text)
    article_data["comments"] = comments if comments else 'No comments found'

    # Related Articles (if available)
    related_articles = []
    related_links = soup.find_all('a', {'class': 'related-article-link'})
    for link in related_links:
        related_articles.append(link.get('href'))
    article_data["related_articles"] = related_articles if related_articles else 'No related articles found'

    # Embedded Videos (if available)
    videos = []
    video_iframes = soup.find_all('iframe')
    for iframe in video_iframes:
        video_src = iframe.get('src')
        if video_src and 'youtube' in video_src:
            videos.append(video_src)
    article_data["videos"] = videos if videos else 'No videos found'

    # Structured Data (JSON-LD)
    json_ld_data = []
    json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
    for script in json_ld_scripts:
        try:
            json_ld = json.loads(script.string)
            json_ld_data.append(json_ld)
        except json.JSONDecodeError:
            continue
    article_data["structured_data"] = json_ld_data if json_ld_data else 'No structured data found'

    # Canonical URL
    canonical_meta = soup.find('link', {'rel': 'canonical'})
    article_data["canonical_url"] = canonical_meta['href'] if canonical_meta else 'No canonical URL found'

    # Favicon
    favicon_link = soup.find('link', {'rel': 'icon'})
    article_data["favicon"] = favicon_link['href'] if favicon_link else 'No favicon found'

    # Site Name
    site_name_meta = soup.find('meta', {'property': 'og:site_name'})
    article_data["site_name"] = site_name_meta['content'] if site_name_meta else 'No site name found'

    # Publisher
    publisher_meta = soup.find('meta', {'name': 'publisher'})
    article_data["publisher"] = publisher_meta['content'] if publisher_meta else 'No publisher found'

    # Viewport (for responsive design)
    viewport_meta = soup.find('meta', {'name': 'viewport'})
    article_data["viewport"] = viewport_meta['content'] if viewport_meta else 'No viewport found'

    # Article Tags
    tags_meta = soup.find_all('meta', {'property': 'article:tag'})
    tags = [tag['content'] for tag in tags_meta] if tags_meta else []
    article_data["tags"] = tags if tags else 'No tags found'

    # Open Graph Data
    open_graph_data = {}
    og_tags = soup.find_all('meta', {'property': lambda x: x and x.startswith('og:')})
    for tag in og_tags:
        og_key = tag['property']
        og_value = tag['content']
        open_graph_data[og_key] = og_value
    article_data["open_graph_data"] = open_graph_data if open_graph_data else 'No Open Graph data found'

    # Twitter Card Data
    twitter_data = {}
    twitter_tags = soup.find_all('meta', {'name': lambda x: x and x.startswith('twitter:')})
    for tag in twitter_tags:
        twitter_key = tag['name']
        twitter_value = tag['content']
        twitter_data[twitter_key] = twitter_value
    article_data["twitter_data"] = twitter_data if twitter_data else 'No Twitter data found'

    # Article Word Count
    word_count = len(full_text.split())
    article_data["word_count"] = word_count if word_count > 0 else 'No word count found'

    return article_data

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
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
        save_to_json(all_articles, 'articles.json')

        # Print the total number of collected articles
        print("---------------------------------------")
        if len(all_articles) < __numberOfUrls:
            print(f"Only {len(all_articles)} articles collected.")
        else:
            print(f"Total number of articles collected: {len(all_articles)}")
        print("Data saved to articles.json")
    else:
        print(article_urls)

