from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_DIRECTORY = Path(
    "data/processed/product_details"
)

OUTPUT_DIRECTORY = Path(
    "data/samples/autodoc_client_sample"
)

MAXIMUM_PRODUCTS = None

# Karena sample saat ini adalah kategori brake disc.
CATEGORY_ORIGINAL = "Bremsscheiben"
CATEGORY_ENGLISH = "Brake Discs"
CATEGORY_ARABIC = "أقراص الفرامل"


# ============================================================
# TRANSLATION MAPS
# ============================================================

LABEL_TRANSLATIONS_EN = {
    "Einbauposition": "Fitting Position",
    "Durchmesser": "Diameter",
    "Bremsscheibenart": "Brake Disc Type",
    "Gelocht": "Drilled",
    "Oberfläche": "Surface",
    "Bearbeitung": "Processing",
    "Ergänzungsartikel / Ergänzende Info 2": (
        "Supplementary Article / Supplementary Info 2"
    ),
    "Ergänzungsartikel  /  Ergänzende Info 2": (
        "Supplementary Article / Supplementary Info 2"
    ),
    "Bremsscheibendicke": "Brake Disc Thickness",
    "Höhe mm": "Height [mm]",
    "Material": "Material",
    "Zentrierungsdurchmesser [mm]": (
        "Centering Diameter [mm]"
    ),
    "Lochanzahl": "Number of Holes",
    "Radbolzen-Bohrungsdurchmesser [mm]": (
        "Wheel Bolt Hole Diameter [mm]"
    ),
    "Lochkreis-Ø [mm]": (
        "Bolt Circle Diameter [mm]"
    ),
    "Mindestdicke [mm]": (
        "Minimum Thickness [mm]"
    ),
    "Anzahl der Befestigungsbohrungen": (
        "Number of Mounting Holes"
    ),
    "Prüfzeichen": "Test Mark",
    "Artikelnummer": "Part Number",
    "Hersteller": "Brand",
    "EAN-Nummer(n)": "EAN Number",
    "Zustand": "Condition",

    # Compatibility
    "Automodelle": "Vehicle Models",
    "Motoren": "Engines",
    "Auto Leistung (Pferdestärke)": (
        "Vehicle Power [hp]"
    ),
    "Leistung (Kilowatt)": "Power [kW]",
    "Baujahr": "Production Years",
    "Hersteller Artikelnummer": (
        "Manufacturer Part Number"
    ),
    "OE-Referenznummer(n)": (
        "OE Reference Numbers"
    ),
}


VALUE_TRANSLATIONS_EN = {
    "Vorderachse": "Front Axle",
    "Hinterachse": "Rear Axle",
    "Belüftet": "Vented",
    "innenbelüftet": "Internally Vented",
    "Voll": "Solid",
    "Gelocht": "Drilled",
    "nein": "No",
    "ja": "Yes",
    "unbeschichtet": "Uncoated",
    "beschichtet": "Coated",
    "geölt": "Oiled",
    "unbehandelt": "Untreated",
    "ohne Schrauben": "Without Screws",
    "mit Schrauben": "With Screws",
    "Gusseisen": "Cast Iron",
    "Stahl": "Steel",
    "Brandneu": "New",
    "Diese Eigenschaft variiert je nach Fahrzeugmodell": (
        "This property varies depending on the vehicle model"
    ),
}


TITLE_TRANSLATIONS_EN = {
    "Bremsscheiben": "Brake Discs",
    "Bremsscheibe": "Brake Disc",
    "Vorderachse": "Front Axle",
    "Hinterachse": "Rear Axle",
    "innenbelüftet": "Internally Vented",
    "Belüftet": "Vented",
    "Gusseisen": "Cast Iron",
    "für": "for",
}


TITLE_TRANSLATIONS_AR = {
    "Bremsscheiben": "أقراص الفرامل",
    "Bremsscheibe": "قرص فرامل",
    "Vorderachse": "المحور الأمامي",
    "Hinterachse": "المحور الخلفي",
    "innenbelüftet": "مهواة داخليًا",
    "Belüftet": "مهواة",
    "Gusseisen": "حديد زهر",
    "für": "لـ",
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean_text(value: Any) -> str:
    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value),
    ).strip()


def value_to_csv(value: Any) -> str:
    """
    Mengubah list atau nilai lain menjadi teks CSV bersih.
    """

    if value is None:
        return ""

    if isinstance(value, list):
        return ", ".join(
            clean_text(item)
            for item in value
            if clean_text(item)
        )

    if isinstance(value, bool):
        return "true" if value else "false"

    return clean_text(value)


def replace_case_insensitive(
    text: str,
    original: str,
    replacement: str,
) -> str:
    return re.sub(
        re.escape(original),
        replacement,
        text,
        flags=re.IGNORECASE,
    )


def translate_product_text(
    value: Any,
    language: str,
) -> str:
    text = clean_text(value)

    if not text:
        return ""

    if language == "en":
        replacements = TITLE_TRANSLATIONS_EN
    elif language == "ar":
        replacements = TITLE_TRANSLATIONS_AR
    else:
        return text

    # Frasa yang lebih panjang diganti lebih dahulu.
    ordered_replacements = sorted(
        replacements.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    translated = text

    for original, replacement in ordered_replacements:
        translated = replace_case_insensitive(
            translated,
            original,
            replacement,
        )

    if language == "en":
        translated = normalize_english_technical_text(
            translated
        )

    return clean_text(translated)


def normalize_english_technical_text(
    value: Any,
) -> str:
    """
    Normalisasi teks teknis Jerman menjadi format global.

    Contoh:
    241,3 -> 241.3
    75-106 PS -> 75-106 hp
    1999-2006 Jahre -> 1999-2006 years
    """

    text = clean_text(value)

    if not text:
        return ""

    # Koma desimal di antara angka menjadi titik.
    text = re.sub(
        r"(?<=\d),(?=\d)",
        ".",
        text,
    )

    text = re.sub(
        r"\bJahre\b",
        "years",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\bPS\b",
        "hp",
        text,
        flags=re.IGNORECASE,
    )

    # Beberapa nilai teknis yang umum.
    translated_exact = VALUE_TRANSLATIONS_EN.get(
        text
    )

    if translated_exact:
        return translated_exact

    # Menerjemahkan istilah yang muncul di dalam kalimat.
    replacements = sorted(
        VALUE_TRANSLATIONS_EN.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for original, replacement in replacements:
        text = replace_case_insensitive(
            text,
            original,
            replacement,
        )

    return clean_text(text)


def translate_label_to_english(
    label: Any,
) -> str:
    cleaned = clean_text(label)

    return LABEL_TRANSLATIONS_EN.get(
        cleaned,
        cleaned,
    )


def translate_value_to_english(
    value: Any,
) -> str:
    if isinstance(value, list):
        return ", ".join(
            normalize_english_technical_text(item)
            for item in value
            if clean_text(item)
        )

    cleaned = clean_text(value)

    if not cleaned:
        return ""

    exact_translation = VALUE_TRANSLATIONS_EN.get(
        cleaned
    )

    if exact_translation:
        return exact_translation

    return normalize_english_technical_text(
        cleaned
    )


# ============================================================
# IMAGE HELPERS
# ============================================================

def get_successful_images(
    record: dict[str, Any],
) -> list[dict[str, Any]]:
    images = record.get("images", [])

    if not isinstance(images, list):
        return []

    return [
        image
        for image in images
        if (
            isinstance(image, dict)
            and image.get("status") == "success"
        )
    ]


def get_image_urls(
    record: dict[str, Any],
) -> str:
    successful_images = get_successful_images(
        record
    )

    urls: list[str] = []

    for image in successful_images:
        source_url = clean_text(
            image.get("source_url")
        )

        if source_url and source_url not in urls:
            urls.append(source_url)

    # Fallback jika download record belum memiliki images.
    if not urls:
        raw_image_urls = record.get(
            "image_urls",
            [],
        )

        if isinstance(raw_image_urls, list):
            for image_url in raw_image_urls:
                cleaned_url = clean_text(image_url)

                if (
                    cleaned_url
                    and cleaned_url not in urls
                ):
                    urls.append(cleaned_url)

    return ", ".join(urls)


def get_image_files(
    record: dict[str, Any],
) -> str:
    successful_images = get_successful_images(
        record
    )

    image_files: list[str] = []

    for image in successful_images:
        candidate = (
            image.get("sample_path")
            or image.get("filename")
            or image.get("local_path")
        )

        candidate_text = clean_text(candidate)

        if not candidate_text:
            continue

        # Agar mudah dibuka lintas sistem.
        candidate_text = candidate_text.replace(
            "\\",
            "/",
        )

        if candidate_text not in image_files:
            image_files.append(candidate_text)

    return ", ".join(image_files)


def get_image_filenames(
    record: dict[str, Any],
) -> str:
    """
    Menyimpan nama file saja tanpa seluruh path.
    """

    successful_images = get_successful_images(
        record
    )

    filenames: list[str] = []

    for image in successful_images:
        filename = clean_text(
            image.get("filename")
        )

        if not filename:
            local_path = clean_text(
                image.get("local_path")
            )

            if local_path:
                filename = Path(
                    local_path
                ).name

        if filename and filename not in filenames:
            filenames.append(filename)

    return ", ".join(filenames)


# ============================================================
# MAP FLATTENING
# ============================================================

def add_original_map_to_row(
    row: dict[str, Any],
    source_map: Any,
) -> None:
    if not isinstance(source_map, dict):
        return

    for label, value in source_map.items():
        cleaned_label = clean_text(label)

        if not cleaned_label:
            continue

        row[cleaned_label] = value_to_csv(
            value
        )


def add_english_map_to_row(
    row: dict[str, Any],
    source_map: Any,
) -> None:
    if not isinstance(source_map, dict):
        return

    for label, value in source_map.items():
        translated_label = (
            translate_label_to_english(
                label
            )
        )

        if not translated_label:
            continue

        row[translated_label] = (
            translate_value_to_english(
                value
            )
        )


# ============================================================
# ROW BUILDERS
# ============================================================

def build_original_row(
    record: dict[str, Any],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "url": record.get("requested_url"),
        "category title": CATEGORY_ORIGINAL,
        "product title": record.get(
            "product_title"
        ),
        "product subtitle": record.get(
            "product_subtitle"
        ),
        "price": record.get(
            "price_display"
        ),
        "price amount": record.get(
            "price_amount"
        ),
        "currency": record.get(
            "price_currency"
        ),
    }

    add_original_map_to_row(
        row,
        record.get(
            "specification_map",
            {},
        ),
    )

    add_original_map_to_row(
        row,
        record.get(
            "compatibility_map",
            {},
        ),
    )

    row["ОЕ-Nummern"] = record.get(
        "ОЕ-Nummern",
        record.get(
            "oem_numbers_text",
            "",
        ),
    )

    row["image URLs"] = get_image_urls(
        record
    )

    row["image files"] = get_image_files(
        record
    )

    row["image filenames"] = (
        get_image_filenames(record)
    )

    return row


def build_english_row(
    record: dict[str, Any],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "url": record.get("requested_url"),
        "category title": CATEGORY_ENGLISH,
        "product title": (
            translate_product_text(
                record.get("product_title"),
                "en",
            )
        ),
        "product subtitle": (
            translate_product_text(
                record.get("product_subtitle"),
                "en",
            )
        ),
        "price": record.get(
            "price_display"
        ),
        "price amount": record.get(
            "price_amount"
        ),
        "currency": record.get(
            "price_currency"
        ),
    }

    add_english_map_to_row(
        row,
        record.get(
            "specification_map",
            {},
        ),
    )

    add_english_map_to_row(
        row,
        record.get(
            "compatibility_map",
            {},
        ),
    )

    row["OE numbers"] = record.get(
        "ОЕ-Nummern",
        record.get(
            "oem_numbers_text",
            "",
        ),
    )

    row["image URLs"] = get_image_urls(
        record
    )

    row["image files"] = get_image_files(
        record
    )

    row["image filenames"] = (
        get_image_filenames(record)
    )

    return row


def build_arabic_hybrid_row(
    record: dict[str, Any],
) -> dict[str, Any]:
    """
    Sesuai instruksi client:

    - Category title dalam Arabic.
    - Part/product title dalam Arabic.
    - Semua technical fields tetap English/global.
    - Product subtitle diperlakukan sebagai technical detail,
      sehingga disimpan dalam English.
    - Brand, model, part number, EAN, engine, dan OE tetap global.
    """

    row: dict[str, Any] = {
        "url": record.get("requested_url"),
        "category title": CATEGORY_ARABIC,
        "product title": (
            translate_product_text(
                record.get("product_title"),
                "ar",
            )
        ),
        "product subtitle": (
            translate_product_text(
                record.get("product_subtitle"),
                "en",
            )
        ),
        "price": record.get(
            "price_display"
        ),
        "price amount": record.get(
            "price_amount"
        ),
        "currency": record.get(
            "price_currency"
        ),
    }

    # Technical data menggunakan English/global.
    add_english_map_to_row(
        row,
        record.get(
            "specification_map",
            {},
        ),
    )

    add_english_map_to_row(
        row,
        record.get(
            "compatibility_map",
            {},
        ),
    )

    row["OE numbers"] = record.get(
        "ОЕ-Nummern",
        record.get(
            "oem_numbers_text",
            "",
        ),
    )

    row["image URLs"] = get_image_urls(
        record
    )

    row["image files"] = get_image_files(
        record
    )

    row["image filenames"] = (
        get_image_filenames(record)
    )

    return row


# ============================================================
# CSV FIELD ORDER
# ============================================================

def collect_fieldnames(
    rows: list[dict[str, Any]],
) -> list[str]:
    """
    Menggabungkan seluruh nama field dari semua produk.

    Penting karena setiap produk bisa memiliki
    spesifikasi yang berbeda.
    """

    leading_fields = [
        "url",
        "category title",
        "product title",
        "product subtitle",
        "price",
        "price amount",
        "currency",
    ]

    trailing_fields = [
        "ОЕ-Nummern",
        "OE numbers",
        "image URLs",
        "image files",
        "image filenames",
    ]

    all_fields: list[str] = []
    seen: set[str] = set()

    # Kolom identitas utama di awal.
    for field in leading_fields:
        if any(field in row for row in rows):
            all_fields.append(field)
            seen.add(field)

    # Specification dan compatibility di tengah.
    for row in rows:
        for field in row:
            if field in seen:
                continue

            if field in trailing_fields:
                continue

            all_fields.append(field)
            seen.add(field)

    # OEM dan gambar di akhir.
    for field in trailing_fields:
        if (
            field not in seen
            and any(
                field in row
                for row in rows
            )
        ):
            all_fields.append(field)
            seen.add(field)

    return all_fields


def write_csv(
    rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    if not rows:
        print(
            f"⚠️ Tidak ada data untuk: "
            f"{output_path}"
        )
        return

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = collect_fieldnames(
        rows
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        for row in rows:
            normalized_row = {
                field: value_to_csv(
                    row.get(field)
                )
                for field in fieldnames
            }

            writer.writerow(
                normalized_row
            )


# ============================================================
# INPUT LOADING
# ============================================================

def load_successful_records(
    input_directory: Path,
    maximum_products: int | None,
) -> list[dict[str, Any]]:
    input_paths = sorted(
        input_directory.glob(
            "page_*.json"
        )
    )

    if not input_paths:
        raise FileNotFoundError(
            "Tidak menemukan page_*.json di: "
            f"{input_directory}"
        )

    records: list[dict[str, Any]] = []

    for input_path in input_paths:
        print(
            f"Membaca input: {input_path}"
        )

        try:
            data = json.loads(
                input_path.read_text(
                    encoding="utf-8"
                )
            )
        except json.JSONDecodeError as exc:
            print(
                f"⚠️ JSON tidak valid, dilewati: "
                f"{input_path} | {exc}"
            )
            continue

        if not isinstance(data, list):
            continue

        for item in data:
            if not isinstance(item, dict):
                continue

            if item.get("status") != "success":
                continue

            records.append(item)

            if (
                maximum_products is not None
                and len(records)
                >= maximum_products
            ):
                return records

    return records


# ============================================================
# EXPORT
# ============================================================

def export_client_sample() -> None:
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_records = load_successful_records(
        input_directory=INPUT_DIRECTORY,
        maximum_products=MAXIMUM_PRODUCTS,
    )

    if not raw_records:
        raise RuntimeError(
            "Tidak ada record berstatus success "
            "yang dapat diekspor."
        )

    original_rows = [
        build_original_row(record)
        for record in raw_records
    ]

    english_rows = [
        build_english_row(record)
        for record in raw_records
    ]

    arabic_rows = [
        build_arabic_hybrid_row(record)
        for record in raw_records
    ]

    original_path = (
        OUTPUT_DIRECTORY
        / "autodoc sample original.csv"
    )

    english_path = (
        OUTPUT_DIRECTORY
        / "autodoc sample english.csv"
    )

    arabic_path = (
        OUTPUT_DIRECTORY
        / "autodoc sample arabic hybrid.csv"
    )

    write_csv(
        rows=original_rows,
        output_path=original_path,
    )

    write_csv(
        rows=english_rows,
        output_path=english_path,
    )

    write_csv(
        rows=arabic_rows,
        output_path=arabic_path,
    )

    print()
    print("=" * 70)
    print(
        f"Jumlah produk diekspor: "
        f"{len(raw_records)}"
    )
    print(
        f"Original CSV: {original_path}"
    )
    print(
        f"English CSV : {english_path}"
    )
    print(
        f"Arabic CSV  : {arabic_path}"
    )
    print("=" * 70)


def main() -> None:
    try:
        export_client_sample()

    except Exception as exc:
        print(
            f"❌ Export gagal: {exc}"
        )
        raise


if __name__ == "__main__":
    main()