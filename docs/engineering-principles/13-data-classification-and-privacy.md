# Data Classification and Privacy

> **Owner:** Chief Privacy Officer (with Information Security) · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** PIPEDA fair information principles (priv.gc.ca); Quebec Act respecting the protection of personal information in the private sector, as amended by Law 25 (legisquebec.gouv.qc.ca, cai.gouv.qc.ca); OSFI B-10 (osfi-bsif.gc.ca); Microsoft Learn (Azure OpenAI / Foundry authentication)

> **Not legal advice; confirm with Compliance/Legal.** References to internal governance and privacy policies are marked `ASSUMPTION:` because their names and contents are unresolved (F1). The Quebec statute pages could not be retrieved at write time; every section-level claim about Law 25 carries `VERIFY:`.

## Purpose
Define the data classification scheme and a single matrix of what data may go where (LLM prompts, logs and traces, tests, indexes, CI). Set privacy rules for personal information used by AI systems, including residency, privacy impact assessment (PIA), retention, deletion and access requests. This is the home doc for classification and privacy. Logging mechanics are in [10-logging-observability.md](./10-logging-observability.md); secrets are in [06-secrets-and-env.md](./06-secrets-and-env.md); governance approval is in [12-governance-and-compliance.md](./12-governance-and-compliance.md).

## Classification scheme
`ASSUMPTION:` these four levels match, or will be mapped to, the corporate classification policy `<data-classification-policy>`.

| Class | Definition | Examples (all fictional) |
|---|---|---|
| Public | Approved for public release | Published product brochure |
| Internal | Business information not for release; no personal information | Internal runbooks, architecture diagrams |
| Confidential | Personal information of low sensitivity, or commercially sensitive data | Customer name and contact, policy number, employee data |
| Restricted | Health, financial, beneficiary, identity-document, authentication, government identifier, or any data whose exposure causes serious harm | Medical report text, claim details, banking details, SIN, secrets and keys |

Rule: when data of mixed class is combined, the result takes the **highest** class. Data without a label is Restricted until labelled.

## Data-flow matrix
`Y` allowed; `R` allowed only after redaction or tokenization; `P` allowed only with an approved PIA and governance approval (tier per [12](./12-governance-and-compliance.md)); `N` never.

| Destination | Public | Internal | Confidential | Restricted |
|---|---|---|---|---|
| Prompt to approved Foundry deployment (Canada region, private networking) | Y | Y | P | P |
| Prompt to any other LLM or tool | Y | N | N | N |
| Application logs, traces, metrics (content capture off) | Y | Y | R | N |
| Telemetry with prompt/response capture enabled | Y | Y | N | N |
| Unit and integration tests, fixtures | Y | Y | N (synthetic only) | N |
| Golden eval datasets | Y | Y | N (synthetic only) | N |
| Vector or search index | Y | Y | P | P |
| Developer laptop and AI coding agent context | Y | Y | N | N |
| CI jobs and artifacts | Y | Y | N | N |
| Non-production environments | Y | Y | N (synthetic only) | N |
| Third-party SaaS (analytics, ticketing, chat) | Y | P | N | N |

## Residency and sovereignty
- Azure Canada Central (Toronto) provides physical residency for data at rest. It does **not** by itself provide legal sovereignty: a US-headquartered provider may be subject to foreign law (for example the US CLOUD Act). `ASSUMPTION:` the organization's position on foreign-access risk is set by Legal and the third-party risk policy; this doc requires the PIA to address it.
- Foundry deployment types can process data outside the chosen region (global or data-zone deployment types). VERIFY: current Microsoft Learn description of each deployment type and its processing location, then pin the allowed type in [23-azure-foundry-standards.md](./23-azure-foundry-standards.md).
- Quebec test: the trigger for a PIA on transfers is personal information leaving **Quebec**, not Canada. VERIFY: Quebec private-sector Act s. 17 (assessment of privacy-related factors before communicating personal information outside Quebec) against the current statute text.

## Rules

### Classification and handling
- **DAT-001** [MUST] [review] Every dataset, table, index, bucket, topic and prompt template MUST carry a classification label (Public, Internal, Confidential, Restricted) in its manifest, README or resource tags.
- **DAT-002** [MUST] [ci: terraform tag check] Every Azure resource storing Confidential or Restricted data MUST have a `data-classification` tag set by Terraform, and the CI policy check MUST fail when it is missing.
- **DAT-003** [MUST] [review] Data flows MUST conform to the data-flow matrix; any `P` cell requires an approved PIA and an inventory entry before the first production use.
- **DAT-004** [MUST] [review] Unlabelled data MUST be treated as Restricted.
- **DAT-005** [SHOULD] [review] Services SHOULD minimise fields sent to a model: select needed fields explicitly, never send whole records or whole documents when an excerpt suffices.

### LLM prompts and outputs
- **DAT-006** [MUST] [ci: egress policy] Prompts containing Confidential or Restricted data MUST only be sent to an approved Foundry deployment in an approved Canadian region over private networking; no other endpoint MAY receive them.
- **DAT-007** [MUST] [test] A pre-call guard MUST block or redact data above the caller's allowed class before it reaches the model client; the guard MUST have unit tests with synthetic positives (see [24-testing-standards.md](./24-testing-standards.md)).
- **DAT-008** [MUST] [review] Prompt templates and system prompts MUST NOT contain personal information, secrets or customer examples; use placeholders and synthetic few-shot examples.
- **DAT-009** [MUST] [review] Model outputs MUST be classified at the highest class of any input they were derived from and stored, logged and shared accordingly.
- **DAT-010** [MUST] [review] Customer data MUST NOT be used to fine-tune or train any model without an approved PIA, governance approval and documented consent or legal basis.
- **DAT-011** [MUST] [review] Retrieval-augmented systems MUST classify indexed content and enforce per-user access at query time as specified in [19-rag-and-retrieval.md](./19-rag-and-retrieval.md).

### Logs, traces and telemetry
- **DAT-012** [MUST] [runtime] Application logs, traces and metric labels MUST NOT contain Restricted data and MUST redact Confidential data before leaving the process or the collector.
- **DAT-013** [MUST] [runtime] Prompt and response content capture in telemetry MUST be disabled by default in production; enabling it for a service requires a recorded approval and treats the telemetry store as Restricted.
- **DAT-014** [MUST] [test] Redaction MUST be covered by tests that feed synthetic identifiers (names, emails, phone numbers, policy numbers) through the logging pipeline and assert none appear in output.

### Tests, evals and non-production
- **DAT-015** [MUST] [ci: secret/PII scan] Real customer data MUST NOT exist in repositories, fixtures, golden datasets, CI variables, CI artifacts or non-production environments; the pipeline MUST scan for known identifier patterns.
- **DAT-016** [MUST] [review] Test and eval data MUST be synthetic or irreversibly anonymised with a documented method; the generator and seed MUST be committed.
- **DAT-017** [SHOULD] [review] Synthetic data SHOULD preserve schema, edge cases and EN/FR variants, and SHOULD be labelled `synthetic` in dataset metadata.
- **DAT-018** [MUST] [review] Developers and AI coding agents MUST NOT paste production records into prompts, issues, MR comments or chat tools.

### Privacy governance
- **DAT-019** [MUST] [review] A PIA MUST be completed and approved before any AI system processes personal information in production, and re-done when purpose, data classes, vendor, region or model changes.
- **DAT-020** [MUST] [review] The PIA MUST state: purposes, data classes, legal basis or consent, retention, locations of processing and storage, subprocessors, foreign-access risk, automated-decision impact, and safeguards.
- **DAT-021** [MUST] [review] Personal information MUST NOT leave Quebec (including to another Canadian province) for processing, storage or inference until the PIA has assessed the transfer. VERIFY: s. 17 of the Quebec private-sector Act and any applicable regulation.
- **DAT-022** [MUST] [review] Where a system makes or materially informs a decision about an individual using automated processing, the design MUST support informing the individual and providing human review on request. VERIFY: Quebec private-sector Act s. 12.1 and PIPEDA guidance on automated decision-making.
- **DAT-023** [MUST] [review] Each system MUST name an accountable owner for personal information it handles (PIPEDA accountability principle) and the owner MUST match the inventory entry.

### Retention, deletion and access requests
- **DAT-024** [MUST] [review] Every store of personal information (database, blob, index, cache, evaluation set, trace store) MUST have a documented retention period no longer than needed for the purpose, set from the corporate records schedule (`ASSUMPTION:` `<records-retention-schedule>`).
- **DAT-025** [MUST] [test] Deletion MUST propagate to derived stores (search indexes, embeddings, caches, summaries, trace stores); a test or runbook step MUST demonstrate it.
- **DAT-026** [MUST] [review] Systems MUST support locating and exporting a given individual's personal information to answer access, correction and deletion requests within the corporate timeline (VERIFY: statutory timelines with Legal).
- **DAT-027** [SHOULD] [manual] Services SHOULD tokenize direct identifiers at ingestion so downstream AI components work on tokens, with the mapping held in a restricted store.
- **DAT-028** [MUST] [manual] A suspected privacy breach (disclosure of personal information to an unauthorised party, including via a prompt or log) MUST be reported to the Privacy Office immediately; the Privacy Office decides on regulator and individual notification. VERIFY: PIPEDA breach-of-security-safeguards reporting thresholds and Quebec incident register obligations.

## Redaction and synthetic-data tooling
| Need | Option | Status |
|---|---|---|
| Detect and mask PII in text | Microsoft Presidio (open source) or Azure AI Language PII detection | VERIFY: current docs, supported languages (EN/FR recall must be measured), and approval via [20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md) |
| Synthetic tabular data | Faker with fixed seed; schema-driven generators | VERIFY: Faker locale support for `en_CA` and `fr_CA` |
| Tokenization | Format-preserving or keyed-hash tokens; keys in Azure Key Vault | See [06-secrets-and-env.md](./06-secrets-and-env.md) |

Rule of thumb: redaction libraries miss things. Use them as one layer, measure recall on a synthetic EN/FR set, and keep the matrix above as the control.

```python
# Pre-call guard (sketch). Class labels come from the caller's data contract.
from enum import IntEnum

class DataClass(IntEnum):
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3

def guard_prompt(text: str, label: DataClass, allowed: DataClass) -> str:
    if label > allowed:
        raise PermissionError("prompt data class exceeds deployment allowance")
    return text
```

## Checklist
- [ ] All data labelled; unlabelled treated as Restricted
- [ ] Data-flow matrix respected; `P` cells have an approved PIA
- [ ] Prompts go only to approved Foundry deployments in approved regions
- [ ] Content capture off in production telemetry
- [ ] Redaction tests pass with synthetic identifiers
- [ ] No real customer data in repo, CI, tests or non-production
- [ ] PIA covers Quebec transfer and foreign-access risk
- [ ] Retention set; deletion propagates to indexes and caches
- [ ] Access/deletion request path documented
- [ ] `ASSUMPTION:` and `VERIFY:` markers reviewed by Legal

## Common AI failure modes
- Pasting a real-looking record into a prompt, fixture or test "for realism".
- Enabling prompt/response capture in telemetry to debug and leaving it on.
- Assuming Canada Central removes the need for a PIA or foreign-access analysis.
- Treating Canada-wide residency as satisfying the Quebec transfer test.
- Redacting at the UI but not in logs, traces or error messages.
- Forgetting derived copies (embeddings, caches, summaries) when deleting.
- Hard-coding sample personal data into prompt templates.
- Citing statute section numbers from memory.

## Related docs
- [12-governance-and-compliance.md](./12-governance-and-compliance.md)
- [02-security.md](./02-security.md)
- [06-secrets-and-env.md](./06-secrets-and-env.md)
- [10-logging-observability.md](./10-logging-observability.md)
- [19-rag-and-retrieval.md](./19-rag-and-retrieval.md)
- [23-azure-foundry-standards.md](./23-azure-foundry-standards.md)
- [24-testing-standards.md](./24-testing-standards.md)
- [22-localization-and-accessibility.md](./22-localization-and-accessibility.md)
