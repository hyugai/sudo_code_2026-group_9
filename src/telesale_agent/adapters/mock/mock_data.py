"""Fictional electronics data used by the local agent-harness demo."""

from __future__ import annotations

from typing import Any


PRODUCTS: dict[str, dict[str, Any]] = {
    "ELEC_001": {
        "product_id": "ELEC_001",
        "name": "Auralite H5 Wireless Headphones",
        "category": "tai nghe không dây",
        "price_vnd": 1_890_000,
        "stock": {"status": "in_stock", "quantity": 24},
        "warranty_months": 12,
        "highlights": ["Bluetooth 5.3", "chống ồn chủ động", "pin 35 giờ"],
    },
    "ELEC_002": {
        "product_id": "ELEC_002",
        "name": "KeyForge K87 Mechanical Keyboard",
        "category": "bàn phím cơ",
        "price_vnd": 1_490_000,
        "stock": {"status": "in_stock", "quantity": 18},
        "warranty_months": 12,
        "highlights": ["layout TKL", "hot-swap", "RGB"],
    },
    "ELEC_003": {
        "product_id": "ELEC_003",
        "name": "Vector M2 Pro Wireless Mouse",
        "category": "chuột máy tính",
        "price_vnd": 990_000,
        "stock": {"status": "low_stock", "quantity": 3},
        "warranty_months": 12,
        "highlights": ["kết nối 2.4 GHz", "Bluetooth", "cảm biến 20.000 DPI"],
    },
    "ELEC_004": {
        "product_id": "ELEC_004",
        "name": "VoltGo P20 20,000mAh Power Bank",
        "category": "pin sạc dự phòng",
        "price_vnd": 790_000,
        "stock": {"status": "in_stock", "quantity": 31},
        "warranty_months": 12,
        "highlights": ["20.000 mAh", "sạc nhanh USB-C", "màn hình dung lượng"],
    },
    "ELEC_005": {
        "product_id": "ELEC_005",
        "name": "NovaFit S3 Smartwatch",
        "category": "đồng hồ thông minh",
        "price_vnd": 2_290_000,
        "stock": {"status": "in_stock", "quantity": 11},
        "warranty_months": 12,
        "highlights": ["AMOLED", "GPS", "theo dõi nhịp tim"],
    },
    "ELEC_006": {
        "product_id": "ELEC_006",
        "name": "NetCore AX3000 Wi-Fi 6 Router",
        "category": "bộ định tuyến Wi-Fi",
        "price_vnd": 1_590_000,
        "stock": {"status": "in_stock", "quantity": 9},
        "warranty_months": 24,
        "highlights": ["Wi-Fi 6", "tốc độ AX3000", "4 cổng Gigabit"],
    },
    "ELEC_007": {
        "product_id": "ELEC_007",
        "name": "FlashCore X1 Portable SSD 1TB",
        "category": "ổ SSD di động",
        "price_vnd": 2_190_000,
        "stock": {"status": "in_stock", "quantity": 7},
        "warranty_months": 36,
        "highlights": ["dung lượng 1 TB", "USB-C", "đọc tối đa 1.050 MB/s"],
    },
    "ELEC_008": {
        "product_id": "ELEC_008",
        "name": "ChargeMax GaN 65W USB-C Charger",
        "category": "bộ sạc USB-C",
        "price_vnd": 690_000,
        "stock": {"status": "out_of_stock", "quantity": 0},
        "warranty_months": 12,
        "highlights": ["GaN 65 W", "2 cổng USB-C", "1 cổng USB-A"],
    },
}


PRODUCT_ALIASES: dict[str, str] = {
    "auralite": "ELEC_001",
    "h5": "ELEC_001",
    "tai nghe": "ELEC_001",
    "keyforge": "ELEC_002",
    "k87": "ELEC_002",
    "bàn phím": "ELEC_002",
    "vector m2": "ELEC_003",
    "chuột": "ELEC_003",
    "voltgo": "ELEC_004",
    "pin sạc": "ELEC_004",
    "novafit": "ELEC_005",
    "đồng hồ": "ELEC_005",
    "netcore": "ELEC_006",
    "router": "ELEC_006",
    "flashcore": "ELEC_007",
    "ssd": "ELEC_007",
    "chargemax": "ELEC_008",
    "sạc 65w": "ELEC_008",
    "bộ sạc": "ELEC_008",
}


RETURN_POLICY: dict[str, Any] = {
    "policy_id": "RETURN_ELECTRONICS_001",
    "change_of_mind_days": 7,
    "technical_defect_days": 30,
    "conditions": [
        "Có hóa đơn hoặc mã đơn hàng",
        "Sản phẩm còn đầy đủ phụ kiện",
        "Sản phẩm không hư hỏng do người sử dụng",
    ],
    "note": "Sản phẩm lỗi kỹ thuật cần được kiểm tra trước khi đổi tương đương.",
}


SHIPPING_POLICY: dict[str, Any] = {
    "policy_id": "SHIPPING_STANDARD_001",
    "standard_days": "2-4 ngày làm việc",
    "standard_fee_vnd": 30_000,
    "free_shipping_from_vnd": 1_500_000,
    "note": "Khu vực xa có thể phát sinh phụ phí và thời gian giao lâu hơn.",
}


PROMOTIONS: list[dict[str, Any]] = [
    {
        "promotion_id": "PROMO_H5_10",
        "product_id": "ELEC_001",
        "discount_percent": 10,
        "starts_at": "2026-01-01",
        "expires_at": "2099-12-31",
        "status": "active",
    },
    {
        "promotion_id": "PROMO_H5_20_OLD",
        "product_id": "ELEC_001",
        "discount_percent": 20,
        "starts_at": "2025-01-01",
        "expires_at": "2025-03-31",
        "status": "expired",
    },
    {
        "promotion_id": "PROMO_SSD_08",
        "product_id": "ELEC_007",
        "discount_percent": 8,
        "starts_at": "2026-01-01",
        "expires_at": "2099-12-31",
        "status": "active",
    },
]

