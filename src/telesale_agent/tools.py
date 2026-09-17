"""Mock business tools called by the demo agent."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Awaitable, Callable

from telesale_agent.adapters.mock.mock_data import (
    PRODUCTS,
    PROMOTIONS,
    RETURN_POLICY,
    SHIPPING_POLICY,
)


ToolOutput = dict[str, Any]
ToolHandler = Callable[[dict[str, Any]], Awaitable[ToolOutput]]


class MockToolbox:
    """Small allow-listed tool registry backed by fictional local data."""

    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {
            "get_product": self._get_product,
            "get_price": self._get_price,
            "check_inventory": self._check_inventory,
            "get_return_policy": self._get_return_policy,
            "get_warranty_policy": self._get_warranty_policy,
            "get_shipping_policy": self._get_shipping_policy,
            "get_active_promotions": self._get_active_promotions,
        }

    @property
    def allowed_tools(self) -> frozenset[str]:
        return frozenset(self._handlers)

    async def execute(self, name: str, arguments: dict[str, Any]) -> ToolOutput:
        handler = self._handlers.get(name)
        if handler is None:
            raise ValueError(f"unknown tool: {name}")
        return await handler(arguments)

    @staticmethod
    def _product(product_id: str | None) -> dict[str, Any]:
        product = PRODUCTS.get(product_id or "")
        if product is None:
            raise ValueError(f"product not found: {product_id}")
        return product

    async def _get_product(self, arguments: dict[str, Any]) -> ToolOutput:
        return deepcopy(self._product(arguments.get("product_id")))

    async def _get_price(self, arguments: dict[str, Any]) -> ToolOutput:
        product = self._product(arguments.get("product_id"))
        return {
            "product_id": product["product_id"],
            "name": product["name"],
            "price_vnd": product["price_vnd"],
        }

    async def _check_inventory(self, arguments: dict[str, Any]) -> ToolOutput:
        product = self._product(arguments.get("product_id"))
        return {
            "product_id": product["product_id"],
            "name": product["name"],
            "stock": deepcopy(product["stock"]),
        }

    async def _get_return_policy(self, arguments: dict[str, Any]) -> ToolOutput:
        return deepcopy(RETURN_POLICY)

    async def _get_warranty_policy(self, arguments: dict[str, Any]) -> ToolOutput:
        product = self._product(arguments.get("product_id"))
        return {
            "product_id": product["product_id"],
            "name": product["name"],
            "warranty_months": product["warranty_months"],
            "requirements": ["Mã đơn hàng hoặc số sê-ri", "Kiểm tra tình trạng"],
        }

    async def _get_shipping_policy(self, arguments: dict[str, Any]) -> ToolOutput:
        return deepcopy(SHIPPING_POLICY)

    async def _get_active_promotions(self, arguments: dict[str, Any]) -> ToolOutput:
        product_id = arguments.get("product_id")
        matches = [
            deepcopy(item)
            for item in PROMOTIONS
            if item["product_id"] == product_id and item["status"] == "active"
        ]
        return {"product_id": product_id, "promotions": matches}

