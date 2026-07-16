from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from app.collectors.product_detail_dom_reader import (
    read_product_detail,
)


def save_page_product_details(
    page_number: int,
    records: list[dict[str, Any]],
) -> Path:
    """
    Menyimpan hasil detail berdasarkan listing page.

    Contoh:
    data/processed/product_details/page_1.json
    """

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


def create_initial_record(
    page_number: int,
    product_index: int,
    product_url: str,
) -> dict[str, Any]:
    """
    Membuat struktur awal agar produk berhasil
    maupun gagal mempunyai format yang sama.
    """

    return {
        "listing_page": page_number,
        "product_index": product_index,
        "requested_url": product_url,
        "final_url": None,
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


def process_product_urls_for_page(
    detail_browser,
    product_urls: list[str],
    page_number: int,
    delay_seconds: float = 3.0,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """
    Menghubungkan URL hasil listing pagination
    dengan product_detail_dom_reader.py.

    product_detail_dom_reader.py tidak perlu diubah.
    """

    urls_to_process = product_urls

    if limit is not None:
        urls_to_process = product_urls[:limit]

    page_records: list[dict[str, Any]] = []

    print()
    print("=" * 70)
    print(
        f"Mulai membaca product detail "
        f"dari listing page {page_number}"
    )
    print(
        f"Jumlah URL detail: "
        f"{len(urls_to_process)}"
    )
    print("=" * 70)

    for product_index, product_url in enumerate(
        urls_to_process,
        start=1,
    ):
        print()
        print("-" * 70)
        print(
            f"[Listing page {page_number}] "
            f"Product {product_index}/"
            f"{len(urls_to_process)}"
        )
        print(f"URL: {product_url}")
        print("-" * 70)

        record = create_initial_record(
            page_number=page_number,
            product_index=product_index,
            product_url=product_url,
        )

        try:
            product_detail = read_product_detail(
                browser=detail_browser,
                product_url=product_url,
            )

            record.update(product_detail)

            # Pastikan metadata listing tidak tertimpa.
            record["listing_page"] = page_number
            record["product_index"] = product_index
            record["requested_url"] = product_url

            print(
                f"✅ Product title: "
                f"{record.get('product_title')}"
            )

            print(
                f"Specifications: "
                f"{len(record.get('specifications', []))}"
            )

            print(
                f"Notices: "
                f"{len(record.get('specification_notices', []))}"
            )

            print(
                f"Compatibility rows: "
                f"{len(record.get('compatibility_rows', []))}"
            )

            print(
                f"OEM numbers: "
                f"{len(record.get('oem_numbers', []))}"
            )

        except Exception as exc:
            record["status"] = "failed"
            record["error"] = str(exc)

            try:
                record["final_url"] = (
                    detail_browser.current_url
                )

                record["browser_title"] = (
                    detail_browser.title
                )

            except Exception:
                pass

            print(
                f"❌ Gagal membaca product "
                f"{product_index}: {exc}"
            )

        page_records.append(record)

        # Simpan setelah setiap produk.
        save_page_product_details(
            page_number=page_number,
            records=page_records,
        )

        if product_index < len(urls_to_process):
            time.sleep(delay_seconds)

    output_path = save_page_product_details(
        page_number=page_number,
        records=page_records,
    )

    success_count = sum(
        1
        for record in page_records
        if record.get("status") == "success"
    )

    failed_count = (
        len(page_records) - success_count
    )

    print()
    print("=" * 70)
    print(
        f"Detail listing page {page_number} selesai"
    )
    print(f"Berhasil: {success_count}")
    print(f"Gagal: {failed_count}")
    print(f"Output: {output_path}")
    print("=" * 70)

    return page_records