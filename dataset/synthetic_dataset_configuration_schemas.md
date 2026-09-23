# Synthetic Dataset Configuration Schemas

## How a Synthetic Case Is Constructed

A single synthetic case should not be defined by only one label. It is constructed from several independent dimensions that describe different parts of the situation.

The core structure is:

```text
Synthetic Case
=
Case Study
× Persona
× Optional Difficult Scenario
× Interaction Configuration
× Expected Outcome
```

Each dimension has a different role:

| Dimension | Question it answers | Example |
|---|---|---|
| `Case Study` | What system-level problem is being tested? | `session_continuity` |
| `Persona` | What kind of customer is being simulated? | `hesitant_family_approval` |
| `Difficult Scenario` | What optional complication is added? | `expired_promotion` |
| `Interaction Configuration` | How does the case unfold operationally? | `2 sessions`, `voice → chat`, `2 different agents` |
| `Expected Outcome` | What should the interaction end with? | `callback_scheduled`, `closed_won`, `resolved`, `escalated` |

These dimensions should be kept separate because they describe different aspects of the same case.

For example:

```json
{
  "case_id": "CASE_01",
  "persona_id": "P01",
  "difficulty_id": "D03",
  "interaction_configuration": {
    "session_count": 2,
    "channels": ["voice", "voice"]
  },
  "expected_outcome": "callback_scheduled"
}
```

This means:

```text
System problem:
    Returning-customer session continuity

Customer type:
    Hesitant customer who needs family approval

Optional complication:
    The previously offered promotion has expired

Interaction shape:
    Two voice sessions

Expected ending:
    Follow-up or another valid business outcome
```

The important distinction is:

```text
Case Study
    = system problem

Persona
    = customer archetype

Difficult Scenario
    = optional complication

Interaction Configuration
    = operational structure of the journey

Expected Outcome
    = final business/service state
```

`Difficult Scenario` is optional for an individual generated case. A normal case can therefore be:

```json
{
  "case_id": "CASE_01",
  "persona_id": "P01",
  "difficulty_id": null
}
```

while a harder variation of the same case can be:

```json
{
  "case_id": "CASE_01",
  "persona_id": "P01",
  "difficulty_id": "D03"
}
```

Not every possible combination is logically valid. Therefore, after sampling the dimensions, the generator should apply `compatibility_rules.jsonl`.

The recommended generation process is:

```text
Select Case Study
        ↓
Select Persona
        ↓
Optionally select Difficult Scenario
        ↓
Select interaction configuration
        ↓
Apply compatibility rules
        ↓
Build deterministic case specification
        ↓
Generate natural-language conversation
```

This design keeps the synthetic-data generator controllable, reusable, and suitable for producing both normal and difficult multi-session cases.

---

This document defines four JSONL configuration files for synthetic dataset generation:

1. `case_studies.jsonl`
2. `personas.jsonl`
3. `difficult_scenarios.jsonl`
4. `compatibility_rules.jsonl`

The first three correspond to concepts explicitly present in the project brief. `compatibility_rules.jsonl` is a derived generation-control layer used to prevent logically invalid synthetic cases.

---

## 1. `case_studies.jsonl`

### General format

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

### Key explanation

| Key | Type | Description | Example |
|---|---|---|---|
| `case_id` | string | Unique identifier for the case study | `"CASE_01"` |
| `name` | string | Short machine-readable case name | `"session_continuity"` |
| `title` | string | Human-readable case title | `"Returning customer continuity"` |
| `description` | string | Concise explanation of the case | `"Customer returns after a previous interaction"` |
| `problem` | string | Core business/system problem being tested | `"Previous session context is lost"` |
| `trigger` | string | Event that activates the case | `"Customer contacts the business again"` |
| `required_context` | array[string] | Information/state that must exist for the case to make sense | `["previous_interaction", "customer_identity"]` |
| `baseline_behavior` | array[string] | Expected behavior of the system without the agent harness | `["repeat_questions", "lose_context"]` |
| `expected_behavior` | array[string] | Behavior expected from the AI Agent Harness | `["retrieve_context", "continue_previous_session"]` |
| `expected_outcome` | string | General successful result of handling the case | `"continuous_customer_context"` |

### Concept

```text
Case Study
=
What system-level problem are we testing?
```

Examples from the brief:

```text
session continuity
cross-channel continuity
handoff continuity
continuous improvement
```

---

## 2. `personas.jsonl`

### General format

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

### Key explanation

| Key | Type | Description | Example |
|---|---|---|---|
| `persona_id` | string | Unique identifier for the persona | `"P01"` |
| `level` | string | Requirement level from the brief | `"M1"` |
| `name` | string | Machine-readable persona name | `"hesitant_family_approval"` |
| `source_label` | string | Original persona wording from the brief | `"khách do dự cần hỏi người nhà"` |
| `description` | string | General description of this customer type | `"Customer needs family approval before deciding"` |
| `characteristics` | array[string] | Relatively stable behavioral characteristics | `["hesitant", "family_influenced"]` |
| `typical_behaviors` | array[string] | Actions commonly shown by this persona | `["asks_questions", "delays_decision"]` |
| `typical_goal` | string | What the customer is generally trying to achieve | `"evaluate_purchase"` |
| `typical_state` | string | Typical state during the customer journey | `"decision_pending"` |

### Concept

```text
Persona
=
What kind of customer are we simulating?
```

Examples from the brief:

```text
hesitant customer
price-comparison customer
post-purchase customer
high-engagement non-buyer
impatient repeat customer
```

---

## 3. `difficult_scenarios.jsonl`

### General format

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

### Key explanation

| Key | Type | Description | Example |
|---|---|---|---|
| `difficulty_id` | string | Unique identifier for the difficult scenario | `"D03"` |
| `name` | string | Machine-readable name | `"expired_promotion"` |
| `source_label` | string | Original wording from the brief | `"khách đòi áp khuyến mãi đã hết hạn"` |
| `description` | string | Description of the complication | `"Customer requests a promotion that has already expired"` |
| `requires_prior_state` | boolean | Whether an earlier interaction/fact must exist | `true` |
| `required_setup` | array[string] | Conditions that must be created before the complication occurs | `["promotion_previously_active"]` |
| `event` | string | Concrete event introduced into the case | `"customer_requests_expired_promotion"` |
| `expected_behavior` | array[string] | Correct handling expected from the harness | `["detect_expiry", "retrieve_current_offer"]` |
| `forbidden_behavior` | array[string] | Behaviors that would make the handling incorrect | `["claim_expired_promotion_is_active"]` |
| `evaluation_focus` | array[string] | Metrics/capabilities this scenario is intended to test | `["hallucination_prevention", "temporal_validity"]` |

### Concept

```text
Difficult Scenario
=
What optional complication happens during the case?
```

Examples from the brief:

```text
change_of_mind
conflict_with_previous_session
expired_promotion
outside_documentation
```

---

## 4. `compatibility_rules.jsonl`

This file controls which combinations may be generated.

### General format

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

### Key explanation

| Key | Type | Description | Example |
|---|---|---|---|
| `rule_id` | string | Unique rule identifier | `"CR03"` |
| `name` | string | Machine-readable rule name | `"expired_promotion_requires_history"` |
| `rule_type` | string | Category of constraint | `"temporal_requirement"` |
| `when` | object | Condition under which the rule applies | `{"difficulty_id":"D03"}` |
| `require` | object | Conditions that must be true | `{"minimum_sessions":2}` |
| `forbid` | object | Conditions that must not occur | `{"promotion_missing":true}` |
| `action_on_failure` | string | What generator should do when rule fails | `"resample"` |
| `reason` | string | Human-readable explanation of why the rule exists | `"An expired promotion requires a previously valid promotion"` |

### Concept

```text
Compatibility Rule
=
Can this combination produce a logically valid case?
```

Example:

```json
{
  "rule_id": "CR01",
  "name": "conflict_requires_previous_session",
  "rule_type": "session_requirement",
  "when": {
    "difficulty_id": "D02"
  },
  "require": {
    "minimum_sessions": 2,
    "previous_fact_exists": true
  },
  "forbid": {},
  "action_on_failure": "resample",
  "reason": "A conflict with a previous session cannot exist without a previous fact"
}
```

---

# Recommended relationship between the four files

```text
case_studies.jsonl
        ↓
      CASE

personas.jsonl
        ↓
     PERSONA

difficult_scenarios.jsonl
        ↓
 OPTIONAL COMPLICATION

        ↓
Case × Persona × Difficulty
        ↓
compatibility_rules.jsonl
        ↓
valid combination
        ↓
Concrete Case Specification
        ↓
LLM Conversation Generation
```

A generated configuration might initially be:

```json
{
  "case_id": "CASE_01",
  "persona_id": "P01",
  "difficulty_id": "D03"
}
```

The compatibility layer can then enrich and validate it:

```json
{
  "case_id": "CASE_01",
  "persona_id": "P01",
  "difficulty_id": "D03",
  "session_count": 2,
  "prior_promotion_required": true,
  "promotion_must_expire_before_session": 2
}
```

That validated combination should feed into the case specification generator, rather than sending the three labels directly to the LLM.
