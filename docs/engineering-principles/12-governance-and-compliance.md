# Governance and Compliance

> **Owner:** Head of AI Governance / Model Risk (with Compliance) · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** OSFI Guideline E-23 Model Risk Management (osfi-bsif.gc.ca); OSFI Guideline B-10 Third-Party Risk Management (osfi-bsif.gc.ca); OSFI Guideline B-13 Technology and Cyber Risk Management (osfi-bsif.gc.ca)

> **Not legal advice; confirm with Compliance/Legal.** This doc turns regulatory expectations into engineering rules. It does not interpret the law. References to internal governance policies are marked `ASSUMPTION:` because the policy names and links are unresolved (F1).

## Purpose
Define how AI use cases, models and agents are registered, risk-rated, approved, monitored and retired, and what evidence engineering must produce. This is the home doc for: intake and risk tiering, the model and agent inventory, accountable owners, change management, third-party (LLM vendor) approval, and audit evidence retention. Data handling lives in [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md). Waivers live in [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md).

## Regulatory map (verified against primary text where noted)
| Instrument | What it covers | Status of our check |
|---|---|---|
| OSFI E-23 Model Risk Management | Model lifecycle governance, enterprise model inventory, risk rating, risk-based intensity, data, development, independent review, deployment, monitoring and decommissioning. Covers externally sourced models and data. Applies risk-based, scaled to size and complexity | Effective **May 1, 2027**, published September 11, 2025, per the OSFI guideline page |
| OSFI B-10 Third-Party Risk Management | Third-party arrangements including cloud; due diligence, written agreements, incident notification, portability. Sections 4.3-4.4 hold the cloud-specific expectations; Annex 1 and Annex 2 cover technology/cyber due diligence and incident terms | OSFI page does not state an effective date. VERIFY: May 1, 2024 is reported by law-firm commentary only; confirm on osfi-bsif.gc.ca |
| OSFI B-13 Technology and Cyber Risk Management | The institution's own technology and cyber risk (governance, architecture, delivery, operations, security). B-10 section 4.2 defers to B-13 for this | VERIFY: January 1, 2024 effective date is from secondary sources; the B-13 page was not retrievable at write time |

Placement answer: **cloud and third-party requirements sit in B-10** (cloud portability, cloud governance, data protection and key management expectations). **B-13 holds the FRFI's own technology and cyber controls.** Cite both: B-10 for vendor and cloud approval, B-13 for engineering controls (see [02-security.md](./02-security.md)).

Internal policy references: `ASSUMPTION:` an internal AI governance policy, a model risk management policy and a third-party risk policy exist. Replace the placeholders `<ai-governance-policy>`, `<mrm-policy>`, `<tprm-policy>` with real names once F1 is resolved.

## Risk tiers
Tiers drive review intensity, autonomy ceiling, eval thresholds and waiver approvers. The tier is set at intake and re-assessed on any trigger event (RULE GOV-008).

| Tier | Typical signals | Minimum controls |
|---|---|---|
| Tier 3 (low) | Internal productivity, no customer data, no decision influence, human reviews every output | Inventory entry, owner, standard CI gates |
| Tier 2 (medium) | Personal information, customer-facing text, or output used by staff in a decision | Tier 3 plus independent review, eval thresholds, monitoring, PIA per [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md) |
| Tier 1 (high) | Influences coverage, pricing, underwriting, claims or other customer outcomes; autonomous actions; restricted data | Tier 2 plus governance sign-off, fairness/bias assessment, human decision on every outcome, annual revalidation |

`ASSUMPTION:` these tier names and cut-offs are provisional until the internal model risk policy is shared (F1). The tier list in this doc is the one used by the other standards.

## Rules

### Intake and inventory
- **GOV-001** [MUST] [review: MR template] Every AI use case, model, and agent MUST have an approved intake record (purpose, data classes, users, decision impact, proposed tier) before it is built beyond a prototype.
- **GOV-002** [MUST] [ci: registry-check] Every deployed model, prompt-based agent and tool MUST have an inventory entry with a unique inventory ID, and the service repository MUST reference that ID in its manifest (see [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md)).
- **GOV-003** [MUST] [ci: registry-check] The inventory entry MUST record: owner, tier, purpose and non-goals, model deployment and pinned version, data classes handled, third-party vendor, last validation date, and next review date.
- **GOV-004** [MUST] [manual] Prototypes and sandboxes MUST NOT process real customer data or Tier 1 production decisions; promotion to production requires a completed intake record.
- **GOV-005** [SHOULD] [ci: registry-check] The pipeline SHOULD export the inventory as a machine-readable artifact on each release so Model Risk can reconcile it with the enterprise inventory.

### Risk tiering
- **GOV-006** [MUST] [review] Every inventory entry MUST carry a risk tier from the table above, assigned by the owner and confirmed by AI Governance.
- **GOV-007** [MUST] [review] Any use case that influences coverage, pricing, underwriting or claims outcomes MUST be Tier 1 and MUST keep a human as the decision maker; an agent MUST NOT autonomously deny, rescind or reprice.
- **GOV-008** [MUST] [review] The tier MUST be re-assessed when the model, prompt, tool set, data classes, user population or decision impact changes.
- **GOV-009** [SHOULD] [review] A tier SHOULD NOT be lowered without written approval from AI Governance; the approval is attached to the inventory entry.

### Ownership and accountability
- **GOV-010** [MUST] [ci: CODEOWNERS check] Every system in the inventory MUST name one accountable owner (a role and a person) and one technical lead; the owner field MUST match the repository CODEOWNERS file.
- **GOV-011** [MUST] [manual] Ownership transfer MUST be recorded in the inventory before the previous owner leaves; orphaned systems MUST be suspended or retired within an agreed period (`ASSUMPTION:` 30 days, confirm with Model Risk).
- **GOV-012** [MUST] [review] An AI coding agent MUST NOT be recorded as an owner, approver or reviewer of any governance artifact.

### Validation, monitoring and change
- **GOV-013** [MUST] [review] Tier 1 and Tier 2 systems MUST be reviewed by someone independent of the builders before first production release, covering conceptual soundness, data fitness, eval results and known limitations.
- **GOV-014** [MUST] [ci: eval gate] Eval thresholds set for a system MUST be met in CI and the result MUST be stored as evidence; thresholds and datasets are defined in [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md).
- **GOV-015** [MUST] [runtime] Production monitoring MUST track quality, drift, safety events, cost and incident counts per inventory ID, with alert thresholds agreed with the owner (see [10-logging-observability.md](./10-logging-observability.md) and [18-reliability-and-operations.md](./18-reliability-and-operations.md)).
- **GOV-016** [MUST] [ci: MR approval rules] A change to a model version, prompt, tool definition, guardrail or retrieval source in a Tier 1 or Tier 2 system MUST go through an MR with CODEOWNERS approval and a re-run of required evals before deployment.
- **GOV-017** [SHOULD] [manual] Tier 1 systems SHOULD be revalidated at least annually and Tier 2 at least every two years (`ASSUMPTION:` cadence, confirm with Model Risk).
- **GOV-018** [MUST] [manual] Retired systems MUST be decommissioned formally: traffic removed, credentials revoked, data deleted per retention, and the inventory entry closed with a date.

### Third-party and LLM vendor approval
- **GOV-019** [MUST] [review] A new third-party AI service, model provider, SDK that sends data off-platform, or MCP server MUST be approved through third-party risk management before use; the approval ID is recorded in the inventory.
- **GOV-020** [MUST] [review] The approved LLM platform is Microsoft Foundry (Azure OpenAI); any other provider MUST have a waiver per [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md) and a completed third-party approval. Which Foundry models are approved is unresolved (F2): `ASSUMPTION:` only models on the governance-approved list in [15-llm-and-model-governance.md](./15-llm-and-model-governance.md) may be deployed.
- **GOV-021** [MUST] [review] The vendor assessment MUST cover the B-10 topics: due diligence on technology and cyber risk, incident notification terms, subcontractors, data location, exit and portability, and concentration risk.
- **GOV-022** [SHOULD] [review] Each third-party AI dependency SHOULD have a documented exit plan (alternative deployment, degradation path) reviewed when the vendor or model changes.

### Evidence and audit
- **GOV-023** [MUST] [ci: artifact retention] Release pipelines MUST retain, per inventory ID and release: eval results, scan reports, SBOM, approval records, model/prompt versions and deployment record.
- **GOV-024** [MUST] [runtime] Decision-influencing outputs of Tier 1 and Tier 2 systems MUST be traceable to the model version, prompt version, inputs (by reference or redacted), tool calls and human reviewer, with an audit log that is append-only for its retention period.
- **GOV-025** [MUST] [manual] Evidence retention periods MUST follow the corporate records schedule (`ASSUMPTION:` `<records-retention-schedule>`); engineering MUST NOT set shorter periods for governance evidence.
- **GOV-026** [MUST] [review] A material incident involving an AI system (harmful output, data exposure, unauthorized action) MUST be reported to the owner and AI Governance, and a technology/cyber incident MUST follow the corporate OSFI incident reporting process (VERIFY: OSFI Technology and Cyber Security Incident Reporting Advisory timelines).
- **GOV-027** [SHOULD] [review] Each MR that changes governance-relevant behaviour SHOULD cite the rule IDs it satisfies in its description so reviewers and auditors can trace controls.

## Rule-to-requirement mapping
This maps regulatory **themes** to the rules that implement them, so Compliance can trace a requirement to enforceable controls and engineers can see why a rule exists. It is thematic, not clause-level. `ASSUMPTION:` Compliance maps themes to exact clause numbers; until then, do not cite a clause from this table. Rules not listed here are **not yet mapped; Compliance to complete** (for example the redaction and pre-call guard rules DAT-007 and DAT-012 to DAT-014 are privacy safeguards awaiting clause mapping). A per-rule machine-readable mapping is future work (the `rules.yml` registry).

| Regulatory theme | Instrument (check primary text) | Rules that implement it |
|---|---|---|
| Model and agent inventory, including externally sourced models | OSFI E-23 | GOV-001, GOV-002, GOV-003, GOV-005, REG-012, REG-027, LLM-002 |
| Risk rating and risk-based intensity | OSFI E-23 | GOV-006, GOV-007, GOV-008, GOV-009, PRN-014, PRN-017 |
| Accountability and ownership | E-23, B-13 governance, PIPEDA accountability | GOV-010, GOV-011, GOV-012, DAT-023 |
| Independent review and validation before deployment | OSFI E-23 | GOV-013, GOV-014, EVL-033 |
| Ongoing monitoring and drift | OSFI E-23 | GOV-015, EVL-032, PRN-016 |
| Change management for models, prompts and tools | E-23, B-13 delivery | GOV-016, LLM-007, LLM-006, PRC-007, PRC-019, PRC-026, CIC-035 |
| Decommissioning and retirement | OSFI E-23 | GOV-018, LLM-014 |
| Third-party and cloud risk (due diligence, agreements, portability) | OSFI B-10 | GOV-019, GOV-020, GOV-021, DEP-028, SEC-023, WVR-017 |
| Technology and cyber controls (access, secrets, scanning, supply chain) | OSFI B-13 | SEC-001, SEC-009, SEC-011, SEC-012, SEC-028, DEP-024, DEP-025, SCR-001, SCR-006, SCR-008, CIC-020 |
| Least privilege for agents and tools | B-13, OWASP agentic list | FDY-010, REG-018, SEC-018, SEC-014 |
| Human oversight and emergency stop | E-23 risk controls | SEC-015, REL-024, REL-025, CIC-032 |
| Audit trail and evidence retention | E-23, B-13 operations | GOV-023, GOV-024, GOV-025, OBS-027, OBS-028, OBS-029, EVL-034, LLM-028 |
| Incident management and reporting | B-10 incident notification, B-13 operations | GOV-026, REL-029, REL-030, REL-031, SCR-023 |
| Privacy accountability, PIA before processing | PIPEDA, Quebec Law 25 | DAT-019, DAT-020, DAT-023 |
| Data residency and foreign-access risk | Law 25 (outside-Quebec test), PIPEDA transfers | DAT-021, FDY-024, FDY-025 |
| Data minimisation, classification, and no customer data in dev/test | PIPEDA, Law 25 | DAT-001, DAT-004, DAT-005, DAT-006, DAT-007, DAT-012, DAT-013, DAT-014, DAT-015, DAT-016, DAT-018, GOV-004 |
| No customer data to train or fine-tune models | PIPEDA purpose limitation | DAT-010 |
| Automated decision transparency | Law 25 | DAT-022 |
| Retention, deletion and access requests | PIPEDA, Law 25 | DAT-024, DAT-025, DAT-026, RAG-025 |
| Breach response | PIPEDA breach reporting | DAT-028 |
| Exceptions are approved, time-bound and tracked | internal risk governance | WVR-006, PRC-020 |

`VERIFY:` instrument effective dates are listed in the regulatory map above. Revisit this table whenever Compliance publishes or changes an internal policy (F1) or when OSFI revises a guideline.

## Checklist
- [ ] Intake record approved and linked in the MR
- [ ] Inventory ID present in the manifest; entry complete
- [ ] Tier assigned and confirmed; Tier 1 has human decision maker
- [ ] Owner matches CODEOWNERS
- [ ] Independent review done (Tier 1 and 2)
- [ ] Evals met thresholds; results retained
- [ ] Third-party approval ID recorded; exit plan noted
- [ ] Monitoring and alerts configured
- [ ] Audit log covers model, prompt, tools and reviewer
- [ ] All `ASSUMPTION:` and `VERIFY:` markers resolved or accepted by Compliance

## Common AI failure modes
- Treating a prototype as exempt and shipping it to production without intake.
- Quietly swapping a model version or prompt and skipping re-validation.
- Listing the coding agent as reviewer or owner.
- Inventing OSFI section numbers or dates instead of citing the guideline text.
- Choosing a new SDK or hosted service for convenience without third-party approval.
- Lowering the risk tier to avoid review.
- Logging decisions without model and prompt versions, leaving no audit trail.

## Related docs
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)
- [02-security.md](./02-security.md)
- [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md)
- [15-llm-and-model-governance.md](./15-llm-and-model-governance.md)
- [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md)
- [16-cicd-and-deployment.md](./16-cicd-and-deployment.md)
