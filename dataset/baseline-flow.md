``` mermaid
flowchart LR
    A[Customer Contacts]
    --> B[Agent Collects<br/>Customer Information]
    --> C[Consult / Support]
    --> D{Resolved?}

    D -->|Yes| E[Purchase / Resolution]
    D -->|No| F[Session Ends]

    F --> G[Customer Returns]
    G --> H["⚠ PREVIOUS CONTEXT<br/>NOT AVAILABLE"]
    H --> B

    style H fill:#ffdddd,stroke:#cc0000,stroke-width:4px,color:#990000
```

## Catalog

| Requirement | M1 | M2 |
| --- | --- | --- |
| **Catalog size** | **≥ 30 SKUs** | **≥ 100 SKUs** |
| **Industries** | 1 industry | 3 industries |
| Product information | Required | Required, larger/more diverse |
| Price information | Required | Required |
| Promotion information | Required | Required, including expiration/validity handling |
| Inventory / availability | Required | Required, including out-of-stock cases |

## Policy

| Requirement | M1 | M2 |
| --- | --- | --- |
| Shipping information | Required | Required |
| Return / exchange policy | Required | Required |
| Product / business policy | Required | Required |
| Policy document count | **Not specified** | **Not specified** |

> catalog.json

Product
├── sku
├── industry
├── category
├── name
├── brand
├── description
├── price
│   ├── amount
│   └── currency
├── specifications {}
├── inventory
│   ├── quantity
│   ├── status
│   └── updated_at
├── promotion_ids []
└── active

> promotions.json

Promotion
├── promotion_id
├── name
├── description
├── discount_type
├── discount_value
├── valid_from
├── valid_until
└── active
