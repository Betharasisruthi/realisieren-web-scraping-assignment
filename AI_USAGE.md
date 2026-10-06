# AI_USAGE.md

## AI tools used

I used an AI assistant during development of this learning assignment.

## What AI was used for

The AI was used to help with:

1. Planning the ETL project structure.
2. Drafting initial Python functions for HTTP requests, pagination, cleaning, validation, and deduplication.
3. Suggesting unit-test cases.
4. Reviewing error-handling and logging structure.
5. Drafting documentation.

## Example prompts

- "Create a Python ETL project that scrapes Books to Scrape and Quotes to Scrape and follows the next link dynamically."
- "Write pure Python cleaning functions for whitespace, currency, word ratings, tags, and URLs."
- "Design a duplicate fingerprint using source and identifying fields while ignoring case, punctuation, and spacing."
- "Suggest pytest tests for cleaning, validation, and duplicate detection."

## Review and changes

The generated ideas were reviewed against the assignment reference document before being included.

Important design decisions made during review:

- The first draft omitted the Books `availability` field even though it is explicitly mentioned in the assignment. That was identified during review and corrected by adding `availability` to the common schema and capturing it from the listing page when present.
- An initial idea to scrape every book detail page just to populate category/description was not adopted for the core pipeline because those fields are optional in the common schema and the assignment says not to invent data; this avoids unnecessary traffic.

- Pagination follows `li.next > a` rather than using hard-coded page numbers.
- Both sources use the same common output schema.
- Missing optional fields are represented as empty CSV values rather than guessed data.
- Book category and description are left empty because the assignment explicitly notes that the listing page does not provide them.
- Validation returns specific rejection reasons.
- Duplicate detection uses different identifying fields for books and quotes as required.
- Each source is wrapped so a failure in one source does not prevent the other source from running.
- A 0.5 second request delay is included.
- Temporary HTTP errors are retried.
- Logging records requests, rejected records, and failures.

## Verification

Before submission, run:

```bash
pytest -q
python main.py
```

Then inspect:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

Also verify that both sources appear in the CSV and that the final JSON count matches the number of CSV data rows.

## Important

I understand that AI output should not be submitted blindly. I reviewed the generated code against the assignment requirements and should be able to explain the code, pagination, cleaning, validation, duplicate detection, retry handling, and output generation during an interview.
