from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


AUTODOC_BASE_URL = "https://www.autodoc.de"

PRODUCT_PATH_PATTERN = re.compile(
    r"^/[a-z0-9-]+/\d+/?$",
    flags=re.IGNORECASE,
)


def normalize_product_url(url: str) -> str | None:
    """
    Validasi dan normalisasi URL detail produk AUTODOC.

    Contoh:
    https://www.autodoc.de/ridex/8015064#bremsscheibe
    menjadi:
    https://www.autodoc.de/ridex/8015064
    """
    if not url:
        return None

    absolute_url = urljoin(AUTODOC_BASE_URL, url.strip())
    parsed = urlparse(absolute_url)

    if parsed.netloc.lower() not in {
        "autodoc.de",
        "www.autodoc.de",
    }:
        return None

    if not PRODUCT_PATH_PATTERN.match(parsed.path):
        return None

    return urljoin(
        AUTODOC_BASE_URL,
        parsed.path.rstrip("/"),
    )


def extract_product_urls_from_html(
    html: str,
) -> list[str]:
    """
    Mengambil URL produk berdasarkan setiap kartu listing-item.

    Urutan fallback:
    1. a.listing-item__name[href]
    2. a.listing-item__image-product[href]
    3. elemen [data-link]
    4. pencarian berdasarkan article ID
    """
    soup = BeautifulSoup(html, "lxml")

    product_urls: dict[str, str] = {}

    listing_cards = soup.select(
        'div.listing-item[data-list-item-product]'
        '[data-article-id]'
    )

    print(
        f"Kartu produk pada HTML: {len(listing_cards)}"
    )

    for card in listing_cards:
        article_id = card.get("data-article-id")

        if not article_id:
            continue

        product_url = None

        # Pilihan utama: nama produk
        name_link = card.select_one(
            "a.listing-item__name[href]"
        )

        if name_link:
            product_url = normalize_product_url(
                name_link.get("href", "")
            )

        # Fallback: gambar produk
        if not product_url:
            image_link = card.select_one(
                "a.listing-item__image-product[href]"
            )

            if image_link:
                product_url = normalize_product_url(
                    image_link.get("href", "")
                )

        # Fallback: elemen role=link dengan data-link
        if not product_url:
            data_link_element = card.select_one(
                "[data-link]"
            )

            if data_link_element:
                product_url = normalize_product_url(
                    data_link_element.get("data-link", "")
                )

        # Fallback terakhir:
        # cari semua href/data-link dalam kartu
        if not product_url:
            candidate_elements = card.select(
                "[href], [data-link]"
            )

            for element in candidate_elements:
                candidate = (
                    element.get("href")
                    or element.get("data-link")
                    or ""
                )

                normalized = normalize_product_url(
                    candidate
                )

                if normalized:
                    product_url = normalized
                    break

        if not product_url:
            print(
                "⚠️ URL tidak ditemukan untuk "
                f"article_id={article_id}"
            )
            continue

        product_urls[article_id] = product_url

    return list(product_urls.values())