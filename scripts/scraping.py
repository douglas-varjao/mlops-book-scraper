import os
import argparse
from urllib.parse import urljoin

import requests
import pandas as pd
from bs4 import BeautifulSoup

#--------------------------------------------#
#              CONFIGURAÇÕES                 #
#--------------------------------------------#

site = "https://books.toscrape.com/"
headers = {"User-Agent": "Mozilla/5.0 (compatible; TechChallengeScraper/1.0)"}
rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

#--------------------------------------------#
#                FUNÇÕES BASE                #
#--------------------------------------------#

def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def extract_categories() -> list[tuple[str, str]]:
    soup = get_soup(site)
    return [
        (a.text.strip(), urljoin(site, a.get('href')))
        for a in soup.select(".side_categories ul li ul li a")
    ]

def extract_books_from_category(cat_name: str, cat_url: str, start_id: int = 1) -> tuple[list[dict], int]:
    import re
    books = []
    next_url = cat_url
    book_id = start_id

    while next_url:
        soup = get_soup(next_url)
        products = soup.select("article.product_pod")

        for prod in products:
            title = prod.h3.a.get("title").strip()

            # limpar o preço
            price_text = prod.select_one("p.price_color").text.strip()
            price_text = re.sub(r"[^\d.]", "", price_text)
            price = float(price_text) if price_text else None

            rating = next((rating_map[c] for c in prod.p["class"] if c in rating_map), None)
            availability = prod.select_one("p.instock.availability").text.strip()
            image_url = urljoin(site, prod.select_one("div.image_container img")["src"])
            product_url = urljoin(site, prod.h3.a["href"])

            books.append({
                "id": book_id,
                "title": title,
                "price": price,
                "rating": rating,
                "availability": availability,
                "category": cat_name,
                "image_url": image_url,
                "product_url": product_url
            })
            book_id += 1

        next_link = soup.select_one("li.next a")
        next_url = urljoin(cat_url, next_link["href"]) if next_link else None

    return books, book_id

#--------------------------------------------#
#                EXECUÇÃO                    #
#--------------------------------------------#

def run(out_path: str):
    categories = extract_categories()
    all_books = []
    book_id = 1

    for name, href in categories:
        print(f"📚 Scraping category: {name}")
        cat_books, book_id = extract_books_from_category(name, href, book_id)
        all_books.extend(cat_books)

    df = pd.DataFrame(all_books)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"\n✅ Scraping completed. Data saved to {out_path}\n")

#--------------------------------------------#
#                 ENTRADA                    #
#--------------------------------------------#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Book Scraper")
    parser.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "data", "books.csv"),
                        help="Output CSV file path")
    args = parser.parse_args()
    run(args.out)
