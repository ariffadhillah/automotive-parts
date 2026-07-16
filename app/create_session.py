from pathlib import Path

from app.collectors.selenium_session_collector import (
    AutoDocSeleniumSessionCollector,
)


TARGET_URL = (
    "https://www.autodoc.de/autoteile/"
    "bremsscheibe-10132/hyundai/accent/"
    "accent-ii-stufenheck-lc/18694-1-3"
)


def main() -> None:
    collector = AutoDocSeleniumSessionCollector(
        timeout_seconds=300,
    )

    collector.collect_session(
        url=TARGET_URL,
        cookie_output_path=Path(
            "data/session/autodoc_cookies.json"
        ),
        html_output_path=Path(
            "data/raw/"
            "hyundai_accent_1_3_brake_discs.html"
        ),
    )


if __name__ == "__main__":
    main()