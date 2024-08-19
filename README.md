# Webscraper
## Al Mayadeen Article Scraper

### Overview

This Python script scrapes articles from the Al Mayadeen website and saves the data to a JSON file. The script fetches all URLs from the sitemap, then retrieves the article URLs from each sitemap URL. It then scrapes the article data from each article URL and saves it to a JSON file. The script is designed to scrape 10,000 articles as required.

### Author

**Name:** Mohamad Sayed Ali  
**ID:** 10119295

### Features

The script is designed to scrape the following data for each article:

- **URL:** The link to the article.
- **Post ID:** A unique identifier for the article.
- **Title:** The title of the article.
- **Keywords:** Keywords associated with the article.
- **Thumbnail:** The URL of the article's thumbnail image.
- **Word Count:** The total number of words in the article.
- **Language:** The language in which the article is written.
- **Published Time:** The date and time when the article was published.
- **Last Updated Time:** The date and time when the article was last updated.
- **Description:** A brief summary or description of the article.
- **Author:** The name of the article's author.
- **Classes:** Any relevant classification or categories assigned to the article.

### How It Works

1. **Sitemap Retrieval:** The script first fetches all URLs from the main sitemap of the Al Mayadeen website.
2. **Article URL Extraction:** It retrieves the article URLs from the individual sitemap URLs.
3. **Article Scraping:** The script scrapes the necessary data for each article URL.
4. **Data Storage:** The scraped data is saved into a JSON file named `articles.json`.

The script also prints the number of articles collected so far to keep track of the progress.

### Configuration

- The script is configured to scrape up to 10,000 articles by default. This can be adjusted by modifying the `__numberOfUrls` variable.

### Dependencies

- `requests`: For making HTTP requests to fetch webpage content.
- `BeautifulSoup (bs4)`: For parsing and extracting data from HTML and XML documents.
- `JSON`: For saving the scraped data in JSON format.

### Usage

To run the script, simply execute it in your Python environment. The script will print the scraped data for each article to the console and save all the data in the `articles.json` file.

**Example command to run the script:**
```bash
python web_scraper.py

```

## Customization
Change the Number of Articles: Modify the value of __numberOfUrls to scrape a different number of articles.
`__numberOfUrls = 10000  # Change to the desired number of articles to scrape`

## Testing
For fast testing and quick output, a Jupyter Notebook file named `testUnit.ipynb` is provided. This notebook allows you to test the script in a more interactive environment, ideal for rapid development and debugging.

## Output
The output file articles.json will be saved in the same directory as the script. It contains the JSON representation of the scraped article data, formatted with indentation for readability.

## Error Handling
The script includes basic error handling for HTTP requests. If an error occurs during the fetching of URLs or article content, an error message will be returned and printed to the console.
