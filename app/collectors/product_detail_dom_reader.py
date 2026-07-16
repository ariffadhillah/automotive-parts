from __future__ import annotations

import io
from urllib.parse import urlparse
from pathlib import Path 
import requests
from PIL import Image

import re
import time
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait






PRODUCT_TITLE_SELECTOR = "h1.product-block__title"

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

SHOW_MORE_BUTTON_SELECTOR = (
    "div.product-description__btn "
    "[data-show-more-btn]"
)

OEM_LINK_SELECTOR = (
    "div.product-oem "
    "ul.product-oem__list "
    "a.product-oem__link"
)

COMPATIBILITY_BOX_SELECTOR = (
    "div.text-info-box[data-show-more]"
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

PRICE_SELECTOR = (
    "div.product-block__price-new "
    "div.product-block__price-new-wrap"
)

MAIN_GALLERY_IMAGE_SELECTOR = (
    "div.product-gallery__big-image"
)


MAIN_GALLERY_IMAGE_SELECTOR = (
    "div.product-gallery__big-image"
)

GALLERY_IMAGE_SELECTOR = (
    "ul.product-gallery__image-list "
    "li[data-gallery-small-image] img"
)


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

def wait_for_all_specifications_loaded(
    browser,
    timeout_seconds: int = 20,
    stable_checks_required: int = 3,
) -> int:
    """
    Menunggu isi specification yang terlihat stabil
    setelah tombol Mehr diklik.
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
            and current_snapshot
            == previous_snapshot
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
                "✅ Semua specification sudah "
                "selesai dimuat."
            )
            return len(current_snapshot)

        time.sleep(1)

    final_snapshot = (
        get_specification_snapshot(browser)
    )

    print(
        "⚠️ Timeout menunggu specification, "
        f"menggunakan {len(final_snapshot)} "
        "item terakhir."
    )

    return len(final_snapshot)


def clean_text(value: str | None) -> str:
    if not value:
        return ""

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def wait_for_product_page(
    browser,
    timeout_seconds: int = 30,
) -> None:
    """
    Menunggu title dan specification tampil.
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
    Membuat snapshot teks specification yang
    sedang tampil di browser.
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



def get_visible_specification_count(
    browser,
) -> int:
    """
    Menghitung specification item yang benar-benar
    terlihat dan memiliki teks.
    """

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


def wait_for_specifications_stable(
    browser,
    initial_delay_seconds: float = 5.0,
    timeout_seconds: int = 30,
    required_stable_checks: int = 4,
) -> None:
    """
    Menunggu sesudah JavaScript/AJAX selesai mengubah
    specification.

    initial_delay penting agar kita tidak langsung membaca
    HTML awal sebelum AUTODOC selesai memperbarui DOM.
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
        current_snapshot = get_specification_snapshot(
            browser
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
            print("✅ Specification DOM sudah stabil.")
            return

        time.sleep(1)

    print(
        "⚠️ Timeout saat menunggu DOM stabil. "
        "Data terakhir tetap akan dibaca."
    )


def get_direct_text(browser, element) -> str:
    """
    Mengambil hanya text node langsung dari elemen.

    Berguna agar product title tidak tercampur
    dengan subtitle di dalam nested span.
    """

    value = browser.execute_script(
        """
        return Array.from(arguments[0].childNodes)
            .filter(node => node.nodeType === Node.TEXT_NODE)
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
    - product_title
    - product_subtitle
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


def is_notice_value(
    value_element,
    value_text: str,
) -> bool:
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
            '[data-popup-show-ajax="data-popup-search-car"],'
            '[data-ajax-selector-popup-type="car"]'
        ),
    )

    return bool(popup_elements)


def expand_product_specifications(
    browser,
    timeout_seconds: int = 15,
) -> bool:
    """
    Klik tombol 'Mehr' jika masih ada specification
    yang tersembunyi.
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
        f"Specification DOM total: {total_dom_count}"
    )
    print(
        "Specification terlihat sebelum expand: "
        f"{visible_count_before}"
    )

    # Kalau semua item sudah terlihat, tidak perlu klik.
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
                    for element in driver.find_elements(
                        By.CSS_SELECTOR,
                        SHOW_MORE_BUTTON_SELECTOR,
                    )
                    if element.is_displayed()
                ),
                None,
            )
        )

    except Exception:
        print(
            "ℹ️ Tombol 'Mehr' tidak ditemukan "
            "atau tidak terlihat."
        )
        return False

    print(
        "Tombol expand ditemukan:",
        {
            "data_more": clean_text(
                button.get_attribute("data-more")
            ),
            "data_less": clean_text(
                button.get_attribute("data-less")
            ),
            "text": clean_text(button.text),
        },
    )

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
            "⚠️ Jumlah item terlihat tidak bertambah "
            "setelah tombol Mehr diklik."
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


def read_specifications(
    browser,
    include_raw_html: bool = True,
) -> list[dict[str, Any]]:
    """
    Membaca specification langsung dari live DOM Selenium.

    Tidak menggunakan browser.page_source dan
    tidak menggunakan BeautifulSoup.
    """

    specification_elements = browser.find_elements(
        By.CSS_SELECTOR,
        SPECIFICATION_ITEM_SELECTOR,
    )

    specifications: list[dict[str, Any]] = []

    for position, item_element in enumerate(
        specification_elements,
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

    Jika nama yang sama memiliki beberapa nilai berbeda,
    nilainya disimpan sebagai list.
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



def read_oem_numbers(
    browser,
) -> list[dict[str, str | None]]:
    oem_elements = browser.find_elements(
        By.CSS_SELECTOR,
        OEM_LINK_SELECTOR,
    )

    results: list[dict[str, str | None]] = []
    seen: set[tuple[str, str]] = set()

    for element in oem_elements:
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
            oe_number = match.group(1).strip()
            manufacturer = match.group(2).strip()
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
    Klik tombol Mehr pada tabel compatibility
    agar semua baris terlihat.
    """

    rows = browser.find_elements(
        By.CSS_SELECTOR,
        COMPATIBILITY_ROW_SELECTOR,
    )

    total_row_count = len(rows)

    visible_count_before = (
        get_visible_compatibility_row_count(browser)
    )

    print(
        f"Compatibility rows total DOM: "
        f"{total_row_count}"
    )

    print(
        "Compatibility rows terlihat sebelum expand: "
        f"{visible_count_before}"
    )

    if (
        total_row_count > 0
        and visible_count_before >= total_row_count
    ):
        print(
            "ℹ️ Semua compatibility rows sudah terlihat."
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
                    for element in driver.find_elements(
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
            "tidak ditemukan atau tidak terlihat."
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
            "⚠️ Jumlah compatibility row terlihat "
            "tidak bertambah setelah klik Mehr."
        )

    time.sleep(2)

    visible_count_after = (
        get_visible_compatibility_row_count(browser)
    )

    print(
        "Compatibility rows terlihat setelah expand: "
        f"{visible_count_after}"
    )

    return (
        visible_count_after
        > visible_count_before
    )


def read_compatibility_table(
    browser,
) -> tuple[
    list[dict[str, str]],
    dict[str, str],
]:
    """
    Membaca seluruh tabel compatibility.

    Mengembalikan:
    - list of rows
    - map key/value
    """

    rows = browser.find_elements(
        By.CSS_SELECTOR,
        COMPATIBILITY_ROW_SELECTOR,
    )

    compatibility_rows: list[dict[str, str]] = []
    compatibility_map: dict[str, str] = {}

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

        if not name_original or not value_original:
            continue

        compatibility_rows.append(
            {
                "position": position,
                "name_original": name_original,
                "value_original": value_original,
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

            if existing != value_original:
                compatibility_map[
                    name_original
                ] = f"{existing}, {value_original}"

    return (
        compatibility_rows,
        compatibility_map,
    )


def read_product_price(
    browser,
) -> dict[str, Any]:
    elements = browser.find_elements(
        By.CSS_SELECTOR,
        PRICE_SELECTOR,
    )

    if not elements:
        return {
            "price_display": None,
            "price_amount": None,
            "price_currency": None,
        }

    raw_text = clean_text(
        elements[0].text
    )

    normalized_text = re.sub(
        r"\s*,\s*",
        ",",
        raw_text,
    )

    match = re.search(
        r"([\d.]+),(\d{2})\s*€",
        normalized_text,
    )

    if not match:
        return {
            "price_display": normalized_text or None,
            "price_amount": None,
            "price_currency": (
                "EUR"
                if "€" in normalized_text
                else None
            ),
        }

    integer_part = match.group(1)
    decimal_part = match.group(2)

    amount_text = (
        integer_part.replace(".", "")
        + "."
        + decimal_part
    )

    return {
        "price_display": (
            f"{integer_part},{decimal_part} €"
        ),
        "price_amount": float(amount_text),
        "price_currency": "EUR",
    }


def parse_srcset(
    srcset: str | None,
) -> list[tuple[str, float]]:
    if not srcset:
        return []

    results: list[tuple[str, float]] = []

    for item in srcset.split(","):
        item = clean_text(item)

        if not item:
            continue

        parts = item.rsplit(" ", maxsplit=1)

        image_url = parts[0].strip()
        weight = 1.0

        if len(parts) == 2:
            descriptor = parts[1].strip()

            try:
                if descriptor.endswith("x"):
                    weight = float(
                        descriptor[:-1]
                    )
                elif descriptor.endswith("w"):
                    weight = float(
                        descriptor[:-1]
                    )
            except ValueError:
                pass

        results.append(
            (image_url, weight)
        )

    return results


def get_largest_image_url(
    image_element,
) -> str | None:
    candidates: list[tuple[str, float]] = []

    for attribute in (
        "srcset",
        "data-srcset",
    ):
        candidates.extend(
            parse_srcset(
                image_element.get_attribute(
                    attribute
                )
            )
        )

    src = image_element.get_attribute("src")

    if src:
        candidates.append((src, 1.0))

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda value: value[1],
    )[0]


def read_product_image_urls(
    browser,
) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()

    def add_url(url: str | None) -> None:
        if not url:
            return

        url = url.strip()

        if not url:
            return

        lowered = url.casefold()

        if "/brands/" in lowered:
            return

        if lowered.endswith(".svg"):
            return

        if "360-icon" in lowered:
            return

        if url in seen:
            return

        seen.add(url)
        urls.append(url)

    main_images = browser.find_elements(
        By.CSS_SELECTOR,
        MAIN_GALLERY_IMAGE_SELECTOR,
    )

    for container in main_images:
        # Prioritas tertinggi
        add_url(
            container.get_attribute(
                "data-zoom"
            )
        )

        nested_images = container.find_elements(
            By.CSS_SELECTOR,
            "img",
        )

        for image in nested_images:
            add_url(
                get_largest_image_url(image)
            )

    gallery_images = browser.find_elements(
        By.CSS_SELECTOR,
        GALLERY_IMAGE_SELECTOR,
    )

    for image in gallery_images:
        add_url(
            get_largest_image_url(image)
        )

    return urls


def create_image_session(
    browser,
    product_url: str,
) -> requests.Session:
    session = requests.Session()

    user_agent = browser.execute_script(
        "return navigator.userAgent;"
    )

    session.headers.update(
        {
            "User-Agent": user_agent,
            "Accept": (
                "image/avif,image/webp,"
                "image/apng,image/*,*/*;q=0.8"
            ),
            "Referer": product_url,
        }
    )

    for cookie in browser.get_cookies():
        name = cookie.get("name")
        value = cookie.get("value")

        if not name or value is None:
            continue

        session.cookies.set(
            name=name,
            value=value,
            domain=cookie.get("domain"),
            path=cookie.get("path", "/"),
        )

    return session


def save_as_webp(
    image_bytes: bytes,
    output_path: Path,
    quality: int = 88,
) -> tuple[int, int]:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with Image.open(
        io.BytesIO(image_bytes)
    ) as image:
        if image.mode in {"RGBA", "LA"}:
            converted = image.convert("RGBA")
        else:
            converted = image.convert("RGB")

        width, height = converted.size

        # Tidak meneruskan EXIF/metadata sumber.
        converted.save(
            output_path,
            format="WEBP",
            quality=quality,
            method=6,
        )

    return width, height


def download_product_images(
    browser,
    product_url: str,
    image_urls: list[str],
) -> list[dict[str, Any]]:
    product_id = (
        urlparse(product_url)
        .path
        .rstrip("/")
        .split("/")[-1]
    )

    output_directory = (
        Path("data/samples/autodoc_client_sample/images")
        / product_id
    )

    session = create_image_session(
        browser=browser,
        product_url=product_url,
    )

    results: list[dict[str, Any]] = []

    for position, image_url in enumerate(
        image_urls,
        start=1,
    ):
        output_path = (
            output_directory
            / f"{product_id}_{position:02d}.webp"
        )

        record: dict[str, Any] = {
            "position": position,
            "source_url": image_url,
            "local_path": str(output_path),
            "format": "webp",
            "width": None,
            "height": None,
            "metadata_removed": True,
            "status": "pending",
            "error": None,
        }

        try:
            response = session.get(
                image_url,
                timeout=60,
            )
            response.raise_for_status()

            width, height = save_as_webp(
                image_bytes=response.content,
                output_path=output_path,
            )

            record["width"] = width
            record["height"] = height
            record["status"] = "success"

            print(
                f"Image {position}: "
                f"{width}x{height} → {output_path}"
            )

        except Exception as exc:
            record["status"] = "failed"
            record["error"] = str(exc)

            print(
                f"Image {position} gagal: {exc}"
            )

        results.append(record)

    return results





def create_download_session(
    browser,
    referer_url: str,
) -> requests.Session:
    session = requests.Session()

    user_agent = browser.execute_script(
        "return navigator.userAgent;"
    )

    session.headers.update(
        {
            "User-Agent": user_agent,
            "Accept": (
                "image/avif,image/webp,"
                "image/apng,image/*,*/*;q=0.8"
            ),
            "Accept-Language": (
                "de-DE,de;q=0.9,en;q=0.8"
            ),
            "Referer": referer_url,
        }
    )

    for cookie in browser.get_cookies():
        name = cookie.get("name")
        value = cookie.get("value")

        if not name or value is None:
            continue

        session.cookies.set(
            name=name,
            value=value,
            domain=cookie.get("domain"),
            path=cookie.get(
                "path",
                "/",
            ),
        )

    return session

def convert_image_to_webp(
    image_content: bytes,
    output_path: Path,
    quality: int = 88,
) -> tuple[int, int]:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with Image.open(
        io.BytesIO(image_content)
    ) as image:
        if image.mode in {
            "RGBA",
            "LA",
        }:
            converted = image.convert(
                "RGBA"
            )
        else:
            converted = image.convert(
                "RGB"
            )

        width, height = converted.size

        # Tidak meneruskan EXIF atau metadata sumber.
        converted.save(
            output_path,
            format="WEBP",
            quality=quality,
            method=6,
        )

    return width, height

def download_product_images(
    browser,
    product_url: str,
    image_urls: list[str],
    output_root: Path = Path(
        "data/processed/product_images"
    ),
) -> list[dict[str, Any]]:
    product_id = (
        urlparse(product_url)
        .path
        .rstrip("/")
        .split("/")[-1]
    )

    product_directory = (
        output_root / product_id
    )

    session = create_download_session(
        browser=browser,
        referer_url=product_url,
    )

    results: list[dict[str, Any]] = []

    for position, image_url in enumerate(
        image_urls,
        start=1,
    ):
        output_path = (
            product_directory
            / f"image_{position:02d}.webp"
        )

        record: dict[str, Any] = {
            "position": position,
            "source_url": image_url,
            "local_path": str(output_path),
            "format": "webp",
            "width": None,
            "height": None,
            "status": "pending",
            "error": None,
        }

        try:
            response = session.get(
                image_url,
                timeout=60,
            )

            response.raise_for_status()

            width, height = (
                convert_image_to_webp(
                    image_content=response.content,
                    output_path=output_path,
                )
            )

            record["width"] = width
            record["height"] = height
            record["status"] = "success"

            print(
                f"🖼️ {position}: "
                f"{width}x{height} "
                f"→ {output_path}"
            )

        except Exception as exc:
            record["status"] = "failed"
            record["error"] = str(exc)

            print(
                f"❌ Image {position} gagal: "
                f"{exc}"
            )

        results.append(record)

    return results


def read_product_detail(
    browser,
    product_url: str,
) -> dict[str, Any]:
    """
    Fungsi utama untuk membaca satu halaman product detail.
    """

    print(f"Membuka product URL:\n{product_url}")

    browser.get(product_url)


    wait_for_product_page(
        browser=browser,
        timeout_seconds=30,
    )

    # Tunggu kondisi awal halaman selesai.
    wait_for_specifications_stable(
        browser=browser,
        initial_delay_seconds=3,
        timeout_seconds=20,
        required_stable_checks=2,
    )

    # Klik tombol Mehr jika specification masih collapsed.
    expand_product_specifications(
        browser=browser,
        timeout_seconds=15,
    )

    # Tunggu seluruh item specification selesai muncul.
    final_specification_count = (
        wait_for_all_specifications_loaded(
            browser=browser,
            timeout_seconds=20,
            stable_checks_required=3,
        )
    )

    print(
        f"Total specification DOM yang siap dibaca: "
        f"{final_specification_count}"
    )

    product_title, product_subtitle = (
        read_product_title(browser)
    )

    price_data = read_product_price(
        browser
    )

    image_urls = read_product_image_urls(
        browser
    )

    downloaded_images = download_product_images(
        browser=browser,
        product_url=product_url,
        image_urls=image_urls,
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

    specification_map = specifications_to_map(
        specifications
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
        "requested_url": product_url,
        "final_url": browser.current_url,
        "browser_title": browser.title,
        "product_title": product_title,
        "product_subtitle": product_subtitle,
        "specifications": valid_specifications,
        "specification_notices": specification_notices,
        "specification_map": specification_map,

        "compatibility_rows": compatibility_rows,
        "compatibility_map": compatibility_map,

        "oem_numbers": oem_numbers,
        "oem_numbers_text": oem_numbers_text,
        "ОЕ-Nummern": oem_numbers_text,

        "price_display": price_data.get(
            "price_display"
        ),
        "price_amount": price_data.get(
            "price_amount"
        ),
        "price_currency": price_data.get(
            "price_currency"
        ),

        "image_urls": image_urls,
        "images": downloaded_images,

        "status": "success",
        "error": None,
    }