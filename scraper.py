"""
Task 1: Web Scraping with BeautifulSoup
Source: https://books.toscrape.com (public practice site)

Run:  python scraper.py                 -> scrapes all 1000 books (~5-8 min)
      python scraper.py --max-pages 2   -> quick test (~40 books)
Output: data/books_raw.csv
"""
import argparse
import os
import re
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

START_URL = "https://books.toscrape.com/catalogue/page-1.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (Internship-Project; educational scraping)"}
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def get_soup(url, retries=3):
    """Download a page (with simple retries) and return a BeautifulSoup object."""
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.encoding = "utf-8"                      # avoids the 'Â£' encoding bug
            if r.status_code == 200:
                return BeautifulSoup(r.text, "html.parser")
        except requests.RequestException as e:
            print(f"  retry {attempt + 1} for {url}: {e}")
        time.sleep(1 + attempt)
    return None


def parse_book(soup, url):
    """Extract one book's data from its detail page."""
    table = {tr.th.get_text(strip=True): tr.td.get_text(strip=True)
             for tr in soup.select("table.table-striped tr")}
    desc = soup.select_one("#product_description")           # may not exist
    p = desc.find_next_sibling("p") if desc else None
    stock = re.search(r"\d+", table.get("Availability", ""))
    rating_class = soup.select_one("p.star-rating")["class"][1]   # e.g. "Three"
    return {
        "title": soup.select_one("div.product_main h1").get_text(strip=True),
        "category": soup.select("ul.breadcrumb li a")[-1].get_text(strip=True),
        "price_gbp": float(re.sub(r"[^\d.]", "", table["Price (incl. tax)"])),
        "rating": RATING_MAP[rating_class],
        "in_stock": "In stock" in table.get("Availability", ""),
        "stock_count": int(stock.group()) if stock else 0,
        "upc": table.get("UPC"),
        "num_reviews": int(table.get("Number of reviews", 0)),
        "description": p.get_text(strip=True) if p else None,
        "url": url,
    }


def scrape(max_pages=None, delay=0.3):
    rows, url, page = [], START_URL, 1
    while url:                                                # web navigation loop
        soup = get_soup(url)
        if soup is None:
            break
        links = [urljoin(url, a["href"]) for a in soup.select("article.product_pod h3 a")]
        for link in links:
            book = get_soup(link)
            if book is not None:
                try:
                    rows.append(parse_book(book, link))
                except Exception as e:                        # one bad page must not stop the crawl
                    print("  skipped", link, e)
            time.sleep(delay)                                 # be polite
        print(f"Page {page}: {len(links)} books (total {len(rows)})")
        nxt = soup.select_one("li.next a")                    # follow pagination
        url = urljoin(url, nxt["href"]) if nxt and (max_pages is None or page < max_pages) else None
        page += 1
    return pd.DataFrame(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=None)
    args = ap.parse_args()

    os.makedirs("data", exist_ok=True)
    df = scrape(max_pages=args.max_pages)
    df.to_csv("data/books_raw.csv", index=False)
    print(f"\nSaved data/books_raw.csv  ->  {df.shape[0]} rows, {df.shape[1]} columns")
    print("Missing values:\n", df.isna().sum())
