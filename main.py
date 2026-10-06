import csv
import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "scraper.log"
CSV_FILE = OUTPUT_DIR / "final_dataset.csv"
JSON_FILE = OUTPUT_DIR / "summary_report.json"

COLUMNS = [
    "source", "source_url", "name_or_title", "category", "price",
    "availability", "rating", "author", "tags", "description", "scraped_at"
]


def configure_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def write_csv(records):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow({column: record.get(column) for column in COLUMNS})


def write_summary(stats):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with JSON_FILE.open("w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=4)


def process_source(name, scraper, start_time, stats):
    raw_records = scraper.scrape()
    stats["collected_per_source"][name] = len(raw_records)

    cleaned = []
    rejected = Counter()

    for raw in raw_records:
        cleaned_record = clean_record(raw)
        if not cleaned_record.get("scraped_at"):
            cleaned_record["scraped_at"] = start_time

        problems = validate_record(cleaned_record)
        if problems:
            for reason in problems:
                rejected[reason] += 1
            logging.warning(
                "Rejected %s record: %s",
                name,
                ", ".join(problems),
            )
            continue

        cleaned.append(cleaned_record)

    stats["cleaned_per_source"][name] = len(cleaned)
    stats["rejected_by_source"][name] = dict(rejected)
    stats["rejected_by_reason"].update(
        {f"{name}:{key}": value for key, value in rejected.items()}
    )
    return cleaned


def main():
    configure_logging()
    start_dt = datetime.now(timezone.utc)
    start_iso = start_dt.isoformat()

    stats = {
        "collected_per_source": {},
        "cleaned_per_source": {},
        "rejected_by_source": {},
        "rejected_by_reason": {},
        "duplicates_per_source": {},
        "duplicates_detected": 0,
        "final_record_count": 0,
        "start_time": start_iso,
        "end_time": None,
        "duration_seconds": None,
    }

    all_records = []

    sources = [
        ("Books to Scrape", BooksScraper()),
        ("Quotes to Scrape", QuotesScraper()),
    ]

    for name, scraper in sources:
        try:
            all_records.extend(
                process_source(name, scraper, start_iso, stats)
            )
        except Exception:
            logging.exception(
                "Unexpected failure in source %s; continuing with next source",
                name,
            )
            stats["collected_per_source"].setdefault(name, 0)
            stats["cleaned_per_source"].setdefault(name, 0)
            stats["rejected_by_source"].setdefault(name, {})

    unique, duplicates = find_duplicates(all_records)
    stats["duplicates_detected"] = len(duplicates)

    for source in ("Books to Scrape", "Quotes to Scrape"):
        stats["duplicates_per_source"][source] = sum(
            1 for record in duplicates if record.get("source") == source
        )

    write_csv(unique)

    end_dt = datetime.now(timezone.utc)
    stats["end_time"] = end_dt.isoformat()
    stats["duration_seconds"] = round(
        (end_dt - start_dt).total_seconds(), 3
    )
    stats["final_record_count"] = len(unique)

    write_summary(stats)

    logging.info("Final records: %d", len(unique))
    logging.info("Duplicates removed: %d", len(duplicates))
    logging.info("Output CSV: %s", CSV_FILE)
    logging.info("Summary JSON: %s", JSON_FILE)


if __name__ == "__main__":
    main()
