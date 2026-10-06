# Realisieren Technologies - Web Scraping ETL Assignment

## Overview

This project is a small ETL pipeline that collects records from two practice websites:

- Books to Scrape: https://books.toscrape.com/
- Quotes to Scrape: https://quotes.toscrape.com/

The pipeline follows the websites' `Next` links, converts both sources to a common schema, cleans values, validates records, removes duplicates, and writes the required output files.

## Python and setup

Python 3.10-3.12 is recommended.

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

From the project root:

```bash
python main.py
```

The program creates:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

## Website observations

### Books to Scrape

- Record: `article.product_pod`
- Title/link: `h3 > a`
- Price: `p.price_color`
- Rating: classes on `p.star-rating`, such as `Three`
- Next page: `li.next > a`

### Quotes to Scrape

- Record: `div.quote`
- Quote text: `span.text`
- Author: `small.author`
- Tags: `a.tag`
- Author link: `a[href^="/author/"]`
- Next page: `li.next > a`

Pagination is dynamic. The scrapers start at each home page and repeatedly follow the relative `li.next > a` link until there is no next link. Page numbers are not hard-coded.

## Common data model

| Column | Books | Quotes |
|---|---|---|
| source | Books to Scrape | Quotes to Scrape |
| source_url | Book detail page URL | Quote listing page URL |
| name_or_title | Book title | Quote text |
| category | Empty in this implementation | `Quotes` |
| price | Numeric price | Empty |
| availability | Availability text when present | Empty |
| rating | Integer 1-5 | Empty |
| author | Empty | Author name |
| tags | Empty | Lowercase, sorted, semicolon-separated |
| description | Empty | Empty |
| scraped_at | UTC timestamp | UTC timestamp |

### Optional source-specific fields

The Books listing provides title, price, rating and product URL, while availability can be captured from the listing. Category and description are not assumed when they are absent from the listing; the pipeline therefore leaves unavailable fields empty rather than inventing values. The standardized schema still reserves those fields so the two sources can be consolidated safely.

## Cleaning

Cleaning is kept in `processing/cleaning.py` so it can be tested without internet access.

- Text: removes extra whitespace, tabs, newlines and non-breaking spaces.
- Quote text: removes surrounding curly/double quotation marks.
- Price: extracts the numeric value from strings such as `£51.77`.
- Rating: maps `One` through `Five` to integers 1-5.
- Tags: lowercases, removes duplicates, sorts, and joins with `;`.
- URLs: normalizes relative/absolute URLs and accepts only HTTP(S).

## Validation

`processing/validation.py` returns a list of rejection reasons.

Rules:

- Source must be one of the two allowed sources.
- `name_or_title` must be present.
- `source_url` must start with `http://` or `https://`.
- Price, when present, must be a number >= 0.
- Rating, when present, must be an integer from 1 to 5.

A bad record is logged and skipped instead of stopping the complete run.

## Deduplication

`processing/deduplication.py` creates a SHA-256 fingerprint.

- Books: source + title.
- Quotes: source + author + first 50 characters of quote text.

Before hashing, the key is lowercased, punctuation is removed, and whitespace is collapsed. Duplicate records are removed from the final CSV.

The real practice sites are expected to contain unique records, so a real run may report zero duplicates. Unit tests deliberately create duplicates to verify the logic.

## Network and error handling

A shared `requests.Session` is used by both scrapers. Temporary HTTP errors (429, 500, 502, 503 and 504) are retried with exponential backoff. Requests use a timeout and the response encoding is set to UTF-8.

There is approximately a 0.5 second delay between requests. A failed page is logged as an error and stops only that source; the other source is still attempted.

## Tests

Run:

```bash
pytest -q
```

Tests cover:

- text cleaning
- quote stripping
- price cleaning
- rating cleaning
- tag cleaning
- validation failures
- duplicate detection ignoring case/spacing

## Summary report

`output/summary_report.json` contains:

- raw records collected per source
- records after cleaning
- rejected records by source/reason
- duplicate count
- final record count
- start time
- end time
- duration in seconds

The values in the report are generated from the actual run and are not hard-coded.

## Assumptions and limitations

1. The websites are used only as practice scraping targets.
2. No login, CAPTCHA, protection bypass, API key, or paid service is used.
3. Book category and description are left empty because they are not present on the listing page.
4. Quote `source_url` is documented as the author page URL when available; otherwise it falls back to the quote page URL.
5. The output is intended to be reproducible from a clean Python environment.

## AI usage

See `AI_USAGE.md` for an honest record of AI assistance and verification.
