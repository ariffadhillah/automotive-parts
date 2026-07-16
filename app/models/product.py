from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class VehicleInfo(BaseModel):
    make: str | None = None
    model: str | None = None
    generation: str | None = None
    variant: str | None = None
    engine: str | None = None
    engine_code: str | None = None
    power_hp: int | None = None
    power_kw: int | None = None
    fuel_type: str | None = None
    production_years: str | None = None
    kba: str | None = None


class ProductRecord(BaseModel):
    source: str = "autodoc.de"
    source_url: str

    product_url: str | None = None
    product_id: str | None = None

    category_original: str | None = None
    category_ar: str | None = None

    part_name_original: str | None = None
    part_name_ar: str | None = None

    brand: str | None = None
    part_number: str | None = None
    ean: str | None = None

    price: float | None = None
    currency: str = "EUR"
    availability: str | None = None
    condition: str | None = None

    image_url: str | None = None
    local_image_path: str | None = None

    vehicle: VehicleInfo = Field(default_factory=VehicleInfo)

    technical_details: dict[str, Any] = Field(default_factory=dict)
    technical_details_ar: dict[str, Any] = Field(default_factory=dict)

    oem_numbers: list[str] = Field(default_factory=list)
    cross_references: list[str] = Field(default_factory=list)