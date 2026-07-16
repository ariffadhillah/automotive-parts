from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


LABEL_TRANSLATIONS = {
    "Einbauposition": {
        "en": "Fitting Position",
        "ar": "موضع التركيب",
    },
    "Durchmesser": {
        "en": "Diameter",
        "ar": "القطر",
    },
    "Bremsscheibenart": {
        "en": "Brake Disc Type",
        "ar": "نوع قرص الفرامل",
    },
    "Gelocht": {
        "en": "Drilled",
        "ar": "مثقوب",
    },
    "Oberfläche": {
        "en": "Surface",
        "ar": "السطح",
    },
    "Bearbeitung": {
        "en": "Processing",
        "ar": "المعالجة",
    },
    "Ergänzungsartikel / Ergänzende Info 2": {
        "en": "Supplementary Article / Info 2",
        "ar": "معلومات إضافية 2",
    },
    "Bremsscheibendicke": {
        "en": "Brake Disc Thickness",
        "ar": "سماكة قرص الفرامل",
    },
    "Höhe mm": {
        "en": "Height [mm]",
        "ar": "الارتفاع [مم]",
    },
    "Material": {
        "en": "Material",
        "ar": "المادة",
    },
    "Zentrierungsdurchmesser [mm]": {
        "en": "Centering Diameter [mm]",
        "ar": "قطر التمركز [مم]",
    },
    "Lochanzahl": {
        "en": "Number of Holes",
        "ar": "عدد الفتحات",
    },
    "Radbolzen-Bohrungsdurchmesser [mm]": {
        "en": "Wheel Bolt Hole Diameter [mm]",
        "ar": "قطر فتحة مسمار العجلة [مم]",
    },
    "Lochkreis-Ø [mm]": {
        "en": "Bolt Circle Diameter [mm]",
        "ar": "قطر دائرة المسامير [مم]",
    },
    "Artikelnummer": {
        "en": "Part Number",
        "ar": "رقم القطعة",
    },
    "Hersteller": {
        "en": "Brand",
        "ar": "العلامة التجارية",
    },
    "EAN-Nummer(n)": {
        "en": "EAN Number",
        "ar": "رقم EAN",
    },
    "Zustand": {
        "en": "Condition",
        "ar": "الحالة",
    },
    "Automodelle": {
        "en": "Vehicle Models",
        "ar": "طرازات السيارات",
    },
    "Motoren": {
        "en": "Engines",
        "ar": "المحركات",
    },
    "Auto Leistung (Pferdestärke)": {
        "en": "Vehicle Power [hp]",
        "ar": "قوة السيارة [حصان]",
    },
    "Leistung (Kilowatt)": {
        "en": "Power [kW]",
        "ar": "القدرة [كيلوواط]",
    },
    "Baujahr": {
        "en": "Production Years",
        "ar": "سنوات الإنتاج",
    },
    "Hersteller Artikelnummer": {
        "en": "Manufacturer Part Number",
        "ar": "رقم قطعة الشركة المصنعة",
    },
    "OE-Referenznummer(n)": {
        "en": "OE Reference Numbers",
        "ar": "الأرقام المرجعية OE",
    },
}



VALUE_TRANSLATIONS = {
    "Vorderachse": {
        "en": "Front Axle",
        "ar": "المحور الأمامي",
    },
    "Hinterachse": {
        "en": "Rear Axle",
        "ar": "المحور الخلفي",
    },
    "Belüftet": {
        "en": "Vented",
        "ar": "مهواة",
    },
    "innenbelüftet": {
        "en": "Internally Vented",
        "ar": "مهواة داخليًا",
    },
    "Gusseisen": {
        "en": "Cast Iron",
        "ar": "حديد زهر",
    },
    "Brandneu": {
        "en": "New",
        "ar": "جديد",
    },
    "nein": {
        "en": "No",
        "ar": "لا",
    },
    "ja": {
        "en": "Yes",
        "ar": "نعم",
    },
    "unbeschichtet": {
        "en": "Uncoated",
        "ar": "غير مطلي",
    },
    "beschichtet": {
        "en": "Coated",
        "ar": "مطلي",
    },
    "unbehandelt": {
        "en": "Untreated",
        "ar": "غير معالج",
    },
    "ohne Schrauben": {
        "en": "Without Screws",
        "ar": "بدون براغي",
    },
    (
        "Diese Eigenschaft variiert "
        "je nach Fahrzeugmodell"
    ): {
        "en": (
            "This property varies depending "
            "on the vehicle model"
        ),
        "ar": (
            "تختلف هذه الخاصية حسب طراز السيارة"
        ),
    },
}


def translate_label(
    value: str,
    language: str,
) -> str:
    translation = LABEL_TRANSLATIONS.get(
        value,
        {},
    )

    return translation.get(
        language,
        value,
    )


def translate_value(
    value: str,
    language: str,
) -> str:
    translation = VALUE_TRANSLATIONS.get(
        value,
        {},
    )

    if language in translation:
        return translation[language]

    if language == "en":
        return (
            value
            .replace(" Jahre", " years")
            .replace(" PS", " hp")
        )

    if language == "ar":
        return (
            value
            .replace(" Jahre", " سنة")
            .replace(" PS", " حصان")
        )

    return value



def translate_product_text(
    value: str | None,
    language: str,
) -> str | None:
    if not value:
        return None

    translated = value

    replacements = {
        "Bremsscheibe": {
            "en": "Brake Disc",
            "ar": "قرص فرامل",
        },
        "Bremsscheiben": {
            "en": "Brake Discs",
            "ar": "أقراص الفرامل",
        },
        "für": {
            "en": "for",
            "ar": "لـ",
        },
        "Vorderachse": {
            "en": "Front Axle",
            "ar": "المحور الأمامي",
        },
        "Belüftet": {
            "en": "Vented",
            "ar": "مهواة",
        },
        "innenbelüftet": {
            "en": "Internally Vented",
            "ar": "مهواة داخليًا",
        },
        "Gusseisen": {
            "en": "Cast Iron",
            "ar": "حديد زهر",
        },
    }

    for original, languages in replacements.items():
        replacement = languages.get(language)

        if replacement:
            translated = re.sub(
                rf"\b{re.escape(original)}\b",
                replacement,
                translated,
                flags=re.IGNORECASE,
            )

    return translated


def translate_map(
    source_map: dict[str, Any],
    language: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for label, value in source_map.items():
        translated_label = translate_label(
            str(label),
            language,
        )

        if isinstance(value, list):
            translated_value = [
                translate_value(
                    str(item),
                    language,
                )
                for item in value
            ]
        else:
            translated_value = translate_value(
                str(value),
                language,
            )

        result[translated_label] = (
            translated_value
        )

    return result


def build_client_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    specification_de = record.get(
        "specification_map",
        {},
    )

    compatibility_de = record.get(
        "compatibility_map",
        {},
    )

    return {
        "source_url": record.get(
            "requested_url"
        ),

        "product_title_de": record.get(
            "product_title"
        ),
        "product_title_en": (
            translate_product_text(
                record.get("product_title"),
                "en",
            )
        ),
        "product_title_ar": (
            translate_product_text(
                record.get("product_title"),
                "ar",
            )
        ),

        "product_subtitle_de": record.get(
            "product_subtitle"
        ),
        "product_subtitle_en": (
            translate_product_text(
                record.get("product_subtitle"),
                "en",
            )
        ),
        "product_subtitle_ar": (
            translate_product_text(
                record.get("product_subtitle"),
                "ar",
            )
        ),

        "price_display": record.get(
            "price_display"
        ),
        "price_amount": record.get(
            "price_amount"
        ),
        "price_currency": record.get(
            "price_currency"
        ),

        "specification_map_de": (
            specification_de
        ),
        "specification_map_en": (
            translate_map(
                specification_de,
                "en",
            )
        ),
        "specification_map_ar": (
            translate_map(
                specification_de,
                "ar",
            )
        ),

        "compatibility_map_de": (
            compatibility_de
        ),
        "compatibility_map_en": (
            translate_map(
                compatibility_de,
                "en",
            )
        ),
        "compatibility_map_ar": (
            translate_map(
                compatibility_de,
                "ar",
            )
        ),

        "oem_numbers": record.get(
            "oem_numbers",
            [],
        ),
        "oe_numbers_text": record.get(
            "ОЕ-Nummern",
            "",
        ),

        "images": record.get(
            "images",
            [],
        ),
    }


def export_client_sample(
    input_paths: list[Path],
    output_directory: Path,
    maximum_products: int = 3,
) -> None:
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_records: list[dict[str, Any]] = []

    for input_path in input_paths:
        if not input_path.exists():
            continue

        data = json.loads(
            input_path.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, list):
            raw_records.extend(
                item
                for item in data
                if (
                    isinstance(item, dict)
                    and item.get("status")
                    == "success"
                )
            )

    raw_records = raw_records[
        :maximum_products
    ]

    client_records = [
        build_client_record(record)
        for record in raw_records
    ]

    json_path = (
        output_directory
        / "autodoc_sample_de_en_ar.json"
    )

    json_path.write_text(
        json.dumps(
            client_records,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    csv_path = (
        output_directory
        / "autodoc_sample_de_en_ar.csv"
    )

    csv_rows: list[dict[str, Any]] = []

    for record in client_records:
        images = record.get("images", [])

        successful_images = [
            item
            for item in images
            if item.get("status") == "success"
        ]

        csv_rows.append(
            {
                "source_url": record.get(
                    "source_url"
                ),

                "product_title_de": record.get(
                    "product_title_de"
                ),
                "product_title_en": record.get(
                    "product_title_en"
                ),
                "product_title_ar": record.get(
                    "product_title_ar"
                ),

                "product_subtitle_de": record.get(
                    "product_subtitle_de"
                ),
                "product_subtitle_en": record.get(
                    "product_subtitle_en"
                ),
                "product_subtitle_ar": record.get(
                    "product_subtitle_ar"
                ),

                "price_display": record.get(
                    "price_display"
                ),
                "price_amount": record.get(
                    "price_amount"
                ),
                "price_currency": record.get(
                    "price_currency"
                ),

                "specifications_de": json.dumps(
                    record.get(
                        "specification_map_de",
                        {},
                    ),
                    ensure_ascii=False,
                ),
                "specifications_en": json.dumps(
                    record.get(
                        "specification_map_en",
                        {},
                    ),
                    ensure_ascii=False,
                ),
                "specifications_ar": json.dumps(
                    record.get(
                        "specification_map_ar",
                        {},
                    ),
                    ensure_ascii=False,
                ),

                "compatibility_de": json.dumps(
                    record.get(
                        "compatibility_map_de",
                        {},
                    ),
                    ensure_ascii=False,
                ),
                "compatibility_en": json.dumps(
                    record.get(
                        "compatibility_map_en",
                        {},
                    ),
                    ensure_ascii=False,
                ),
                "compatibility_ar": json.dumps(
                    record.get(
                        "compatibility_map_ar",
                        {},
                    ),
                    ensure_ascii=False,
                ),

                "oe_numbers": record.get(
                    "oe_numbers_text"
                ),

                "image_1": (
                    successful_images[0].get(
                        "local_path"
                    )
                    if len(successful_images) > 0
                    else ""
                ),
                "image_2": (
                    successful_images[1].get(
                        "local_path"
                    )
                    if len(successful_images) > 1
                    else ""
                ),
                "image_3": (
                    successful_images[2].get(
                        "local_path"
                    )
                    if len(successful_images) > 2
                    else ""
                ),
            }
        )

    if csv_rows:
        with csv_path.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=list(
                    csv_rows[0].keys()
                ),
            )

            writer.writeheader()
            writer.writerows(csv_rows)

    print(f"JSON sample: {json_path}")
    print(f"CSV sample : {csv_path}")