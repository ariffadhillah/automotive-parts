from __future__ import annotations

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from app.parsers.listing_url_parser import (
    extract_product_urls_from_html,
)


LISTING_CARD_SELECTOR = (
    'div.listing-item[data-list-item-product]'
    '[data-article-id]'
)


def scroll_listing_page(browser) -> None:
    """
    Scroll bertahap agar semua kartu dan lazy-loaded
    content sempat dimasukkan ke DOM.
    """
    last_height = 0

    for _ in range(12):
        current_height = browser.execute_script(
            "return document.body.scrollHeight"
        )

        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        time.sleep(1.5)

        new_height = browser.execute_script(
            "return document.body.scrollHeight"
        )

        if (
            new_height == current_height
            and new_height == last_height
        ):
            break

        last_height = new_height

    browser.execute_script(
        "window.scrollTo(0, 0);"
    )

    time.sleep(1)


def wait_for_listing_stable(
    browser,
    timeout_seconds: int = 30,
    stable_checks_required: int = 3,
) -> int:
    """
    Menunggu sampai jumlah listing-item tidak berubah
    dalam beberapa pemeriksaan berturut-turut.
    """
    WebDriverWait(
        browser,
        timeout_seconds,
    ).until(
        lambda driver: len(
            driver.find_elements(
                By.CSS_SELECTOR,
                LISTING_CARD_SELECTOR,
            )
        ) > 0
    )

    scroll_listing_page(browser)

    previous_count = -1
    stable_checks = 0
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        elements = browser.find_elements(
            By.CSS_SELECTOR,
            LISTING_CARD_SELECTOR,
        )

        current_count = len(elements)

        if current_count == previous_count:
            stable_checks += 1
        else:
            stable_checks = 0
            previous_count = current_count

        if stable_checks >= stable_checks_required:
            return current_count

        time.sleep(1)

    return previous_count


def collect_product_urls_from_current_page(
    browser,
) -> list[str]:
    card_count = wait_for_listing_stable(browser)

    print(
        f"Listing cards terdeteksi browser: "
        f"{card_count}"
    )

    html = browser.page_source

    product_urls = extract_product_urls_from_html(
        html
    )

    print(
        f"URL detail produk berhasil diparsing: "
        f"{len(product_urls)}"
    )

    if card_count != len(product_urls):
        print(
            "⚠️ Perbedaan jumlah kartu dan URL:"
        )
        print(f"   cards = {card_count}")
        print(f"   urls  = {len(product_urls)}")

    return product_urls