import json
from pathlib import Path
import subprocess
import sys

import streamlit as st


st.set_page_config(
    page_title="Multi-Source Web Scraping Pipeline",
    page_icon="🕷️",
    layout="wide",
)


st.title("🕷️ Multi-Source Web Scraping & Data Consolidation")

st.write(
    "Python web scraping pipeline using Books to Scrape and Quotes to Scrape."
)


st.subheader("Project Workflow")

st.write(
    "Web Scraping → Cleaning → Validation → Deduplication → Consolidation"
)


if st.button("🚀 Run Scraper", type="primary"):

    with st.spinner("Running scraper... Please wait."):

        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True,
        )

    if result.returncode == 0:

        st.success("Scraping completed successfully!")

        report_path = Path("output/summary_report.json")

        if report_path.exists():

            with open(report_path, "r", encoding="utf-8") as file:
                report = json.load(file)

            st.subheader("Scraping Summary")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Books",
                report.get("cleaned_per_source", {}).get(
                    "Books to Scrape", 0
                ),
            )

            col2.metric(
                "Quotes",
                report.get("cleaned_per_source", {}).get(
                    "Quotes to Scrape", 0
                ),
            )

            col3.metric(
                "Duplicates",
                report.get("duplicates_detected", 0),
            )

            col4.metric(
                "Final Records",
                report.get("final_record_count", 0),
            )

            st.subheader("Summary Report")

            st.json(report)

        csv_path = Path("output/final_dataset.csv")

        if csv_path.exists():

            with open(csv_path, "rb") as file:

                st.download_button(
                    label="⬇️ Download Final Dataset",
                    data=file,
                    file_name="final_dataset.csv",
                    mime="text/csv",
                )

    else:

        st.error("Scraper failed.")

        if result.stderr:
            st.code(result.stderr)


st.divider()


st.subheader("Data Sources")

st.markdown(
    "- [Books to Scrape](https://books.toscrape.com/)\n"
    "- [Quotes to Scrape](https://quotes.toscrape.com/)"
)


st.subheader("Technologies")

st.write(
    "Python • Requests • BeautifulSoup • lxml • CSV • JSON • "
    "Logging • Pytest • Streamlit"
)