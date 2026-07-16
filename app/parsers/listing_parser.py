from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.models.product import ProductRecord, VehicleInfo
from app.parsers.jsonld_parser import (
    extract_jsonld_blocks,
    find_jsonld_type,
)


BASE_URL = "https://www.autodoc.de"


class AutoDocListingParser:
    def parse(
        self,
        html: str,
        source_url: str,
    ) -> list[ProductRecord]:
        soup = BeautifulSoup(html, "lxml")

        vehicle = self._parse_vehicle(soup)
        category = self._parse_category(soup)

        products = self._parse_from_product_links(
            soup=soup,
            source_url=source_url,
            category=category,
            vehicle=vehicle,
        )

        return products

    def _parse_vehicle(self, soup: BeautifulSoup) -> VehicleInfo:
        page_text = soup.get_text(" ", strip=True)

        title = soup.title.get_text(" ", strip=True) if soup.title else ""

        engine_code_match = re.search(
            r"\b([A-Z][A-Z0-9]{2,5})\b",
            title,
        )

        power_hp_match = re.search(r"(\d+)\s*PS", title)
        power_kw_match = re.search(r"(\d+)\s*kW", title)

        kba_match = re.search(r"KBA:\s*([A-Z0-9]+)", page_text)

        production_match = re.search(
            r"(\d{4}\s*-\s*\d{4})",
            title,
        )

        return VehicleInfo(
            make="HYUNDAI",
            model="Accent",
            generation="Accent II Limousine (LC)",
            variant="1.3",
            engine_code=(
                engine_code_match.group(1)
                if engine_code_match
                else None
            ),
            power_hp=(
                int(power_hp_match.group(1))
                if power_hp_match
                else None
            ),
            power_kw=(
                int(power_kw_match.group(1))
                if power_kw_match
                else None
            ),
            fuel_type=(
                "Benzin"
                if "Benzin" in title
                else None
            ),
            production_years=(
                production_match.group(1)
                if production_match
                else None
            ),
            kba=(
                kba_match.group(1)
                if kba_match
                else None
            ),
        )

    def _parse_category(self, soup: BeautifulSoup) -> str | None:
        heading = soup.find("h1")

        if heading:
            text = heading.get_text(" ", strip=True)

            if text:
                return text.split(" Hyundai", 1)[0].strip()

        return None

    def _parse_from_product_links(
        self,
        soup: BeautifulSoup,
        source_url: str,
        category: str | None,
        vehicle: VehicleInfo,
    ) -> list[ProductRecord]:
        products: list[ProductRecord] = []
        seen_urls: set[str] = set()

        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "")
            text = anchor.get_text(" ", strip=True)

            if not href or not text:
                continue

            if not re.search(
                r"\bBremsscheibe\b",
                text,
                flags=re.IGNORECASE,
            ):
                continue

            product_url = urljoin(BASE_URL, href)

            if product_url in seen_urls:
                continue

            part_number = self._extract_part_number(text)
            brand = self._extract_brand(text)

            products.append(
                ProductRecord(
                    source_url=source_url,
                    product_url=product_url,
                    category_original=category,
                    part_name_original=text,
                    brand=brand,
                    part_number=part_number,
                    vehicle=vehicle.model_copy(deep=True),
                )
            )

            seen_urls.add(product_url)

        return products

    @staticmethod
    def _extract_brand(text: str) -> str | None:
        parts = text.split()

        if not parts:
            return None

        return parts[0].strip()

    @staticmethod
    def _extract_part_number(text: str) -> str | None:
        match = re.search(
            r"^[A-Z0-9.+&-]+\s+(.+?)\s+Bremsscheibe",
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            return None

        return match.group(1).strip()