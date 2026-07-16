# from __future__ import annotations

# import json
# import time
# from pathlib import Path

# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait

# from app.parsers.product_detail_parser import (
#     parse_product_title,
# )


# CLOUDFLARE_MARKERS = (
#     "nur einen moment",
#     "just a moment",
#     "challenges.cloudflare.com",
#     "cf-turnstile",
#     "cf-chl-",
#     "bestätigen sie, dass sie ein mensch sind",
# )


# def is_cloudflare_page(html: str) -> bool:
#     html_lower = html.lower()

#     return any(
#         marker in html_lower
#         for marker in CLOUDFLARE_MARKERS
#     )


# def wait_for_product_detail(
#     browser,
#     timeout_seconds: int = 30,
# ) -> None:
#     """
#     Menunggu halaman detail produk benar-benar siap diparsing.
#     """

#     WebDriverWait(
#         browser,
#         timeout_seconds,
#     ).until(
#         lambda driver: (
#             len(
#                 driver.find_elements(
#                     By.CSS_SELECTOR,
#                     "h1",
#                 )
#             ) > 0
#             and (
#                 len(
#                     driver.find_elements(
#                         By.CSS_SELECTOR,
#                         (
#                             "div.product-description__info "
#                             "ul.product-description__list"
#                         ),
#                     )
#                 ) > 0
#                 or len(
#                     driver.find_elements(
#                         By.CSS_SELECTOR,
#                         "div.product-oem",
#                     )
#                 ) > 0
#             )
#         )
#     )

#     time.sleep(2)


# def save_page_detail_results(
#     page_number: int,
#     records: list[dict],
# ) -> Path:
#     """
#     Menyimpan hasil halaman listing tertentu.

#     Contoh:
#     data/processed/product_details/page_1.json
#     """

#     output_path = Path(
#         "data/processed/product_details/"
#         f"page_{page_number}.json"
#     )

#     output_path.parent.mkdir(
#         parents=True,
#         exist_ok=True,
#     )

#     output_path.write_text(
#         json.dumps(
#             records,
#             ensure_ascii=False,
#             indent=2,
#         ),
#         encoding="utf-8",
#     )

#     return output_path


# def collect_product_titles_for_page(
#     browser,
#     product_urls: list[str],
#     page_number: int,
#     delay_seconds: float = 3.0,
# ) -> list[dict]:
#     """
#     Membuka URL produk dari satu listing page,
#     kemudian membaca title masing-masing produk.
#     """

#     page_records: list[dict] = []

#     print()
#     print(
#         f"Mulai membaca detail produk "
#         f"dari listing page {page_number}"
#     )

#     print(
#         f"Jumlah produk yang akan dibuka: "
#         f"{len(product_urls)}"
#     )

#     for product_index, product_url in enumerate(
#         product_urls,
#         start=1,
#     ):
#         print()
#         print(
#             f"[Page {page_number}] "
#             f"Produk {product_index}/{len(product_urls)}"
#         )
#         print(f"URL: {product_url}")


#         record = {
#             "listing_page": page_number,
#             "product_index": product_index,
#             "requested_url": product_url,
#             "final_url": None,
#             "page_title": None,
#             "product_title": None,
#             "specifications": [],
#             "specification_notices": [],
#             "specification_map": {},
#             "oem_numbers": [],
#             "oem_numbers_text": "",
#             "status": "pending",
#             "error": None,
#         }

#         try:
#             browser.get(product_url)

#             wait_for_product_detail(
#                 browser=browser,
#                 timeout_seconds=30,
#             )

#             html = browser.page_source

#             if is_cloudflare_page(html):
#                 record["status"] = "cloudflare_challenge"
#                 record["final_url"] = browser.current_url

#                 print(
#                     "⚠️ Cloudflare challenge ditemukan "
#                     "pada halaman produk."
#                 )

#                 page_records.append(record)

#                 save_page_detail_results(
#                     page_number=page_number,
#                     records=page_records,
#                 )

#                 continue


#             parsed = parse_product_title(html)

#             record["final_url"] = browser.current_url

#             record["page_title"] = parsed.get(
#                 "page_title"
#             )

#             record["product_title"] = parsed.get(
#                 "product_title"
#             )


#             record["specifications"] = parsed.get(
#                 "specifications",
#                 [],
#             )

#             record["specification_notices"] = parsed.get(
#                 "specification_notices",
#                 [],
#             )

#             record["specification_map"] = parsed.get(
#                 "specification_map",
#                 {},
#             )

#             record["oem_numbers"] = parsed.get(
#                 "oem_numbers",
#                 [],
#             )

#             record["oem_numbers_text"] = parsed.get(
#                 "oem_numbers_text",
#                 "",
#             )



#             record["status"] = "success"


#             print(
#                 f"Page title: "
#                 f"{record['page_title']}"
#             )

#             print(
#                 f"Product title: "
#                 f"{record['product_title']}"
#             )

#             print(
#                 f"Jumlah spesifikasi: "
#                 f"{len(record['specifications'])}"
#             )

#             for specification in (
#                 record["specifications"][:5]
#             ):
#                 print(
#                     "  - "
#                     f"{specification['name_original']}: "
#                     f"{specification['value_original']}"
#                 )


#             print(
#                 f"Jumlah OEM: "
#                 f"{len(record['oem_numbers'])}"
#             )

#             if record["oem_numbers_text"]:
#                 print(
#                     f"OEM: "
#                     f"{record['oem_numbers_text']}"
#                 )
#             else:
#                 print("OEM: tidak ditemukan")


#             print(
#                 f"Jumlah notice spesifikasi: "
#                 f"{len(record['specification_notices'])}"
#             )

#             for notice in record["specification_notices"]:
#                 print(
#                     "  ℹ️ "
#                     f"{notice['name_original']}: "
#                     f"{notice['value_original']}"
#                 )


#         except Exception as exc:
#             record["status"] = "failed"
#             record["error"] = str(exc)

#             try:
#                 record["final_url"] = (
#                     browser.current_url
#                 )
#             except Exception:
#                 pass

#             print(
#                 f"❌ Gagal membaca produk "
#                 f"{product_index}: {exc}"
#             )

#         page_records.append(record)

#         # Simpan setelah setiap produk.
#         # Jika script berhenti, hasil sebelumnya tidak hilang.
#         save_page_detail_results(
#             page_number=page_number,
#             records=page_records,
#         )

#         time.sleep(delay_seconds)

#     output_path = save_page_detail_results(
#         page_number=page_number,
#         records=page_records,
#     )

#     successful_count = sum(
#         1
#         for record in page_records
#         if record["status"] == "success"
#     )

#     failed_count = (
#         len(page_records) - successful_count
#     )

#     print()
#     print(
#         f"Selesai membaca listing page "
#         f"{page_number}"
#     )
#     print(
#         f"Berhasil: {successful_count}"
#     )
#     print(
#         f"Gagal/challenge: {failed_count}"
#     )
#     print(
#         f"Hasil disimpan: {output_path}"
#     )

#     return page_records




from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


# ============================================================
# SELECTORS
# ============================================================

PRODUCT_TITLE_SELECTOR = (
    "h1.product-block__title"
)

PRODUCT_SUBTITLE_SELECTOR = (
    "h1.product-block__title "
    ".product-block__seo-subtitle-text"
)

SPECIFICATION_ITEM_SELECTOR = (
    "div.product-description__info "
    "ul.product-description__list "
    "li.product-description__item"
)

SPECIFICATION_TITLE_SELECTOR = (
    ".product-description__item-title"
)

SPECIFICATION_VALUE_SELECTOR = (
    ".product-description__item-value"
)

SPECIFICATION_MORE_BUTTON_SELECTOR = (
    "div.product-description__btn "
    "[data-show-more-btn]"
)

OEM_LINK_SELECTOR = (
    "div.product-oem "
    "ul.product-oem__list "
    "a.product-oem__link"
)

COMPATIBILITY_ROW_SELECTOR = (
    "div.text-info-box[data-show-more] "
    "table.summary-table tbody tr"
)

COMPATIBILITY_MORE_BUTTON_SELECTOR = (
    "div.text-info-box[data-show-more] "
    ".text-info-box__btn "
    "[data-show-more-btn]"
)


# ============================================================
# CONSTANTS
# ============================================================

INVALID_VALUES = {
    "",
    "-",
    "—",
    "n/a",
    "none",
    "null",
}

NOTICE_MARKERS = (
    "diese eigenschaft variiert je nach fahrzeugmodell",
    "variiert je nach fahrzeugmodell",
)

CLOUDFLARE_MARKERS = (
    "nur einen moment",
    "just a moment",
    "challenges.cloudflare.com",
    "cf-turnstile",
    "cf-chl-",
    "bestätigen sie, dass sie ein mensch sind",
)


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean_text(
    value: str | None,
) -> str:
    """
    Membersihkan whitespace tanpa mengubah
    isi data teknis.
    """

    if not value:
        return ""

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def is_cloudflare_page(
    html: str,
) -> bool:
    html_lower = html.casefold()

    return any(
        marker in html_lower
        for marker in CLOUDFLARE_MARKERS
    )


# ============================================================
# WAIT FOR PRODUCT PAGE
# ============================================================

def wait_for_product_detail(
    browser,
    timeout_seconds: int = 30,
) -> None:
    """
    Menunggu title dan daftar specification awal muncul.
    """

    WebDriverWait(
        browser,
        timeout_seconds,
    ).until(
        lambda driver: (
            len(
                driver.find_elements(
                    By.CSS_SELECTOR,
                    PRODUCT_TITLE_SELECTOR,
                )
            ) > 0
            and len(
                driver.find_elements(
                    By.CSS_SELECTOR,
                    SPECIFICATION_ITEM_SELECTOR,
                )
            ) > 0
        )
    )


def get_specification_snapshot(
    browser,
) -> tuple[str, ...]:
    """
    Mengambil snapshot teks specification
    yang sedang tampil.
    """

    elements = browser.find_elements(
        By.CSS_SELECTOR,
        SPECIFICATION_ITEM_SELECTOR,
    )

    return tuple(
        clean_text(element.text)
        for element in elements
        if clean_text(element.text)
    )


def wait_for_specifications_stable(
    browser,
    initial_delay_seconds: float = 3.0,
    timeout_seconds: int = 20,
    required_stable_checks: int = 2,
) -> None:
    """
    Menunggu DOM specification stabil sebelum
    tombol Mehr diklik.
    """

    print(
        f"Menunggu {initial_delay_seconds} detik "
        "agar AJAX selesai..."
    )

    time.sleep(initial_delay_seconds)

    deadline = time.time() + timeout_seconds

    previous_snapshot: tuple[str, ...] | None = None
    stable_checks = 0

    while time.time() < deadline:
        current_snapshot = (
            get_specification_snapshot(browser)
        )

        if (
            current_snapshot
            and current_snapshot == previous_snapshot
        ):
            stable_checks += 1
        else:
            previous_snapshot = current_snapshot
            stable_checks = 0

        print(
            "Specification items:",
            len(current_snapshot),
            "| stable checks:",
            stable_checks,
        )

        if stable_checks >= required_stable_checks:
            print(
                "✅ Specification DOM sudah stabil."
            )
            return

        time.sleep(1)

    print(
        "⚠️ Timeout menunggu specification stabil. "
        "Data terakhir tetap digunakan."
    )


def wait_for_all_specifications_loaded(
    browser,
    timeout_seconds: int = 20,
    stable_checks_required: int = 3,
) -> int:
    """
    Menunggu seluruh specification stabil setelah
    tombol Mehr diklik.
    """

    deadline = time.time() + timeout_seconds

    previous_snapshot: tuple[str, ...] | None = None
    stable_checks = 0

    while time.time() < deadline:
        current_snapshot = (
            get_specification_snapshot(browser)
        )

        if (
            current_snapshot
            and current_snapshot == previous_snapshot
        ):
            stable_checks += 1
        else:
            previous_snapshot = current_snapshot
            stable_checks = 0

        print(
            "Specification terlihat:",
            len(current_snapshot),
            "| stable checks:",
            stable_checks,
        )

        if stable_checks >= stable_checks_required:
            print(
                "✅ Semua specification selesai dimuat."
            )
            return len(current_snapshot)

        time.sleep(1)

    final_snapshot = (
        get_specification_snapshot(browser)
    )

    print(
        "⚠️ Timeout menunggu specification, "
        f"menggunakan {len(final_snapshot)} item."
    )

    return len(final_snapshot)


# ============================================================
# PRODUCT TITLE
# ============================================================

def get_direct_text(
    browser,
    element,
) -> str:
    """
    Mengambil text node langsung dari h1 sehingga
    subtitle tidak tercampur dengan product title.
    """

    value = browser.execute_script(
        """
        return Array.from(arguments[0].childNodes)
            .filter(
                node =>
                    node.nodeType === Node.TEXT_NODE
            )
            .map(node => node.textContent)
            .join(" ");
        """,
        element,
    )

    return clean_text(value)


def read_product_title(
    browser,
) -> tuple[str | None, str | None]:
    """
    Mengembalikan:
    - product title
    - product subtitle
    """

    title_elements = browser.find_elements(
        By.CSS_SELECTOR,
        PRODUCT_TITLE_SELECTOR,
    )

    if not title_elements:
        return None, None

    title_element = title_elements[0]

    product_title = get_direct_text(
        browser,
        title_element,
    )

    subtitle_elements = browser.find_elements(
        By.CSS_SELECTOR,
        PRODUCT_SUBTITLE_SELECTOR,
    )

    product_subtitle = None

    if subtitle_elements:
        product_subtitle = clean_text(
            subtitle_elements[0].text
        )

    return (
        product_title or None,
        product_subtitle or None,
    )


# ============================================================
# SPECIFICATIONS
# ============================================================

def get_visible_specification_count(
    browser,
) -> int:
    elements = browser.find_elements(
        By.CSS_SELECTOR,
        SPECIFICATION_ITEM_SELECTOR,
    )

    return sum(
        1
        for element in elements
        if (
            element.is_displayed()
            and clean_text(element.text)
        )
    )


def expand_product_specifications(
    browser,
    timeout_seconds: int = 15,
) -> bool:
    """
    Klik tombol Mehr pada product specifications.
    """

    all_items = browser.find_elements(
        By.CSS_SELECTOR,
        SPECIFICATION_ITEM_SELECTOR,
    )

    total_dom_count = len(all_items)

    visible_count_before = (
        get_visible_specification_count(browser)
    )

    print(
        f"Specification DOM total: "
        f"{total_dom_count}"
    )

    print(
        "Specification terlihat sebelum expand: "
        f"{visible_count_before}"
    )

    if (
        total_dom_count > 0
        and visible_count_before >= total_dom_count
    ):
        print(
            "ℹ️ Semua specification sudah terlihat."
        )
        return False

    try:
        button = WebDriverWait(
            browser,
            timeout_seconds,
        ).until(
            lambda driver: next(
                (
                    element
                    for element
                    in driver.find_elements(
                        By.CSS_SELECTOR,
                        SPECIFICATION_MORE_BUTTON_SELECTOR,
                    )
                    if element.is_displayed()
                ),
                None,
            )
        )

    except Exception:
        print(
            "ℹ️ Tombol Mehr specification "
            "tidak ditemukan."
        )
        return False

    browser.execute_script(
        """
        arguments[0].scrollIntoView({
            block: "center",
            inline: "nearest"
        });
        """,
        button,
    )

    time.sleep(1)

    try:
        button.click()

    except Exception:
        browser.execute_script(
            "arguments[0].click();",
            button,
        )

    try:
        WebDriverWait(
            browser,
            timeout_seconds,
        ).until(
            lambda driver: (
                get_visible_specification_count(
                    driver
                )
                > visible_count_before
            )
        )

    except Exception:
        print(
            "⚠️ Specification terlihat tidak "
            "bertambah setelah klik Mehr."
        )

    time.sleep(2)

    visible_count_after = (
        get_visible_specification_count(browser)
    )

    print(
        "Specification terlihat setelah expand: "
        f"{visible_count_after}"
    )

    return (
        visible_count_after
        > visible_count_before
    )


def is_notice_value(
    value_element,
    value_text: str,
) -> bool:
    """
    Mendeteksi value yang merupakan notice
    pemilihan kendaraan.
    """

    value_lower = clean_text(
        value_text
    ).casefold()

    if any(
        marker in value_lower
        for marker in NOTICE_MARKERS
    ):
        return True

    popup_elements = value_element.find_elements(
        By.CSS_SELECTOR,
        (
            '[data-popup-show-ajax='
            '"data-popup-search-car"],'
            '[data-ajax-selector-popup-type="car"]'
        ),
    )

    return bool(popup_elements)


def read_specifications(
    browser,
    include_raw_html: bool = True,
) -> list[dict[str, Any]]:
    """
    Membaca specification langsung dari live DOM.
    """

    item_elements = browser.find_elements(
        By.CSS_SELECTOR,
        SPECIFICATION_ITEM_SELECTOR,
    )

    specifications: list[dict[str, Any]] = []

    for position, item_element in enumerate(
        item_elements,
        start=1,
    ):
        title_elements = item_element.find_elements(
            By.CSS_SELECTOR,
            SPECIFICATION_TITLE_SELECTOR,
        )

        value_elements = item_element.find_elements(
            By.CSS_SELECTOR,
            SPECIFICATION_VALUE_SELECTOR,
        )

        if not title_elements or not value_elements:
            continue

        title_element = title_elements[0]
        value_element = value_elements[0]

        name_original = clean_text(
            title_element.text
        ).rstrip(":").strip()

        value_original = clean_text(
            value_element.text
        )

        if not name_original:
            continue

        if not value_original:
            continue

        if (
            value_original.casefold()
            in INVALID_VALUES
        ):
            continue

        specification_type = (
            "notice"
            if is_notice_value(
                value_element=value_element,
                value_text=value_original,
            )
            else "specification"
        )

        specification: dict[str, Any] = {
            "position": position,
            "name_original": name_original,
            "value_original": value_original,
            "type": specification_type,
            "name_ar": None,
            "value_ar": None,
        }

        if include_raw_html:
            specification["raw_html"] = (
                item_element.get_attribute(
                    "outerHTML"
                )
            )

        specifications.append(
            specification
        )

    return specifications


def specifications_to_map(
    specifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Mengubah seluruh specification dan notice
    menjadi dictionary.
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

        existing = result[name]

        if existing == value:
            continue

        if isinstance(existing, list):
            if value not in existing:
                existing.append(value)

        else:
            result[name] = [
                existing,
                value,
            ]

    return result


# ============================================================
# OEM NUMBERS
# ============================================================

def read_oem_numbers(
    browser,
) -> list[dict[str, str | None]]:
    """
    Membaca seluruh OE/OEM number dari live DOM.
    """

    elements = browser.find_elements(
        By.CSS_SELECTOR,
        OEM_LINK_SELECTOR,
    )

    results: list[dict[str, str | None]] = []
    seen: set[tuple[str, str]] = set()

    for element in elements:
        display_text = clean_text(
            element.text
        )

        source_url = element.get_attribute(
            "href"
        )

        if not display_text:
            continue

        match = re.match(
            r"^OE\s+(.+?)\s+[—–-]\s+(.+)$",
            display_text,
            flags=re.IGNORECASE,
        )

        if match:
            oe_number = (
                match.group(1).strip()
            )

            manufacturer = (
                match.group(2).strip()
            )

        else:
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

            oe_number = parts[0].strip()

            manufacturer = (
                parts[1].strip()
                if len(parts) > 1
                else ""
            )

        if not oe_number:
            continue

        dedup_key = (
            oe_number,
            manufacturer,
        )

        if dedup_key in seen:
            continue

        seen.add(dedup_key)

        normalized_display = (
            f"OE {oe_number}"
        )

        if manufacturer:
            normalized_display += (
                f" — {manufacturer}"
            )

        results.append(
            {
                "oe_number": oe_number,
                "manufacturer": (
                    manufacturer or None
                ),
                "display_text": (
                    normalized_display
                ),
                "source_url": source_url,
            }
        )

    return results


# ============================================================
# COMPATIBILITY
# ============================================================

def get_visible_compatibility_row_count(
    browser,
) -> int:
    rows = browser.find_elements(
        By.CSS_SELECTOR,
        COMPATIBILITY_ROW_SELECTOR,
    )

    return sum(
        1
        for row in rows
        if (
            row.is_displayed()
            and clean_text(row.text)
        )
    )


def expand_compatibility_table(
    browser,
    timeout_seconds: int = 15,
) -> bool:
    """
    Klik tombol Mehr pada tabel compatibility.
    """

    rows = browser.find_elements(
        By.CSS_SELECTOR,
        COMPATIBILITY_ROW_SELECTOR,
    )

    total_row_count = len(rows)

    visible_count_before = (
        get_visible_compatibility_row_count(
            browser
        )
    )

    print(
        f"Compatibility rows total DOM: "
        f"{total_row_count}"
    )

    print(
        "Compatibility terlihat sebelum expand: "
        f"{visible_count_before}"
    )

    if (
        total_row_count > 0
        and visible_count_before >= total_row_count
    ):
        print(
            "ℹ️ Semua compatibility sudah terlihat."
        )
        return False

    try:
        button = WebDriverWait(
            browser,
            timeout_seconds,
        ).until(
            lambda driver: next(
                (
                    element
                    for element
                    in driver.find_elements(
                        By.CSS_SELECTOR,
                        COMPATIBILITY_MORE_BUTTON_SELECTOR,
                    )
                    if element.is_displayed()
                ),
                None,
            )
        )

    except Exception:
        print(
            "ℹ️ Tombol Mehr compatibility "
            "tidak ditemukan."
        )
        return False

    browser.execute_script(
        """
        arguments[0].scrollIntoView({
            block: "center",
            inline: "nearest"
        });
        """,
        button,
    )

    time.sleep(1)

    try:
        button.click()

    except Exception:
        browser.execute_script(
            "arguments[0].click();",
            button,
        )

    try:
        WebDriverWait(
            browser,
            timeout_seconds,
        ).until(
            lambda driver: (
                get_visible_compatibility_row_count(
                    driver
                )
                > visible_count_before
            )
        )

    except Exception:
        print(
            "⚠️ Compatibility row tidak bertambah "
            "setelah klik Mehr."
        )

    time.sleep(2)

    visible_count_after = (
        get_visible_compatibility_row_count(
            browser
        )
    )

    print(
        "Compatibility terlihat setelah expand: "
        f"{visible_count_after}"
    )

    return (
        visible_count_after
        > visible_count_before
    )


def read_compatibility_table(
    browser,
) -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
]:
    """
    Membaca tabel compatibility langsung dari DOM.
    """

    rows = browser.find_elements(
        By.CSS_SELECTOR,
        COMPATIBILITY_ROW_SELECTOR,
    )

    compatibility_rows: list[
        dict[str, Any]
    ] = []

    compatibility_map: dict[
        str,
        Any,
    ] = {}

    for position, row in enumerate(
        rows,
        start=1,
    ):
        cells = row.find_elements(
            By.CSS_SELECTOR,
            "td",
        )

        if len(cells) < 2:
            continue

        name_original = clean_text(
            cells[0].text
        )

        value_original = clean_text(
            cells[1].text
        )

        if not name_original:
            continue

        if not value_original:
            continue

        compatibility_rows.append(
            {
                "position": position,
                "name_original": (
                    name_original
                ),
                "value_original": (
                    value_original
                ),
            }
        )

        if name_original not in compatibility_map:
            compatibility_map[
                name_original
            ] = value_original

        else:
            existing = compatibility_map[
                name_original
            ]

            if existing == value_original:
                continue

            if isinstance(existing, list):
                if value_original not in existing:
                    existing.append(
                        value_original
                    )

            else:
                compatibility_map[
                    name_original
                ] = [
                    existing,
                    value_original,
                ]

    return (
        compatibility_rows,
        compatibility_map,
    )


# ============================================================
# READ ONE PRODUCT DETAIL
# ============================================================

def read_product_detail(
    browser,
    product_url: str,
) -> dict[str, Any]:
    """
    Membuka dan membaca satu product detail.
    """

    browser.get(product_url)

    wait_for_product_detail(
        browser=browser,
        timeout_seconds=30,
    )

    html = browser.page_source

    if is_cloudflare_page(html):
        raise RuntimeError(
            "Cloudflare challenge ditemukan "
            "pada halaman produk."
        )

    wait_for_specifications_stable(
        browser=browser,
        initial_delay_seconds=3,
        timeout_seconds=20,
        required_stable_checks=2,
    )

    expand_product_specifications(
        browser=browser,
        timeout_seconds=15,
    )

    final_specification_count = (
        wait_for_all_specifications_loaded(
            browser=browser,
            timeout_seconds=20,
            stable_checks_required=3,
        )
    )

    print(
        "Total specification siap dibaca: "
        f"{final_specification_count}"
    )

    product_title, product_subtitle = (
        read_product_title(browser)
    )

    specifications = read_specifications(
        browser=browser,
        include_raw_html=True,
    )

    valid_specifications = [
        item
        for item in specifications
        if item.get("type") == "specification"
    ]

    specification_notices = [
        item
        for item in specifications
        if item.get("type") == "notice"
    ]

    specification_map = (
        specifications_to_map(
            specifications
        )
    )

    expand_compatibility_table(
        browser=browser,
        timeout_seconds=15,
    )

    compatibility_rows, compatibility_map = (
        read_compatibility_table(
            browser
        )
    )

    oem_numbers = read_oem_numbers(
        browser
    )

    oem_numbers_text = ", ".join(
        str(item["display_text"])
        for item in oem_numbers
        if item.get("display_text")
    )

    return {
        "final_url": browser.current_url,
        "page_title": browser.title,
        "browser_title": browser.title,
        "product_title": product_title,
        "product_subtitle": product_subtitle,

        "specifications": valid_specifications,
        "specification_notices": (
            specification_notices
        ),
        "specification_map": specification_map,

        "compatibility_rows": compatibility_rows,
        "compatibility_map": compatibility_map,

        "oem_numbers": oem_numbers,
        "oem_numbers_text": oem_numbers_text,
        "ОЕ-Nummern": oem_numbers_text,

        "status": "success",
        "error": None,
    }


# ============================================================
# SAVE RESULTS
# ============================================================

def save_page_detail_results(
    page_number: int,
    records: list[dict[str, Any]],
) -> Path:
    output_path = Path(
        "data/processed/product_details/"
        f"page_{page_number}.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            records,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path


# ============================================================
# READ ALL PRODUCTS FROM ONE LISTING PAGE
# ============================================================

def collect_product_titles_for_page(
    browser,
    product_urls: list[str],
    page_number: int,
    delay_seconds: float = 3.0,
) -> list[dict[str, Any]]:
    """
    Membaca semua product detail dari satu listing page.

    Nama fungsi dipertahankan agar main.py
    tidak perlu diubah.
    """

    page_records: list[dict[str, Any]] = []

    print()
    print(
        f"Mulai membaca detail produk "
        f"dari listing page {page_number}"
    )

    print(
        f"Jumlah produk yang akan dibuka: "
        f"{len(product_urls)}"
    )

    for product_index, product_url in enumerate(
        product_urls,
        start=1,
    ):
        print()
        print("=" * 70)
        print(
            f"[Page {page_number}] "
            f"Produk {product_index}/"
            f"{len(product_urls)}"
        )
        print(f"URL: {product_url}")
        print("=" * 70)

        record: dict[str, Any] = {
            "listing_page": page_number,
            "product_index": product_index,
            "requested_url": product_url,
            "final_url": None,
            "page_title": None,
            "browser_title": None,
            "product_title": None,
            "product_subtitle": None,

            "specifications": [],
            "specification_notices": [],
            "specification_map": {},

            "compatibility_rows": [],
            "compatibility_map": {},

            "oem_numbers": [],
            "oem_numbers_text": "",
            "ОЕ-Nummern": "",

            "status": "pending",
            "error": None,
        }

        try:
            product_detail = read_product_detail(
                browser=browser,
                product_url=product_url,
            )

            record.update(
                product_detail
            )

            print(
                f"Page title: "
                f"{record['page_title']}"
            )

            print(
                f"Product title: "
                f"{record['product_title']}"
            )

            print(
                f"Product subtitle: "
                f"{record['product_subtitle']}"
            )

            print(
                f"Jumlah spesifikasi: "
                f"{len(record['specifications'])}"
            )

            for specification in (
                record["specifications"][:5]
            ):
                print(
                    "  - "
                    f"{specification.get('name_original')}: "
                    f"{specification.get('value_original')}"
                )

            print(
                "Jumlah notice specification: "
                f"{len(record['specification_notices'])}"
            )

            for notice in (
                record["specification_notices"]
            ):
                print(
                    "  ℹ️ "
                    f"{notice.get('name_original')}: "
                    f"{notice.get('value_original')}"
                )

            print(
                "Jumlah compatibility rows: "
                f"{len(record['compatibility_rows'])}"
            )

            print(
                f"Jumlah OEM: "
                f"{len(record['oem_numbers'])}"
            )

            print(
                f"ОЕ-Nummern: "
                f"{record['ОЕ-Nummern']}"
            )

        except Exception as exc:
            record["status"] = "failed"
            record["error"] = str(exc)

            try:
                record["final_url"] = (
                    browser.current_url
                )

                record["page_title"] = (
                    browser.title
                )

                record["browser_title"] = (
                    browser.title
                )

            except Exception:
                pass

            print(
                f"❌ Gagal membaca produk "
                f"{product_index}: {exc}"
            )

        page_records.append(record)

        save_page_detail_results(
            page_number=page_number,
            records=page_records,
        )

        if product_index < len(product_urls):
            time.sleep(delay_seconds)

    output_path = save_page_detail_results(
        page_number=page_number,
        records=page_records,
    )

    successful_count = sum(
        1
        for record in page_records
        if record["status"] == "success"
    )

    failed_count = (
        len(page_records)
        - successful_count
    )

    print()
    print("=" * 70)
    print(
        f"Selesai membaca listing page "
        f"{page_number}"
    )
    print(f"Berhasil: {successful_count}")
    print(f"Gagal: {failed_count}")
    print(f"Hasil: {output_path}")
    print("=" * 70)

    return page_records