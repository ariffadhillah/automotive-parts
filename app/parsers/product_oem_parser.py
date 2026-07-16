from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup


OEM_LINK_SELECTOR = (
    "div.product-oem "
    "ul.product-oem__list "
    "a.product-oem__link"
)


def parse_product_oem_numbers(
    html: str,
) -> list[dict[str, Any]]:
    """
    Mengambil nomor OE/OEM dari halaman detail produk AUTODOC.

    Contoh hasil:
    [
        {
            "oe_number": "5171225060",
            "manufacturer": "HYUNDAI",
            "display_text": "OE 5171225060 — HYUNDAI",
            "source_url": "...",
        }
    ]
    """

    soup = BeautifulSoup(html, "lxml")

    oem_records: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()

    for link in soup.select(OEM_LINK_SELECTOR):
        display_text = link.get_text(
            " ",
            strip=True,
        )

        source_url = link.get("href")

        oe_number = None
        manufacturer = None

        # Contoh:
        # OE 5171225060 — HYUNDAI
        match = re.match(
            r"^OE\s+(.+?)\s+[—–-]\s+(.+)$",
            display_text,
            flags=re.IGNORECASE,
        )

        if match:
            oe_number = match.group(1).strip()
            manufacturer = match.group(2).strip()

        else:
            # Fallback bila format teks sedikit berubah
            cleaned_text = re.sub(
                r"^OE\s+",
                "",
                display_text,
                flags=re.IGNORECASE,
            )

            parts = re.split(
                r"\s+[—–-]\s+",
                cleaned_text,
                maxsplit=1,
            )

            if parts:
                oe_number = parts[0].strip()

            if len(parts) > 1:
                manufacturer = parts[1].strip()

        if not oe_number:
            continue

        dedup_key = (
            oe_number,
            manufacturer or "",
        )

        if dedup_key in seen_keys:
            continue

        seen_keys.add(dedup_key)

        normalized_display = f"OE {oe_number}"

        if manufacturer:
            normalized_display += f" — {manufacturer}"

        oem_records.append(
            {
                "oe_number": oe_number,
                "manufacturer": manufacturer,
                "display_text": normalized_display,
                "source_url": source_url,
            }
        )

    return oem_records


def oem_numbers_to_text(
    oem_numbers: list[dict[str, Any]],
) -> str:
    """
    Mengubah list OEM menjadi satu string untuk CSV.
    """

    return ", ".join(
        str(item.get("display_text", "")).strip()
        for item in oem_numbers
        if item.get("display_text")
    )