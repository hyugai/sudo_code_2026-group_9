# Phase 1 — Define Domain & Data Scope

## Overview

| Item | Detail |
|---|---|
| **Status** | ◐ In Progress |
| **Objective** | Define the industry and data scope for the project. |

## Status Legend

| Symbol | Status |
|---|---|
| `✓` | Done |
| `◐` | In Progress |
| `○` | Not Started |
| `✗` | Blocked |

## Requirements

| Requirement | Status |
|---|:---:|
| Industry | ✓ |
| Business Context | ✓ |
| Channels | ✓ |
| Datasets | ✓ |
| Product Scope | ◐ In Progress |
| Data Source | ◐ In Progress |
| Language | ✓ |
| Multi-session | ✓ |
| Multi-channel | ◐ In Progress |
| PII | ◐ In Progress |

### 1. Industry


```text
Consumer Electronics & Accessories
```

Used consistently across Policy, Catalog, and Transcript data.

### 2. Business Context


```text
Retail / e-commerce consultation and customer support
```

| Context | Available |
|---|:---:|
| Sales | ✓ |
| Product Q/A | ✓ |
| Follow-up | ✓ |
| Returns | ✓ |
| Warranty | ✓ |
| Complaints | ✓ |

### 3. Channels


```text
Phone
Zalo
Facebook Messenger
Website chat
```

### 4. Datasets


| Dataset | Purpose |
|---|---|
| Policy | Business rules |
| Catalog | Product information |
| Transcript | Customer interactions |

### 5. Product Scope


| Dataset | Categories |
|---|:---:|
| Mock | ? |
| M1 | ? |
| M2 | ? |

Target:

```text
30–50 products
```

Main categories:

```text
...
```

### 6. Data Source


| Source | Proportion (%) |
|---|:---:|
| Existing/reference data | ? |
| AI-generated synthetic data | ? |
| Manually defined synthetic data | ? |


### 7. Language


```text
Vietnamese
```

Use natural sales and customer-support language.

### 8. Multi-session


One user can have multiple sessions.

```text
User
├── Session 1
├── Session 2
└── Session 3
```

### 9. Multi-channel


The same user can continue across different platforms.

```text
Phone → Zalo → Facebook Messenger
```

Q/A: How many channels are sufficient enough for M1 and M2 ?
| | Min | Max |
|---|:---:|:---:|
| M1 | ? | ? |
| M2 | ? | ? |

### 10. PII


Personal information must be:

```text
Synthetic or masked
```
