import hashlib
import re


def _normalize_key(value):
    value = str(value or "").lower()
    value = re.sub(r"[^\w\s]", " ", value)
    return " ".join(value.split())


def make_fingerprint(rec):
    if rec["source"] == "Books to Scrape":
        key = f'{rec["source"]} {rec["name_or_title"]}'
    else:
        key = (
            f'{rec["source"]} {rec.get("author")} '
            f'{rec.get("name_or_title", "")[:50]}'
        )

    normalized = _normalize_key(key)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def find_duplicates(records):
    seen = set()
    unique = []
    duplicates = []

    for rec in records:
        fingerprint = make_fingerprint(rec)
        if fingerprint in seen:
            duplicates.append(rec)
        else:
            seen.add(fingerprint)
            unique.append(rec)

    return unique, duplicates
