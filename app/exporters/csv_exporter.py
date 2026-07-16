from __future__ import annotations

import csv
import json
from pathlib import Path

from app.models.product import ProductRecord


CSV_FIELDS = [
    "source",
    "source_url",
    "product_url",
    "product_id",
    "category_original",
    "category_ar",
    "part_name_original",
    "part_name_ar",
    "brand",
    "part_number",
    "ean",
    "price",
    "currency",
    "availability",
    "condition",
    "image_url",
    "local_image_path",
    "vehicle_make",
    "vehicle_model",
    "vehicle_generation",
    "vehicle_variant",
    "engine",
    "engine_code",
    "power_hp",
    "power_kw",
    "fuel_type",
    "production_years",
    "kba",
    "technical_details",
    "technical_details_ar",
    "oem_numbers",
    "cross_references",
]


def export_products_to_csv(
    products: list[ProductRecord],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=CSV_FIELDS,
        )

        writer.writeheader()

        for product in products:
            vehicle = product.vehicle

            writer.writerow(
                {
                    "source": product.source,
                    "source_url": product.source_url,
                    "product_url": product.product_url,
                    "product_id": product.product_id,
                    "category_original": product.category_original,
                    "category_ar": product.category_ar,
                    "part_name_original": product.part_name_original,
                    "part_name_ar": product.part_name_ar,
                    "brand": product.brand,
                    "part_number": product.part_number,
                    "ean": product.ean,
                    "price": product.price,
                    "currency": product.currency,
                    "availability": product.availability,
                    "condition": product.condition,
                    "image_url": product.image_url,
                    "local_image_path": product.local_image_path,
                    "vehicle_make": vehicle.make,
                    "vehicle_model": vehicle.model,
                    "vehicle_generation": vehicle.generation,
                    "vehicle_variant": vehicle.variant,
                    "engine": vehicle.engine,
                    "engine_code": vehicle.engine_code,
                    "power_hp": vehicle.power_hp,
                    "power_kw": vehicle.power_kw,
                    "fuel_type": vehicle.fuel_type,
                    "production_years": vehicle.production_years,
                    "kba": vehicle.kba,
                    "technical_details": json.dumps(
                        product.technical_details,
                        ensure_ascii=False,
                    ),
                    "technical_details_ar": json.dumps(
                        product.technical_details_ar,
                        ensure_ascii=False,
                    ),
                    "oem_numbers": "|".join(product.oem_numbers),
                    "cross_references": "|".join(
                        product.cross_references
                    ),
                }
            )