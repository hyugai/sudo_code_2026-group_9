"""Catalog domain tools — catalog.search, inventory.check, pricing.get_quote"""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from telesale_agent.adapters.mock.mock_data import (
    PRODUCTS, PRODUCT_ALIASES, PROMOTIONS
)

REFERENCE_DATE = date(2026, 10, 15)


def _today(on: str | None) -> date:
    return date.fromisoformat(on) if on else REFERENCE_DATE


def _load_btc_products() -> dict[str, Any]:
    """Try to load BTC products.json if available, fallback to mock_data."""
    for path in [
        "dataset/BTC-Data-Vong1-TEAMS/catalog/products.json",
        "BTC-Data-Vong1-TEAMS/catalog/products.json",
    ]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                # Normalize to {sku: product} dict
                if isinstance(raw, list):
                    return {p["sku"]: p for p in raw}
                return raw
        except FileNotFoundError:
            continue
    return PRODUCTS  # fallback to built-in mock


def catalog_search(
    query: str | None = None,
    category: str | None = None,
    sku: str | None = None,
    max_price_vnd: int | None = None,
    min_room_area_m2: int | None = None,
    on: str | None = None,
) -> dict[str, Any]:
    """Search the product catalog.

    BTC tool name: catalog.search
    """
    products = _load_btc_products()
    results = []

    for product_id, product in products.items():
        if sku and product_id != sku:
            continue
        list_price = product.get("price_vnd") or product.get("list_price_vnd", 0)
        if max_price_vnd and list_price > max_price_vnd:
            continue
        if category and category.lower() not in product.get("category", "").lower():
            continue
        if query:
            q = query.lower()
            searchable = (
                product.get("name", "").lower()
                + product.get("category", "").lower()
                + " ".join(product.get("highlights", []))
                + " ".join(product.get("description", "").split())
            )
            alias_match = any(
                alias in q for alias, pid in PRODUCT_ALIASES.items() if pid == product_id
            )
            if q not in searchable and not alias_match:
                continue

        results.append({
            "sku": product_id,
            "name": product.get("name", ""),
            "list_price_vnd": list_price,
            "attributes": {"warranty_months": product.get("warranty_months")},
            "variants": product.get("variants", []),
        })

    return {"items": results}


def inventory_check(sku: str, on: str | None = None) -> dict[str, Any]:
    """Check inventory for a SKU on a given date.

    BTC tool name: inventory.check
    Uses inventory_timeline.json if available.
    """
    products = _load_btc_products()
    product = products.get(sku)
    if not product:
        return {"sku": sku, "in_stock": False, "qty": 0, "discontinued": True}

    stock = product.get("stock", {})
    qty = stock.get("quantity", 0)
    in_stock = stock.get("status") in ("in_stock",) and qty > 0

    return {
        "sku": sku,
        "in_stock": in_stock,
        "qty": qty,
        "restock_expected": stock.get("restock_expected"),
        "discontinued": stock.get("status") == "discontinued",
        "successor_sku": product.get("successor_sku"),
    }


def pricing_get_quote(
    sku: str,
    on: str | None = None,
    qty: int = 1,
    customer_phone: str | None = None,
    address: str | None = None,
    basket_skus: list | None = None,
) -> dict[str, Any]:
    """Calculate final price including applicable promotions.

    BTC tool name: pricing.get_quote
    """
    products = _load_btc_products()
    product = products.get(sku)
    if not product:
        return {"error": "product_not_found"}

    call_date = _today(on)
    list_price = product.get("price_vnd") or product.get("list_price_vnd", 0)
    best_discount = 0
    applied_promos: list[str] = []
    expired_promos: list[str] = []

    for promo in PROMOTIONS:
        if promo.get("product_id") != sku:
            continue
        expires = date.fromisoformat(promo["expires_at"])
        starts = date.fromisoformat(promo["starts_at"])
        if call_date > expires:
            expired_promos.append(promo["promotion_id"])
            continue
        if call_date < starts:
            continue
        disc = promo.get("discount_percent", 0)
        if disc > best_discount:
            best_discount = disc
            applied_promos = [promo["promotion_id"]]

    final_price = int(list_price * (1 - best_discount / 100))
    freeship = (final_price * qty) >= 1_500_000

    return {
        "list_price_vnd": list_price,
        "final_price_vnd": final_price,
        "applied_promos": applied_promos,
        "expired_promos": expired_promos,
        "ineligible_promos": [],
        "not_applied_exclusive": [],
        "freeship": freeship,
    }


TOOLS = {
    "catalog.search": catalog_search,
    "inventory.check": inventory_check,
    "pricing.get_quote": pricing_get_quote,
}
