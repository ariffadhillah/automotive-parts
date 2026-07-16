from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup, Tag


SPECIFICATION_CONTAINER_SELECTOR = (
    "div.product-description__info "
    "ul.product-description__list"
)

SPECIFICATION_ITEM_SELECTOR = (
    "li.product-description__item"
)

TITLE_SELECTOR = (
    ".product-description__item-title"
)

VALUE_SELECTOR = (
    ".product-description__item-value"
)


INVALID_VALUES = {
    "",
    "-",
    "—",
    "n/a",
    "none",
    "null",
}

INVALID_VALUES_CASEFOLD = {
    value.casefold()
    for value in INVALID_VALUES
}




def clean_text(value: str | None) -> str:
    """
    Membersihkan whitespace tanpa mengubah isi teknis.

    Contoh:
    '  60 / 55  ' -> '60 / 55'
    'schwarz\\nschwarz' -> 'schwarz schwarz'
    """
    if not value:
        return ""

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def normalize_field_name(name: str | None) -> str:
    """
    Membersihkan nama field.

    Contoh:
    'Durchmesser: ' -> 'Durchmesser'
    """
    cleaned = clean_text(name)

    return cleaned.rstrip(":").strip()


def extract_element_text(
    element: Tag | None,
) -> str:
    """
    Mengambil semua text dari sebuah elemen,
    termasuk jika value memiliki nested span atau icon.

    Tag <img> tidak ikut karena get_text hanya mengambil teks.
    """
    if element is None:
        return ""

    return clean_text(
        element.get_text(
            " ",
            strip=True,
        )
    )


def is_informational_value(
    value_element: Tag | None,
    value_text: str,
) -> bool:
    """
    Mendeteksi value yang bukan spesifikasi teknis,
    tetapi pesan/popup pemilihan kendaraan.
    """

    value_lower = clean_text(value_text).casefold()

    informational_markers = (
        "diese eigenschaft variiert je nach fahrzeugmodell",
        "variiert je nach fahrzeugmodell",
    )

    if any(
        marker in value_lower
        for marker in informational_markers
    ):
        return True

    if value_element is None:
        return False

    # Periksa atribut pada value element itu sendiri
    if (
        value_element.get("data-popup-show-ajax")
        == "data-popup-search-car"
    ):
        return True

    if (
        value_element.get("data-ajax-selector-popup-type")
        == "car"
    ):
        return True

    # Periksa elemen di dalam value element
    popup_element = value_element.select_one(
        '[data-popup-show-ajax="data-popup-search-car"]'
    )

    if popup_element is not None:
        return True

    car_selector_element = value_element.select_one(
        '[data-ajax-selector-popup-type="car"]'
    )

    if car_selector_element is not None:
        return True

    return False

def find_value_from_item(
    item: Tag,
    title_element: Tag | None,
) -> tuple[str, Tag | None]:
    """
    Mengembalikan:
    - value text
    - elemen HTML value
    """

    value_element = item.select_one(
        VALUE_SELECTOR
    )

    if value_element:
        return (
            extract_element_text(value_element),
            value_element,
        )

    if title_element:
        sibling_texts: list[str] = []

        for sibling in title_element.next_siblings:
            if isinstance(sibling, Tag):
                text = extract_element_text(sibling)
            else:
                text = clean_text(str(sibling))

            if text:
                sibling_texts.append(text)

        if sibling_texts:
            return (
                clean_text(" ".join(sibling_texts)),
                None,
            )

    item_text = extract_element_text(item)
    title_text = extract_element_text(title_element)

    if title_text and item_text.startswith(title_text):
        return (
            clean_text(item_text[len(title_text):]),
            None,
        )

    return item_text, None




def parse_product_specifications(
    html: str,
) -> list[dict[str, Any]]:
    """
    Parser dinamis untuk seluruh kategori AUTODOC.

    Tidak memerlukan daftar field sebelumnya.
    Setiap pasangan title/value akan otomatis diambil.
    """

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    specifications: list[dict[str, Any]] = []

    container = soup.select_one(
        SPECIFICATION_CONTAINER_SELECTOR
    )

    if container is None:
        return specifications

    items = container.select(
        SPECIFICATION_ITEM_SELECTOR
    )


    for position, item in enumerate(
        items,
        start=1,
    ):
        title_element = item.select_one(
            TITLE_SELECTOR
        )

        if title_element is None:
            continue

        name_original = normalize_field_name(
            extract_element_text(
                title_element
            )
        )

        value_original, value_element = (
            find_value_from_item(
                item=item,
                title_element=title_element,
            )
        )

        if not name_original:
            continue

        if not value_original:
            continue

        if (
            value_original.casefold()
            in INVALID_VALUES_CASEFOLD
        ):
            continue

        if is_informational_value(
            value_element=value_element,
            value_text=value_original,
        ):
            specification_type = "notice"
        else:
            specification_type = "specification"

        specifications.append(
            {
                "position": position,
                "name_original": name_original,
                "value_original": value_original,
                "type": specification_type,
                "name_ar": None,
                "value_ar": None,
                "raw_html": str(item),
            }
        )



    return specifications



def specifications_to_dict(
    specifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Mengubah list spesifikasi menjadi dictionary.

    Jika nama yang sama mempunyai beberapa nilai berbeda,
    nilainya disimpan sebagai list agar tidak saling menimpa.
    """

    result: dict[str, Any] = {}

    for specification in specifications:
        name = clean_text(
            str(
                specification.get(
                    "name_original",
                    "",
                )
            )
        )

        value = clean_text(
            str(
                specification.get(
                    "value_original",
                    "",
                )
            )
        )

        if not name or not value:
            continue

        if name not in result:
            result[name] = value
            continue

        existing_value = result[name]

        if existing_value == value:
            continue

        if isinstance(existing_value, list):
            if value not in existing_value:
                existing_value.append(value)
        else:
            result[name] = [
                existing_value,
                value,
            ]

    return result
    