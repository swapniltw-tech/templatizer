# Exceptions and Waivers

> **Owner:** Head of Engineering Standards (with AI Governance) · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** none (internal standard); regulatory context in [12-governance-and-compliance.md](./12-governance-and-compliance.md)

## Purpose
Define the only way to deviate from a `MUST` rule. No silent deviations. A waiver is a time-boxed, approved, recorded exception with compensating controls. `SHOULD` rules may be departed from with a recorded reason in the MR (WVR-002) and do not need a waiver. `ASSUMPTION:` approver titles below are placeholders until the internal governance structure is shared (F1).

## Approvers by risk tier
Tiers are defined in [12-governance-and-compliance.md](./12-governance-and-compliance.md).

| System tier | Approvers (all required) | Maximum duration |
|---|---|---|
| Tier 3 (low) | Service owner and Engineering lead | 180 days |
| Tier 2 (medium) | Service owner, Engineering lead, Application Security (for security rules) or Privacy Office (for data rules) | 90 days |
| Tier 1 (high) | Tier 2 approvers plus AI Governance / Model Risk | 60 days |

A waiver of a rule in [02-security.md](./02-security.md) or [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md) always needs the matching specialist approver regardless of tier. `ASSUMPTION:` durations are provisional.

## Waiver template (file `waivers/<WVR-YYYY-NNN>.md` or equivalent registry record)
```
id: WVR-YYYY-NNN            # registry id, not a rule id
rule_ids: [<AREA-NNN>]
system: <inventory id> / <repo>
tier: 1|2|3
requester: <person>         # a human, never an agent
reason: <why the rule cannot be met now>
risk: <what could go wrong, likelihood, impact>
compensating_controls: [<control and how it is verified>]
scope: <exact services, environments, paths>
approvers: [<role/person, date>]
start: YYYY-MM-DD
expiry: YYYY-MM-DD          # mandatory
exit_plan: <work item to remove the need, owner, date>
review_date: YYYY-MM-DD
```

## Lifecycle
`requested` -> `approved` | `rejected` -> `active` -> `renewed` | `expired` | `closed`.

## Rules

### Requesting and approving
- **WVR-001** [MUST] [review] A `MUST` rule MUST NOT be bypassed except under an approved, active waiver for that rule ID and scope.
- **WVR-002** [SHOULD] [review] A departure from a `SHOULD` rule SHOULD be explained in the MR description with the rule ID and reason; no waiver is required.
- **WVR-003** [MUST] [review] A waiver request MUST use the template and name the rule IDs, exact scope, risk, compensating controls, exit plan and an expiry date.
- **WVR-004** [MUST] [review] The requester MUST be a human employee. An AI agent MUST NOT request, approve, extend, edit or self-grant a waiver, and MUST NOT mark a waiver as approved.
- **WVR-005** [MUST] [review] The approver set MUST match the tier table and MUST NOT include the requester; approvals MUST be recorded with date and identity.
- **WVR-006** [MUST] [review] A waiver MUST include at least one compensating control that is testable or monitored, and the request MUST state how it is verified.
- **WVR-007** [MUST] [review] A waiver MUST NOT be granted for a rule that is a legal or regulatory obligation unless Compliance/Legal approves in writing; the tier table alone is insufficient. VERIFY: with Compliance which rules fall in this class once the mapping in [12-governance-and-compliance.md](./12-governance-and-compliance.md) is final.

### Duration, renewal and expiry
- **WVR-008** [MUST] [ci: waiver-check] Every waiver MUST have an expiry date not later than the tier maximum; open-ended waivers are invalid.
- **WVR-009** [MUST] [ci: waiver-check] The pipeline MUST fail the build for a waived rule once its waiver has expired, and MUST fail when a suppression references a waiver ID that does not exist or is not active.
- **WVR-010** [MUST] [review] Renewal MUST be a new approval at the tier required then, with evidence of progress on the exit plan; a waiver MUST NOT be renewed more than twice without AI Governance and Engineering standards review.
- **WVR-011** [SHOULD] [manual] Owners SHOULD receive an automatic reminder at least 14 days before expiry.

### Recording and visibility
- **WVR-012** [MUST] [ci: waiver-check] Every active waiver MUST appear in the waiver registry (a Git-tracked file or issue board, `ASSUMPTION:` location TBD) with its status, scope and expiry.
- **WVR-013** [MUST] [ci: waiver-check] Any in-code or in-config suppression of a `MUST` rule (for example `# noqa`, `# type: ignore`, `# nosec`, scanner ignore entries, `ignore_errors`) MUST carry a waiver ID in the same line or entry; unreferenced suppressions MUST fail the check.
- **WVR-014** [MUST] [review] The MR that relies on a waiver MUST reference the waiver ID and the rule ID(s).
- **WVR-015** [MUST] [manual] The waiver registry MUST be reviewed monthly by the Engineering standards owner and reported to AI Governance each quarter (`ASSUMPTION:` cadence), including count, age and renewals per rule.
- **WVR-016** [SHOULD] [manual] Rules waived frequently SHOULD be reviewed as candidates for rule change, since they signal an unrealistic or unclear rule.

### Specific cases
- **WVR-017** [MUST] [review] Use of a preview feature, a non-approved LLM provider or model, or a non-default region for an AI workload MUST have a waiver and the third-party approval described in [12-governance-and-compliance.md](./12-governance-and-compliance.md).
- **WVR-018** [MUST] [review] Emergency exceptions (production incident) MAY be approved verbally by the incident commander and one specialist approver, but MUST be written up as a waiver within two business days with a maximum duration of 14 days.
- **WVR-019** [MUST] [runtime] When a waiver expires or closes, the owner MUST remove the suppression or exception in the same or next release and record closure in the registry.

## Example: suppression with waiver reference
```python
import subprocess  # nosec B404  WVR-2026-014 (expires 2027-02-01)
```
`WVR-2026-014` is an illustrative registry ID. Rule IDs in waivers use the real `AREA-NNN` form from the owning doc.

## Checklist
- [ ] Rule is `MUST` and cannot be met now; no alternative design
- [ ] Template complete, with expiry within tier maximum
- [ ] Compensating controls testable
- [ ] Correct approvers; requester is human
- [ ] Registered; MR and suppressions reference the waiver ID
- [ ] Exit plan has owner and date
- [ ] Expiry reminder set

## Common AI failure modes
- Adding `# noqa`, `# type: ignore`, scanner ignores or `skip` to make a check pass without a waiver.
- Writing a waiver file and marking it approved.
- Deleting or weakening a test or rule instead of requesting a waiver.
- Open-ended or copy-pasted waivers with no compensating control.
- Quietly extending an expired waiver's date.
- Treating a `SHOULD` departure as needing no explanation.

## Related docs
- [12-governance-and-compliance.md](./12-governance-and-compliance.md)
- [02-security.md](./02-security.md)
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)
- [01-codebase-practices.md](./01-codebase-practices.md)
- [16-cicd-and-deployment.md](./16-cicd-and-deployment.md)
