from pathlib import Path

from app.exporters.client_sample_exporter import (
    export_client_sample,
)


def main() -> None:
    export_client_sample(
        input_paths=[
            Path(
                "data/processed/product_details/"
                "page_1.json"
            ),
            Path(
                "data/processed/product_details/"
                "page_2.json"
            ),
            Path(
                "data/processed/product_details/"
                "page_3.json"
            ),
            Path(
                "data/processed/product_details/"
                "page_4.json"
            ),
        ],
        output_directory=Path(
            "data/samples/autodoc_client_sample"
        ),
        maximum_products=3,
    )


if __name__ == "__main__":
    main()