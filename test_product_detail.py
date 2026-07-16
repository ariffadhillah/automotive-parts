import json
from pathlib import Path

from app.collectors.product_detail_dom_reader import (
    read_product_detail,
)

from app.browser import setup_browser

PRODUCT_URL = (
    "https://www.autodoc.de/"
    "borg-beck/10720907"
)




def save_product_detail(
    product_detail: dict,
) -> Path:
    output_path = Path(
        "data/processed/"
        "single_product_detail.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            product_detail,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path


def main():
    browser = setup_browser()

    try:
        product_detail = read_product_detail(
            browser=browser,
            product_url=PRODUCT_URL,
        )

        print()
        print("=" * 60)
        print(
            "Product title:",
            product_detail["product_title"],
        )
        print(
            "Product subtitle:",
            product_detail[
                "product_subtitle"
            ],
        )

        print()
        print("Specifications:")

        for item in product_detail[
            "specifications"
        ]:
            print(
                f"- {item['name_original']}: "
                f"{item['value_original']}"
            )

        print()
        print("Specification notices:")

        for item in product_detail[
            "specification_notices"
        ]:
            print(
                f"- {item['name_original']}: "
                f"{item['value_original']}"
            )

        print()
        print(
            "OEM:",
            product_detail[
                "oem_numbers_text"
            ],
        )

        output_path = save_product_detail(
            product_detail
        )

        print()
        print(
            f"JSON disimpan ke: {output_path}"
        )

    except Exception as exc:
        print(
            f"❌ Gagal membaca product detail: "
            f"{exc}"
        )

    finally:
        input(
            "\nTekan ENTER untuk menutup browser..."
        )
        browser.quit()


if __name__ == "__main__":
    main()