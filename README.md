# Article Scraper version 2 :

## Please remember the following: `"This is the most recent and final version you should use."`

## Overview

This code is designed to scrape and store articles from a website by processing its sitemap. It extracts relevant details from each article, such as the title, keywords, author, and content, and then saves this data into a JSON file. The code is structured with multiple classes to handle different tasks, ensuring a modular and organized approach.

### Author

**Name:** Mohamad Sayed Ali  
**ID:** 10119295

## Key Components and Benefits

### Article Class (`Article`)

- **Purpose**: Represents the structure of an article with attributes like URL, title, keywords, content, etc.
- **Benefit**: Provides a standardized format to store and manage the scraped article data.

### Sitemap Parser (`SitemapParser`)

- **Purpose**: Retrieves URLs from the website's sitemap.
- **Benefit**: Efficiently identifies and collects all article URLs from the sitemap, allowing the scraper to process a large number of articles systematically.

### Article Scraper (`ArticleScraper`)

- **Purpose**: Extracts detailed information from each article page, such as the title, publication date, and full text.
- **Benefit**: Automates the extraction of key details from articles, including handling edge cases where certain elements might be missing, thus improving the reliability of the scraping process.

### File Utility (`FileUtility`)

- **Purpose**: Handles the loading of existing articles and saving new articles into JSON files.
- **Benefit**: Ensures that scraped data is consistently saved and organized, avoiding duplication and enabling easy resumption of the scraping process if interrupted.

### Main Functionality (`main`)

- **Purpose**: Orchestrates the overall scraping process by iterating through the sitemap, scraping each article, and saving the data.
- **Benefit**: Provides a complete end-to-end solution for large-scale article scraping, with logging and checks to manage the number of articles processed and avoid unnecessary work.

## Additional Features

- **Error Handling**: The code includes robust error handling to manage network issues and missing data gracefully, ensuring the scraper can continue operating even when encountering issues.

- **90% Threshold Check**: Before scraping a month’s worth of articles, the program checks if 90% or more articles have already been scraped, skipping further processing if this is the case, thus saving time and resources.

- **Resume Functionality**: If the program is interrupted, it can resume from where it left off, processing only the remaining articles, ensuring efficient use of resources.

## Conclusion

This code provides an efficient and reliable way to scrape a large number of articles from a website. By modularizing tasks like sitemap parsing, article scraping, and file handling, it ensures that each component is easy to maintain, update, and extend. The code's built-in error handling and optimization strategies, such as skipping already processed articles, make it a powerful tool for large-scale web scraping projects.

---

# Webscraper

## Al Mayadeen Article Scraper

### Overview

This Python script scrapes articles from the Al Mayadeen website and saves the data to a JSON file. The script fetches all URLs from the sitemap, then retrieves the article URLs from each sitemap URL. It then scrapes the article data from each article URL and saves it to a JSON file. The script is designed to scrape 10,000 articles as required.

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

Change the Number of Articles: Modify the value of **numberOfUrls to scrape a different number of articles.
`**numberOfUrls = 10000 # Change to the desired number of articles to scrape`

## Testing

For fast testing and quick output, a Jupyter Notebook file named `testUnit.ipynb` is provided. This notebook allows you to test the script in a more interactive environment, ideal for rapid development and debugging.

## Output

The output file articles.json will be saved in the same directory as the script. It contains the JSON representation of the scraped article data, formatted with indentation for readability.

## Error Handling

The script includes basic error handling for HTTP requests. If an error occurs during the fetching of URLs or article content, an error message will be returned and printed to the console.
