from __future__ import annotations

import time
from pathlib import Path

import requests


class AutoDocListingCollector:
    def __init__(
        self,
        timeout: int = 30,
        delay_seconds: float = 2.0,
    ) -> None:
        self.timeout = timeout
        self.delay_seconds = delay_seconds

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/150.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;"
                    "q=0.9,image/avif,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
        )

    def fetch(self, url: str) -> str:
        response = self.session.get(
            url,
            timeout=self.timeout,
        )

        response.raise_for_status()

        html = response.text

        if len(html) < 10_000:
            raise RuntimeError(
                f"HTML response looks incomplete: {len(html)} characters"
            )

        time.sleep(self.delay_seconds)

        return html

    @staticmethod
    def save_html(html: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")