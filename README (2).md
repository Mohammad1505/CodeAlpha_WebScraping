# Task 1: Web Scraping

Scrapes **1,000 books** from [books.toscrape.com](https://books.toscrape.com) (a public site made for scraping practice) using Python, `requests` and **BeautifulSoup**.

## Requirements covered

| Requirement                                     | How                                                                                                               |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Use BeautifulSoup                               | `scraper.py`                                                                                                      |
| Collect relevant datasets from public web pages | Books with price, rating, category, stock and description (numeric + categorical + text data for the later tasks) |
| Handle HTML structure and web navigation        | CSS selectors for each field; follows the "next" link through all 50 pages, then opens every book's detail page   |
| Create a custom dataset                         | `data/books_raw.csv`                                                                                              |

## How it works

1. Start at catalogue page 1 and collect each book's link (`article.product_pod h3 a`).
2. Open each book page and extract: title, category (breadcrumb), price, rating (from the CSS class `star-rating Three`), stock, UPC, reviews, description.
3. Follow `li.next a` to the next page until it no longer exists.
4. Save everything to `data/books_raw.csv`.

## Dataset columns

`title, category, price_gbp, rating, in_stock, stock_count, upc, num_reviews, description, url`

## Run

```bash
pip install -r requirements.txt
python scraper.py --max-pages 2   # quick test
python scraper.py                 # full run (~5-8 min)
```

## Results (fill in after running)

- Books scraped: 1000 / 1000
- Categories: 50
- Missing descriptions: 2

## Notes

- Polite scraping: 0.3 s delay between requests and a User-Agent header.
- Challenges solved: `Â£` encoding (set `utf-8`), relative URLs (`urljoin`), missing descriptions (return `None`).
