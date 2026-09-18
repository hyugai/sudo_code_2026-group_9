# Phase 2 — Finalize Database Schema

## Status

| Item | Value |
|---|---|
| Status | ✅ Completed |
| Phase | 2 |
| Name | Finalize Database Schema |

## Objective

Define a simple relational database structure that supports:

- Policy Dataset
- Catalog Dataset
- Transcript Dataset
- Multi-session customer journeys
- Multi-channel interactions
- Sessions that may involve more than one product

## Database Overview

| Logical Dataset | Tables |
|---|---|
| Policy | `policies` |
| Catalog | `catalog` |
| Transcript | `users`, `sessions`, `messages` |
| Relationship | `session_products` |

## Relationship Overview

```text
Users
  |
  | 1:N
  v
Sessions
  |
  | 1:N
  v
Messages

Sessions
  |
  | N:M
  v
Catalog
  ^
  |
session_products

Policies
  |
  └── independent grounding source
```

---

## 1. `users`

Stores customer identity, persona, regional information, and long-term profile data.

| Column | Type | Key | Nullable | Default | Description |
|---|---|---|---|---|---|
| `user_id` | `VARCHAR(30)` | PK | No | None | Unique customer identifier |
| `name` | `VARCHAR(150)` |  | No | None | Customer name |
| `phone` | `VARCHAR(30)` |  | Yes | `NULL` | Synthetic or masked phone number |
| `region` | `VARCHAR(30)` |  | Yes | `NULL` | Customer region |
| `persona` | `VARCHAR(60)` |  | Yes | `NULL` | Main customer behavior group |
| `profile` | `JSONB` |  | No | `{}` | Flexible long-term customer information |

---

## 2. `catalog`

Stores product information and acts as the main product knowledge source.

| Column | Type | Key | Nullable | Default | Description |
|---|---|---|---|---|---|
| `product_id` | `VARCHAR(30)` | PK | No | None | Unique product identifier |
| `category` | `VARCHAR(100)` |  | No | None | Product category |
| `name` | `VARCHAR(255)` |  | No | None | Product name |
| `brand` | `VARCHAR(100)` |  | Yes | `NULL` | Product brand |
| `price` | `BIGINT` |  | No | None | Product price in VND |
| `stock` | `INTEGER` |  | No | `0` | Available stock quantity |
| `specifications` | `JSONB` |  | No | `{}` | Flexible product-specific specifications |

### Recommended Constraints

```text
price >= 0
stock >= 0
```

---

## 3. `policies`

Stores business rules independently from product information.

| Column | Type | Key | Nullable | Default | Description |
|---|---|---|---|---|---|
| `policy_id` | `VARCHAR(30)` | PK | No | None | Unique policy identifier |
| `category` | `VARCHAR(60)` |  | No | None | Policy category |
| `name` | `VARCHAR(255)` |  | No | None | Human-readable policy name |
| `rules` | `JSONB` |  | No | `{}` | Structured policy rules |

### Suggested Policy Categories

```text
ordering
payment
shipping
return
warranty
promotion
privacy
customer_support
Rules for communicating with customers.
```

---

## 4. `sessions`

Represents one complete interaction between a user and the business.

A single user may have multiple sessions across different channels and platforms.

| Column | Type | Key | Nullable | Default | Description |
|---|---|---|---|---|---|
| `session_id` | `VARCHAR(30)` | PK | No | None | Unique session identifier |
| `user_id` | `VARCHAR(30)` | FK → `users.user_id` | No | None | Customer associated with the session |
| `channel` | `VARCHAR(30)` |  | No | None | General communication type |
| `platform` | `VARCHAR(50)` |  | No | None | Communication platform |
| `timestamp` | `TIMESTAMPTZ` |  | No | `CURRENT_TIMESTAMP` | Session start time |
| `summary` | `TEXT` |  | Yes | `NULL` | Short episodic-memory summary |
| `outcome` | `VARCHAR(40)` |  | No | `ongoing` | Current or final session result |

### Suggested Values

| Field | Values |
|---|---|
| `channel` | `voice`, `messaging` |
| `platform` | `phone`, `zalo`, `facebook_messenger`, `website_chat` |
| `outcome` | `ongoing`, `callback_scheduled`, `closed_won`, `rejected`, `resolved`, `escalated` |

---

## 5. `messages`

Stores individual conversation turns within a session.

| Column | Type | Key | Nullable | Default | Description |
|---|---|---|---|---|---|
| `message_id` | `VARCHAR(40)` | PK | No | None | Unique message identifier |
| `session_id` | `VARCHAR(30)` | FK → `sessions.session_id` | No | None | Session containing the message |
| `sender` | `VARCHAR(20)` |  | No | None | Message sender |
| `type` | `VARCHAR(20)` |  | No | `text` | Message type |
| `text` | `TEXT` |  | Yes | `NULL` | Message content or transcript |
| `sequence_no` | `INTEGER` |  | No | None | Message order inside the session |

### Suggested Values

| Field | Values |
|---|---|
| `sender` | `customer`, `agent` |
| `type` | `text`, `voice`, `image`, `file` |

### Recommended Constraint

```text
UNIQUE(session_id, sequence_no)
```

---

## 6. `session_products`

Links sessions with the products discussed during the interaction.

This table is required because one session may involve multiple products.

| Column | Type | Key | Nullable | Default | Description |
|---|---|---|---|---|---|
| `session_id` | `VARCHAR(30)` | FK → `sessions.session_id` | No | None | Session in which the product was discussed |
| `product_id` | `VARCHAR(30)` | FK → `catalog.product_id` | No | None | Product discussed in the session |

### Primary Key

```text
PRIMARY KEY (session_id, product_id)
```

### Example

```text
session_id | product_id
-----------|-----------
SES_001    | ELEC_001
SES_001    | ELEC_005
SES_002    | ELEC_001
```

This means:

- `SES_001` discusses two products.
- `SES_002` discusses one product.

---

## Relationship Summary

| Relationship | Type | Purpose |
|---|---|---|
| `users` → `sessions` | 1:N | One customer can have multiple interactions |
| `sessions` → `messages` | 1:N | One session contains multiple conversation turns |
| `sessions` ↔ `catalog` | N:M | One session may discuss multiple products |
| `session_products` | Junction table | Connects sessions with catalog products |
| `policies` | Independent grounding source | Provides business rules used by the agent |

---

## Design Principles

| Principle | Requirement |
|---|---|
| User separation | User information must not be duplicated inside transcript content |
| Transcript structure | Transcript is represented by `sessions` + `messages` |
| Product grounding | Product facts come from `catalog` |
| Policy grounding | Business rules come from `policies` |
| Multi-product support | Use `session_products` instead of a single `product_id` in `sessions` |
| Multi-session | Same `user_id` can appear in multiple sessions |
| Multi-channel | Same user may move across phone, Zalo, Facebook Messenger, or website chat |
| Flexible fields | JSONB is used only for variable structures such as profile, specifications, and rules |
| Message order | `sequence_no` reconstructs the original conversation order |

---

## Why `session_products` Is Needed

Without `session_products`, a session could only directly reference one product.

Example conversation:

```text
"Tai nghe Auralite H5 với NovaFit S3 thì cái nào phù hợp hơn?"
```

This interaction contains more than one product.

Using a junction table allows:

```text
SES_001 → ELEC_001
SES_001 → ELEC_005
```

without duplicating session data.

---

## Scope Decision for Policies

A separate `session_policies` table is **not required in Phase 2**.

Policies remain an independent grounding source.

A `session_policies` relationship table should only be added later if the project needs to track or evaluate exactly which policy was retrieved or applied during each session.

---

## Completion Criteria

| Check | Expected Result |
|---|---|
| Core tables defined | ✅ |
| Primary keys defined | ✅ |
| Foreign keys defined | ✅ |
| User data separated from transcript content | ✅ |
| Transcript split into Sessions + Messages | ✅ |
| Multi-product sessions supported | ✅ |
| Multi-channel fields defined | ✅ |
| Catalog separated from Policy | ✅ |
| Ready for Policy and Catalog generation | ✅ |

## Final Schema

```text
users
-----
user_id PK
name
phone
region
persona
profile


catalog
-------
product_id PK
category
name
brand
price
stock
specifications


policies
--------
policy_id PK
category
name
rules


sessions
--------
session_id PK
user_id FK
channel
platform
timestamp
summary
outcome


messages
--------
message_id PK
session_id FK
sender
type
text
sequence_no


session_products
----------------
session_id FK
product_id FK

PK (session_id, product_id)
```
