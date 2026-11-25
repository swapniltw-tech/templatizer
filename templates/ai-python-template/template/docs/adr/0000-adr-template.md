---
status: proposed        # proposed | accepted | rejected | deprecated | superseded by NNNN
date: YYYY-MM-DD
decision-makers: <roles>
consulted: <roles>
informed: <roles>
---

# <Short title: problem and chosen solution>

<!-- Template implements STR-025, ARC-030, ARC-033 (MADR 4.0.0 headings, doc 03).
VERIFY: MADR front matter field names against the MADR project site. Copy to NNNN-short-title.md.
Agents may draft ADRs but MUST NOT set status to accepted (ARC-031). -->

## Context and Problem Statement
<Two to five sentences. Include the regulatory or risk context if any.>

## Decision Drivers
- <driver, for example data class, latency, cost, autonomy rung>

## Considered Options
- <Option 1: simplest option or do nothing>
- <Option 2>

## Decision Outcome
Chosen option: "<option>", because <reason tied to drivers>.

### Consequences
- Good: <...>
- Bad: <...>

### Confirmation
<How compliance is checked: fitness test name, eval id, dashboard, review.>

## Pros and Cons of the Options
### <Option 1>
- Good, because <...>
- Bad, because <...>

## More Information
<Links to rules, use-case catalog entry, related ADRs, waiver id if any.>
