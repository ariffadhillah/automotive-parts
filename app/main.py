
import re
import csv
import json
import time
import random
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urljoin, urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

from app.browser import setup_browser

from app.collectors.listing_page_collector import (
    collect_product_urls_from_current_page,
)

# from app.collectors.product_detail_collector import (
#     collect_product_titles_for_page,
# )

from app.collectors.product_detail_bridge import (
    process_product_urls_for_page,
)


HOME_URL = "https://www.autodoc.de/"
TARGET_URL = (
    "https://www.autodoc.de/autoteile/"
    "bremsscheibe-10132/hyundai/accent/"
    "accent-ii-stufenheck-lc/18694-1-3"
)

def close_popups(browser) -> None:
    # Cookie popup
    try:
        accept_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'button[data-cookies="allow_all_cookies"]',
                )
            )
        )

        browser.execute_script(
            "arguments[0].click();",
            accept_button,
        )

        print("✅ Cookie popup ditutup.")
        time.sleep(1)

    except Exception:
        print(
            "ℹ️ Cookie popup tidak muncul "
            "atau sudah ditutup."
        )

    # Sidebar popup
    try:
        close_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'button.popup-sidebar__close'
                    '[data-popup-sidebar-close]',
                )
            )
        )

        browser.execute_script(
            "arguments[0].click();",
            close_button,
        )

        print("✅ Sidebar popup ditutup.")
        time.sleep(1)

    except Exception:
        print(
            "ℹ️ Sidebar popup tidak muncul "
            "atau sudah ditutup."
        )


# def open_to_website(browser):
def open_to_website(
    browser,
    detail_browser):

    browser.get(TARGET_URL)
    time.sleep(5)

    close_popups(browser)

    # product_urls = collect_listing_pages(
    #     browser=browser,
    #     base_url=TARGET_URL,
    # )

    product_urls = collect_listing_pages(
        browser=browser,
        detail_browser=detail_browser,
        base_url=TARGET_URL,
    )

    print("\nSemua pagination selesai.")
    print(
        f"Total URL produk unik ditemukan: "
        f"{len(product_urls)}"
    )

    return product_urls


def build_page_url(base_url: str, page_number: int) -> str:
    parts = urlsplit(base_url)

    query = dict(parse_qsl(parts.query))
    query["page"] = str(page_number)

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query),
            parts.fragment,
        )
    )

# def collect_listing_pages(
#     browser,
#     base_url: str,
# ) -> list[str]:

def collect_listing_pages(
    browser,
    detail_browser,
    base_url: str,
) -> list[str]:

    visited_final_urls: set[str] = set()
    collected_product_urls: set[str] = set()
    page_results: dict[int, int] = {}

    page_number = 1

    while True:
        requested_url = build_page_url(
            base_url=base_url,
            page_number=page_number,
        )

        print(f"\n{'=' * 60}")
        print(f"Membuka listing page {page_number}")
        print(f"Requested URL: {requested_url}")

        browser.get(requested_url)
        time.sleep(3)

        final_url = browser.current_url

        print(f"Final URL: {final_url}")

        # Contoh:
        # meminta page 5 tetapi diarahkan kembali ke page 4.
        if final_url in visited_final_urls:
            print(
                "Pagination selesai karena halaman "
                "terakhir sudah pernah dikunjungi."
            )
            break

        visited_final_urls.add(final_url)

        product_urls = (
            collect_product_urls_from_current_page(
                browser
            )
        )

        page_results[page_number] = len(
            product_urls
        )

        print(
            f"Ditemukan {len(product_urls)} URL "
            f"produk pada page {page_number}."
        )

        previous_total = len(
            collected_product_urls
        )

        collected_product_urls.update(
            product_urls
        )

        added_count = (
            len(collected_product_urls)
            - previous_total
        )

        print(f"URL produk baru: {added_count}")
        print(
            f"Total URL produk unik: "
            f"{len(collected_product_urls)}"
        )

        if not product_urls:
            print(
                "Tidak ada URL produk ditemukan. "
                "Pagination dihentikan."
            )
            break

        # Membaca halaman detail produk dari
        # listing page yang sedang aktif.
        # collect_product_titles_for_page(
        #     browser=browser,
        #     product_urls=product_urls,
        #     page_number=page_number,
        #     delay_seconds=3.0,
        # )

        # collect_product_titles_for_page(
        #     browser=browser,
        #     product_urls=product_urls[:3],
        #     page_number=page_number,
        #     delay_seconds=3.0,
        # )


        # collect_product_titles_for_page(
        #     browser=browser,
        #     product_urls=product_urls,
        #     page_number=page_number,
        #     delay_seconds=3.0,
        # )

        process_product_urls_for_page(
            detail_browser=detail_browser,
            product_urls=product_urls,
            page_number=page_number,
            delay_seconds=3.0,

            # Untuk test, hanya 3 produk per listing page.
            # limit=2,
        )

        print()
        print(
            f"Listing page {page_number} "
            f"beserta detail produknya selesai."
        )

        page_number += 1

    print("\nRingkasan listing per halaman:")

    for page, count in page_results.items():
        print(
            f"Page {page}: {count} produk"
        )

    return sorted(collected_product_urls)


def save_product_urls(
    product_urls: list[str],
) -> None:
    output_path = Path(
        "data/processed/product_urls.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            product_urls,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"URL produk disimpan ke: {output_path}")

# def main():
#     browser = setup_browser()

#     try:
#         product_urls = open_to_website(browser)
#         save_product_urls(product_urls)

#         print("\nDaftar URL produk:")

#         for index, product_url in enumerate(
#             product_urls,
#             start=1,
#         ):
#             print(f"{index}. {product_url}")

#     finally:
#         # input(
#         #     "\nTekan ENTER untuk menutup browser..."
#         # )
#         browser.quit()

def main():
    listing_browser = setup_browser()
    detail_browser = setup_browser()

    try:
        product_urls = open_to_website(
            browser=listing_browser,
            detail_browser=detail_browser,
        )

        save_product_urls(product_urls)

        print("\nDaftar URL produk:")

        for index, product_url in enumerate(
            product_urls,
            start=1,
        ):
            print(f"{index}. {product_url}")

    finally:
        listing_browser.quit()
        detail_browser.quit()

if __name__ == "__main__":
    main()


# https://www.autodoc.de/felgen/search?