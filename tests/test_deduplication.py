from processing.deduplication import find_duplicates, make_fingerprint


def test_duplicates_ignore_case_and_spaces():
    base = {"source": "Books to Scrape"}
    records = [
        {**base, "name_or_title": "Example Book Title"},
        {**base, "name_or_title": "  Example Book Title "},
        {**base, "name_or_title": "EXAMPLE BOOK TITLE"},
    ]

    unique, duplicates = find_duplicates(records)
    assert len(unique) == 1
    assert len(duplicates) == 2


def test_same_book_has_same_fingerprint():
    first = {
        "source": "Books to Scrape",
        "name_or_title": "Example Book Title",
    }
    second = {
        "source": "Books to Scrape",
        "name_or_title": " example-book title ",
    }
    assert make_fingerprint(first) == make_fingerprint(second)
