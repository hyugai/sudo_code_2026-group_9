"""CRM domain tools — crm.get_customer"""

from __future__ import annotations

import json
from typing import Any


def _load_crm_seed() -> dict[str, Any]:
    """Try to load CRM seed from BTC data directory."""
    for path in [
        "dataset/BTC-Data-Vong1-TEAMS/catalog/crm_seed.json",
        "BTC-Data-Vong1-TEAMS/catalog/crm_seed.json",
    ]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            continue

    # Fallback mock data
    return {
        "customers": [
            {
                "customer_id": "CRM-001",
                "name": "Hoa",
                "honorific": "chị",
                "phone": "0984726714",
                "identities": {"phone": "0984726714"},
                "orders": [],
                "region": "HN",
            }
        ]
    }


def crm_get_customer(
    phone: str | None = None,
    zalo_id: str | None = None,
    fb_id: str | None = None,
    on: str | None = None,
) -> dict[str, Any]:
    """Look up a customer by phone or channel identity.

    BTC tool name: crm.get_customer
    """
    crm_data = _load_crm_seed()
    customers = crm_data.get("customers", [])

    # Detect ambiguous (2+ profiles share the same phone)
    matches = [c for c in customers if phone and c.get("phone") == phone]
    if len(matches) > 1:
        return {"found": True, "ambiguous": True, "candidates": matches, "orders": [], "sessions": []}
    if len(matches) == 1:
        return {"found": True, "ambiguous": False, **matches[0], "sessions": []}

    # Zalo / FB fallback
    for customer in customers:
        identities = customer.get("identities", {})
        if zalo_id and identities.get("zalo") == zalo_id:
            return {"found": True, "ambiguous": False, **customer, "sessions": []}
        if fb_id and identities.get("fb") == fb_id:
            return {"found": True, "ambiguous": False, **customer, "sessions": []}

    return {"found": False, "ambiguous": False, "orders": [], "sessions": []}


TOOLS = {
    "crm.get_customer": crm_get_customer,
}
