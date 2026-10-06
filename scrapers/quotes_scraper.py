import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

START_URL = "https://quotes.toscrape.com/"


class QuotesScraper(BaseScraper):
    source = "Quotes to Scrape"

    def parse_quote(self, quote, page_url):
        try:
            text = quote.select_one("span.text")
            author = quote.select_one("small.author")

            if not text:
                raise ValueError("missing_quote_text")
            if not author:
                raise ValueError("missing_author")

            author_link = quote.select_one('a[href^="/author/"]')
            author_url = (
                urljoin(page_url, author_link["href"])
                if author_link and author_link.get("href")
                else page_url
            )

            tags = [tag.get_text(" ", strip=True) for tag in quote.select("a.tag")]

            return {
                "source": self.source,
                "source_url": page_url,
                "name_or_title": text.get_text(" ", strip=True),
                "category": "Quotes",
                "price_raw": None,
                "rating_raw": None,
                "availability_raw": None,
                "author": author.get_text(" ", strip=True),
                "tags": tags,
                "description": None,
            }
        except Exception as exc:
            logger.warning("Skipping quote record: %s", exc)
            return None

    def scrape(self):
        url = START_URL
        records = []
        page_number = 1

        while url:
            logger.info("Quotes page %d: %s", page_number, url)
            try:
                response = self.fetch(url)
            except Exception as exc:
                logger.error("Quotes page failed: %s | %s", url, exc)
                break

            soup = BeautifulSoup(response.text, "lxml")

            for quote in soup.select("div.quote"):
                record = self.parse_quote(quote, url)
                if record:
                    records.append(record)

            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page_number += 1

        logger.info("Quotes raw records: %d", len(records))
        return records
