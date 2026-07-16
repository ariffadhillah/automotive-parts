from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from app.parsers.product_oem_parser import (
    parse_product_oem_numbers,
    oem_numbers_to_text,
)

from app.parsers.product_specification_parser import (
    parse_product_specifications,
    specifications_to_dict,
)


def parse_product_detail(
    html: str,
) -> dict[str, Any]:
    soup = BeautifulSoup(
        html,
        "lxml",
    )

    page_title = None
    product_title = None

    if soup.title:
        page_title = soup.title.get_text(
            " ",
            strip=True,
        )

    h1_element = soup.select_one("h1")

    if h1_element:
        product_title = h1_element.get_text(
            " ",
            strip=True,
        )

    specifications = parse_product_specifications(
        html
    )

    specification_notices = [
        item
        for item in specifications
        if item.get("type") == "notice"
    ]

    valid_specifications = [
        item
        for item in specifications
        if item.get("type") == "specification"
    ]

    specification_map = specifications_to_dict(
        valid_specifications
    )

    oem_numbers = parse_product_oem_numbers(
        html
    )

    oem_numbers_text = oem_numbers_to_text(
        oem_numbers
    )

    return {
        "page_title": page_title,
        "product_title": product_title,
        "specifications": valid_specifications,
        "specification_notices": specification_notices,
        "specification_map": specification_map,
        "oem_numbers": oem_numbers,
        "oem_numbers_text": oem_numbers_text,
    }


def parse_product_title(
    html: str,
) -> dict[str, Any]:
    """
    Compatibility wrapper agar collector lama
    tetap dapat digunakan.
    """

    return parse_product_detail(html)