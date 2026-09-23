# Synthetic Dataset Dimension Architecture

## 1. Dimension Architecture

A synthetic case should be constructed from independent dimensions rather than one hard-coded scenario.

```text
Case Study
× Persona
× Optional Difficult Scenario
× Journey Pattern
× Customer
× Business Ground Truth
× Expected Outcome
↓
Compatibility Rules
↓
Case Specification
↓
LLM generates Vietnamese transcript
```

| Dimension | Purpose |
|---|---|
| Case Study | What system-level problem is being tested? |
| Persona | What kind of customer is being simulated? |
| Difficult Scenario | What optional complication happens? |
| Journey Pattern | How many sessions, which channels, and in what order? |
| Customer | Who is the synthetic customer? |
| Business Ground Truth | Which products, prices, promotions, inventory, and policies are true? |
| Expected Outcome | What should the case end with? |
| Compatibility Rules | Is the sampled combination logically valid? |
| Case Specification | Final deterministic scenario given to the LLM |

**Principle:** input files decide **what** must happen; `case_specs.jsonl` records **exactly what** should happen; the LLM decides **how** it is naturally expressed in Vietnamese.

---

## 2. `case_studies.jsonl`

Defines the system-level problem being tested.

```json
{
  "case_id": "",
  "name": "",
  "title": "",
  "description": "",
  "problem": "",
  "trigger": "",
  "required_context": [],
  "baseline_behavior": [],
  "expected_behavior": [],
  "expected_outcome": ""
}
```

| Key | Type | Description |
|---|---|---|
| `case_id` | string | Unique case identifier |
| `name` | string | Machine-readable case name |
| `title` | string | Human-readable title |
| `description` | string | Short case description |
| `problem` | string | Core system/business problem |
| `trigger` | string | Event that activates the case |
| `required_context` | array[string] | Context required for the case |
| `baseline_behavior` | array[string] | Expected behavior without the harness |
| `expected_behavior` | array[string] | Desired harness behavior |
| `expected_outcome` | string | General successful result |

---

## 3. `personas.jsonl`

Defines the customer archetype.

```json
{
  "persona_id": "",
  "level": "",
  "name": "",
  "source_label": "",
  "description": "",
  "characteristics": [],
  "typical_behaviors": [],
  "typical_goal": "",
  "typical_state": ""
}
```

| Key | Type | Description |
|---|---|---|
| `persona_id` | string | Unique persona identifier |
| `level` | string | Requirement level such as M1/M2 |
| `name` | string | Machine-readable persona name |
| `source_label` | string | Original wording from the brief |
| `description` | string | Customer archetype description |
| `characteristics` | array[string] | Relatively stable characteristics |
| `typical_behaviors` | array[string] | Common observable behaviors |
| `typical_goal` | string | Typical customer objective |
| `typical_state` | string | Typical journey state |

---

## 4. `difficult_scenarios.jsonl`

Defines an optional complication.

```json
{
  "difficulty_id": "",
  "name": "",
  "source_label": "",
  "description": "",
  "requires_prior_state": false,
  "required_setup": [],
  "event": "",
  "expected_behavior": [],
  "forbidden_behavior": [],
  "evaluation_focus": []
}
```

| Key | Type | Description |
|---|---|---|
| `difficulty_id` | string | Unique difficult-scenario identifier |
| `name` | string | Machine-readable name |
| `source_label` | string | Original wording from the brief |
| `description` | string | Complication description |
| `requires_prior_state` | boolean | Whether previous state must exist |
| `required_setup` | array[string] | Preconditions required |
| `event` | string | Complication introduced in the case |
| `expected_behavior` | array[string] | Correct handling behavior |
| `forbidden_behavior` | array[string] | Behavior that must not occur |
| `evaluation_focus` | array[string] | Metrics/capabilities being tested |

---

## 5. `journey_patterns.jsonl`

Defines session count, channel sequence, timing, and handoffs.

```json
{
  "journey_pattern_id": "",
  "name": "",
  "description": "",
  "session_count": 0,
  "cross_channel": false,
  "sessions": [
    {
      "session_number": 0,
      "channel": "",
      "platform": "",
      "handler_type": "",
      "handler_change": false,
      "time_offset": ""
    }
  ]
}
```

| Key | Type | Description |
|---|---|---|
| `journey_pattern_id` | string | Unique journey-pattern identifier |
| `name` | string | Machine-readable pattern name |
| `description` | string | Interaction-flow description |
| `session_count` | integer | Number of sessions |
| `cross_channel` | boolean | Whether multiple channels are used |
| `sessions` | array[object] | Ordered session definitions |
| `sessions[].session_number` | integer | Session position |
| `sessions[].channel` | string | General channel type |
| `sessions[].platform` | string | Specific platform |
| `sessions[].handler_type` | string | Human/AI handler type |
| `sessions[].handler_change` | boolean | Whether handler changes |
| `sessions[].time_offset` | string | Relative time from previous session |

---

## 6. `customers.jsonl`

Defines controlled synthetic customer identities and profiles.

```json
{
  "customer_id": "",
  "name": "",
  "phone": "",
  "region": "",
  "addressing": "",
  "channel_identities": {},
  "profile": {},
  "preferences": {},
  "constraints": {}
}
```

| Key | Type | Description |
|---|---|---|
| `customer_id` | string | Internal synthetic customer ID |
| `name` | string | Synthetic customer name |
| `phone` | string | Synthetic phone number |
| `region` | string | Regional grouping |
| `addressing` | string | Vietnamese form of address |
| `channel_identities` | object | IDs used across phone/Zalo/Facebook/etc. |
| `profile` | object | Stable customer facts |
| `preferences` | object | Customer preferences |
| `constraints` | object | Budget or purchase constraints |

---

## 7. `products.jsonl`

Defines authoritative product ground truth.

```json
{
  "product_id": "",
  "sku": "",
  "category": "",
  "name": "",
  "brand": "",
  "description": "",
  "price": {},
  "specifications": {},
  "inventory": {},
  "active": true
}
```

| Key | Type | Description |
|---|---|---|
| `product_id` | string | Internal product identifier |
| `sku` | string | Business SKU |
| `category` | string | Product category |
| `name` | string | Product name |
| `brand` | string | Brand |
| `description` | string | Product description |
| `price` | object | Current authoritative price |
| `specifications` | object | Product attributes/specifications |
| `inventory` | object | Availability information |
| `active` | boolean | Whether product is currently active |

---

## 8. `promotions.jsonl`

Defines promotion ground truth and validity.

```json
{
  "promotion_id": "",
  "name": "",
  "description": "",
  "applicable_product_ids": [],
  "discount": {},
  "valid_from": "",
  "valid_until": "",
  "conditions": [],
  "active": true
}
```

| Key | Type | Description |
|---|---|---|
| `promotion_id` | string | Unique promotion identifier |
| `name` | string | Promotion name |
| `description` | string | Promotion details |
| `applicable_product_ids` | array[string] | Products covered |
| `discount` | object | Discount/value definition |
| `valid_from` | string | Start date |
| `valid_until` | string | Expiry date |
| `conditions` | array[string] | Additional conditions |
| `active` | boolean | Whether currently active |

---

## 9. `policies.jsonl`

Defines authoritative business policies.

```json
{
  "policy_id": "",
  "type": "",
  "title": "",
  "description": "",
  "rules": [
    {
      "condition": "",
      "rule": ""
    }
  ],
  "valid_from": "",
  "valid_until": "",
  "active": true
}
```

| Key | Type | Description |
|---|---|---|
| `policy_id` | string | Unique policy identifier |
| `type` | string | Policy category |
| `title` | string | Policy title |
| `description` | string | General description |
| `rules` | array[object] | Individual policy rules |
| `rules[].condition` | string | Rule condition |
| `rules[].rule` | string | Rule result/action |
| `valid_from` | string | Effective date |
| `valid_until` | string/null | Expiry date if applicable |
| `active` | boolean | Whether currently valid |

---

## 10. `compatibility_rules.jsonl`

Defines constraints between dimensions.

```json
{
  "rule_id": "",
  "name": "",
  "rule_type": "",
  "when": {},
  "require": {},
  "forbid": {},
  "action_on_failure": "",
  "reason": ""
}
```

| Key | Type | Description |
|---|---|---|
| `rule_id` | string | Unique rule identifier |
| `name` | string | Machine-readable rule name |
| `rule_type` | string | Constraint category |
| `when` | object | Condition that activates the rule |
| `require` | object | Conditions that must hold |
| `forbid` | object | Conditions that must not hold |
| `action_on_failure` | string | Generator action on invalid combination |
| `reason` | string | Human-readable explanation |

---

## 11. `case_specs.jsonl`

Generated intermediate file containing the final deterministic scenario.

```json
{
  "case_spec_id": "",
  "case_id": "",
  "persona_id": "",
  "difficulty_id": null,
  "journey_pattern_id": "",
  "customer_id": "",

  "business_context": {
    "product_ids": [],
    "promotion_ids": [],
    "policy_ids": []
  },

  "initial_state": {
    "known_facts": {},
    "unknown_facts": [],
    "customer_goal": "",
    "customer_state": ""
  },

  "sessions": [
    {
      "session_number": 0,
      "channel": "",
      "platform": "",
      "goal": "",
      "facts_to_establish": {},
      "facts_to_carry": [],
      "facts_to_confirm": [],
      "facts_to_change": {},
      "facts_to_invalidate": [],
      "must_not_ask": [],
      "event": null,
      "expected_actions": [],
      "expected_outcome": ""
    }
  ],

  "final_expected_state": {
    "customer_state": "",
    "purchase_state": "",
    "resolved_items": [],
    "unresolved_items": []
  },

  "evaluation_ground_truth": {
    "must_carry_over": [],
    "must_not_ask": [],
    "must_confirm": [],
    "must_not_claim": [],
    "required_actions": [],
    "forbidden_actions": [],
    "success_conditions": []
  }
}
```

| Key | Type | Description |
|---|---|---|
| `case_spec_id` | string | Unique concrete case ID |
| `case_id` | string | Selected case study |
| `persona_id` | string | Selected persona |
| `difficulty_id` | string/null | Optional complication |
| `journey_pattern_id` | string | Selected journey structure |
| `customer_id` | string | Customer used in the case |
| `business_context` | object | Relevant business-data references |
| `initial_state` | object | Ground truth before the first session |
| `sessions` | array[object] | Ordered session specifications |
| `final_expected_state` | object | Ground truth after all sessions |
| `evaluation_ground_truth` | object | Machine-checkable expectations |

### Important session keys

| Key | Type | Description |
|---|---|---|
| `facts_to_establish` | object | Facts that must become known |
| `facts_to_carry` | array[string] | Facts carried from earlier sessions |
| `facts_to_confirm` | array[string] | Existing facts requiring confirmation |
| `facts_to_change` | object | Facts whose active value changes |
| `facts_to_invalidate` | array[string] | Old facts that should no longer be active |
| `must_not_ask` | array[string] | Known facts the agent must not re-ask openly |
| `event` | string/null | Optional difficult event |
| `expected_actions` | array[string] | Required actions |
| `expected_outcome` | string | Expected session result |

### Evaluation keys

| Key | Type | Description |
|---|---|---|
| `must_carry_over` | array[string] | Context Carryover ground truth |
| `must_not_ask` | array[string] | Repeat-Question ground truth |
| `must_confirm` | array[string] | Facts that should be confirmed |
| `must_not_claim` | array[string] | Unsupported claims that are forbidden |
| `required_actions` | array[string] | Actions required for success |
| `forbidden_actions` | array[string] | Actions that indicate failure |
| `success_conditions` | array | Machine-checkable task-success conditions |

---

## Final Pipeline

```text
Input Definition Files
↓
Compatibility Validation
↓
case_specs.jsonl
↓
LLM Conversation Generation
↓
Vietnamese Multi-session / Multi-channel Transcripts
```
