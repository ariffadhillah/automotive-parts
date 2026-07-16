from __future__ import annotations

import json
from typing import Any

from bs4 import BeautifulSoup


def extract_jsonld_blocks(
    soup: BeautifulSoup,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    scripts = soup.find_all(
        "script",
        attrs={"type": "application/ld+json"},
    )

    for script in scripts:
        raw = script.string or script.get_text(strip=True)

        if not raw:
            continue

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, dict):
            results.append(parsed)

        elif isinstance(parsed, list):
            results.extend(
                item for item in parsed if isinstance(item, dict)
            )

    return results


def find_jsonld_type(
    blocks: list[dict[str, Any]],
    target_type: str,
) -> dict[str, Any] | None:
    for block in blocks:
        block_type = block.get("@type")

        if block_type == target_type:
            return block

        graph = block.get("@graph")

        if isinstance(graph, list):
            for item in graph:
                if (
                    isinstance(item, dict)
                    and item.get("@type") == target_type
                ):
                    return item

    return None