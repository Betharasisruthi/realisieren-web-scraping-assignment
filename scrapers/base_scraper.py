import logging
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "RealisierenScrapingAssignment/1.0 (learning project)"
    })

    retries = Retry(
        total=3,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class BaseScraper:
    delay_seconds = 0.5
    timeout_seconds = 10

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or create_session()

    def fetch(self, url: str):
        logger.info("Request: %s", url)
        response = self.session.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        response.encoding = "utf-8"
        time.sleep(self.delay_seconds)
        return response
