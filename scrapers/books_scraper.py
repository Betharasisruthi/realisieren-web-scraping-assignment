import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

START_URL = "https://books.toscrape.com/"


class BooksScraper(BaseScraper):
    source = "Books to Scrape"

    def parse_book(self, article, page_url):
        try:
            link = article.select_one("h3 > a")
            price = article.select_one("p.price_color")
            rating = article.select_one("p.star-rating")

            if not link:
                raise ValueError("missing_book_link")

            return {
                "source": self.source,
                "source_url": urljoin(page_url, link.get("href", "")),
                "name_or_title": link.get("title") or link.get_text(" ", strip=True),
                "category": None,
                "price_raw": price.get_text(" ", strip=True) if price else None,
                "rating_raw": " ".join(rating.get("class", [])) if rating else None,
                "availability_raw": None,
                "author": None,
                "tags": None,
                "description": None,
            }
        except Exception as exc:
            logger.warning("Skipping book record: %s", exc)
            return None

    def scrape(self):
        url = START_URL
        records = []
        page_number = 1

        while url:
            logger.info("Books page %d: %s", page_number, url)
            try:
                response = self.fetch(url)
            except Exception as exc:
                logger.error("Books page failed: %s | %s", url, exc)
                break

            soup = BeautifulSoup(response.text, "lxml")

            for article in soup.select("article.product_pod"):
                record = self.parse_book(article, url)
                if record:
                    availability = article.select_one("p.instock.availability")
                    record["availability_raw"] = availability.get_text(" ", strip=True) if availability else None
                    records.append(record)

            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page_number += 1

        logger.info("Books raw records: %d", len(records))
        return records
