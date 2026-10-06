from processing.validation import validate_record


def valid_record():
    return {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/catalogue/example_1/index.html",
        "name_or_title": "Example Book",
        "price": 10.5,
        "rating": 4,
    }


def test_valid_record():
    assert validate_record(valid_record()) == []


def test_missing_name():
    record = valid_record()
    record["name_or_title"] = None
    assert "missing_name" in validate_record(record)


def test_invalid_rating():
    record = valid_record()
    record["rating"] = 6
    assert "invalid_rating" in validate_record(record)
