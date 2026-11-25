# LLM and Model Governance

> **Owner:** AI governance lead with Platform Engineering lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** [Model versioning](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/model-versions), [Model lifecycle and support policy](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements), [Foundry quotas and limits](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/quotas-limits), internal AI governance policies (names not yet supplied; open item F1)

## Purpose
This doc is the **policy** for which models we use and how we change them: the approved list, version pinning, prompts as audited artifacts, fallback, deprecation and migration, cost budgets and structured output. Platform mechanics (SDK, SKUs, guardrails, identity) are in [23-azure-foundry-standards.md](./23-azure-foundry-standards.md). Manifests are in [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md). Regulatory framing (model risk, inventory, vendor approval) is in [12-governance-and-compliance.md](./12-governance-and-compliance.md); data handling is in [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md).

Decision recorded: the approved provider is **Microsoft Foundry only**. ASSUMPTION: which models count as approved is unresolved (F2); this doc defines the process and a table to fill, and uses placeholder names like `<chat-deployment>`.

## Rules

### Approved models
- **LLM-001** [MUST] [review] Only models on the approved list below MAY be deployed. Until AI governance fills the list (F2), no model is approved for production and every use is a waiver ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)). ASSUMPTION: F2 open.
- **LLM-002** [MUST] [manual] Adding a model to the approved list MUST follow the intake process: vendor and terms review ([12-governance-and-compliance.md](./12-governance-and-compliance.md)), data-handling and residency check, evals on our own tasks, security review, and AI governance sign-off recorded in the inventory.
- **LLM-003** [MUST] [review] The approved list MUST state per model: allowed deployment types (see [23-azure-foundry-standards.md](./23-azure-foundry-standards.md)), maximum data class, allowed use-case risk tiers, languages tested (English and French), and lifecycle stage and retirement date from the Models API.
- **LLM-004** [MUST] [ci: make registry-check] Services MUST reference models only by the approved entry (placeholder `<chat-deployment>` style names in docs; real deployment names in config), never by a model name hard-coded in source.
- **LLM-005** [SHOULD] [review] Models in Preview lifecycle stage SHOULD NOT be approved for production; preview models are force-upgraded or retired with at least 30 days notice.

### Version pinning and change
- **LLM-006** [MUST] [ci: terraform plan check] Production deployments MUST pin an explicit model version; floating aliases and "latest" MUST NOT be used. The agent manifest `model_version` MUST match the deployed version.
- **LLM-007** [MUST] [review] A change of model, model version, deployment type, sampling parameters or system prompt is a **model change**: it MUST be an MR, MUST re-run the evals in [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md) against the thresholds, and MUST record before and after results as evidence.
- **LLM-008** [MUST] [review] High-risk use cases ([26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md)) MUST NOT change model version without AI governance review of the eval results.
- **LLM-009** [MUST] [ci: make eval] Sampling parameters (temperature, top-p, seed where supported, maximum output tokens) MUST be set explicitly in configuration and covered by evals; defaults MUST NOT be relied on.
- **LLM-010** [SHOULD] [review] Each approved model SHOULD have a documented fallback model (or "route to human") that has passed the same evals.

### Deprecation and migration
- **LLM-011** [MUST] [manual] The platform team MUST own a **retirement calendar** with a named owner role, fed by the scheduled lifecycle job in [23-azure-foundry-standards.md](./23-azure-foundry-standards.md).
- **LLM-012** [MUST] [manual] Migration to a replacement MUST start at least 90 days before the retirement date and MUST complete evals, canary and rollout before it. Microsoft names the official replacement roughly 90 to 120 days before retirement and does not extend retirement dates; do not wait for the name to start evaluating.
- **LLM-013** [MUST] [review] Migration MUST evaluate candidates on our own prompts and data comparing quality, latency and cost together, and MUST NOT rely on public benchmarks alone. Prompts and schemas MAY need adaptation and are re-reviewed as code.
- **LLM-014** [MUST] [manual] A model with an emergency or security-driven retirement MUST trigger the incident process ([18-reliability-and-operations.md](./18-reliability-and-operations.md)) and the fallback in LLM-010.

### Prompts and definitions as artifacts
- **LLM-015** [MUST] [ci: make registry-check] System prompts, few-shot examples, and tool descriptions MUST live in version control (`prompts/`), be loaded by a loader that verifies the hash recorded in the agent manifest, and be reviewed like code.
- **LLM-016** [MUST] [review] Prompt changes MUST be MRs that cite the eval run; prompts MUST NOT be edited in a portal or injected from runtime configuration without a hash entry.
- **LLM-017** [MUST] [review] Prompts MUST NOT contain secrets, personal data, real customer examples or internal system names that are not needed; examples MUST be synthetic ([13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)).
- **LLM-018** [SHOULD] [review] Prompts SHOULD state the task, constraints and output schema; instructions that rely on the model "being careful" are not controls. Security-relevant rules MUST also be enforced in code ([02-security.md](./02-security.md)).
- **LLM-019** [MUST] [review] User-supplied and retrieved text MUST be kept structurally separate from instructions and treated as untrusted ([02-security.md](./02-security.md); [19-rag-and-retrieval.md](./19-rag-and-retrieval.md)).

### Structured output and validation
- **LLM-020** [MUST] [test] Every LLM output consumed by code MUST be parsed against a schema (pydantic) with explicit failure handling; free-text output MUST NOT drive actions.
- **LLM-021** [MUST] [test] Schema validation failure MUST NOT be "fixed up" silently; allow a bounded retry (at most the configured count), then fall back or escalate to a human.
- **LLM-022** [SHOULD] [review] Prefer constrained structured output features where the approved model supports them, but still validate. VERIFY: availability per approved model and deployment type.
- **LLM-023** [MUST] [test] Outputs that affect a customer, a coverage, pricing or claims outcome MUST include a reason code and source references so a reviewer can verify them ([12-governance-and-compliance.md](./12-governance-and-compliance.md)).

### Limits, cost and fallback
- **LLM-024** [MUST] [runtime] Each service MUST set maximum input and output tokens, a per-request timeout and a per-user or per-job rate limit to bound cost and abuse (threats in [02-security.md](./02-security.md)).
- **LLM-025** [MUST] [manual] Each service MUST have a monthly cost budget with an owner, alerts at agreed thresholds and an anomaly alert. Quota is not a budget.
- **LLM-026** [MUST] [review] Cost per use case MUST be measured (tokens and tool calls per task) and reported with the eval results so model-tier choices can be compared ([05-decision-playbook.md](./05-decision-playbook.md)).
- **LLM-027** [MUST] [runtime] When the model is unavailable, over quota or fails validation, the service MUST degrade as designed (fallback model, cached or deterministic answer, or human queue) and MUST NOT fabricate an answer ([18-reliability-and-operations.md](./18-reliability-and-operations.md)).
- **LLM-028** [MUST] [runtime] Every model call MUST record deployment name, model version, prompt hash, token counts, latency and outcome (redacted per [10-logging-observability.md](./10-logging-observability.md)) so a decision can be reconstructed for audit.

### Data to models
- **LLM-029** [MUST] [review] Data sent to a model MUST NOT exceed the model's maximum data class and MUST be minimized to what the task needs; the PIA outcome applies ([13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)).
- **LLM-030** [MUST] [review] Models MUST NOT be fine-tuned or customized on customer data without AI governance approval, PIA and a data-lineage record. ASSUMPTION: policy on fine-tuning is pending F1.

## Approved model register (to be completed by AI governance)
| Model entry | Deployment types allowed | Max data class | Risk tiers | Languages tested | Lifecycle stage / retirement | Fallback | Approved by / date |
|---|---|---|---|---|---|---|---|
| `<chat-deployment>` | `Standard`, `ProvisionedManaged` (see 23) | TBD | TBD | EN, FR | from Models API | `<fallback-deployment>` | TBD |
| `<embedding-deployment>` | `Standard` | TBD | TBD | EN, FR | from Models API | none | TBD |

Rows are empty by design: ASSUMPTION F2 open. Embedding models follow different, longer timelines; read the retirement schedule before choosing.

## Change process for a model or prompt
| Step | Evidence |
|---|---|
| 1. Propose change in an MR | Diff of prompt, parameters or deployment |
| 2. Run evals vs thresholds | Eval report link ([14](./14-evals-and-testing-ai.md)) |
| 3. Check cost and latency | Cost per task, p95 latency |
| 4. Review | Security and owner; AI governance for high risk |
| 5. Canary | Sampled traffic, rollback plan |
| 6. Update manifest and inventory | Manifest hash and version, inventory id |

## Checklist
- [ ] Model is on the approved list with a version and a lifecycle date.
- [ ] Manifest `model_version` equals the deployed version; no floating alias.
- [ ] Prompts are in `prompts/` with hashes in the manifest; prompt MR cites eval run.
- [ ] Sampling parameters and token limits are explicit.
- [ ] Outputs are schema-validated; failure path defined; no fabricated answers.
- [ ] Fallback tested; retirement calendar entry exists with owner.
- [ ] Budget, alerts and per-call audit record exist.
- [ ] Data class sent to the model is within the model's maximum.

## Common AI failure modes
- Using the model name from a sample, unpinned, because "it worked".
- Changing temperature or the prompt "slightly" without re-running evals.
- Putting policy in the prompt only ("never reveal ...") with no code enforcement.
- Parsing model text with regular expressions instead of schema validation, or repairing invalid JSON silently.
- Forgetting retirement: a pinned model silently stops at its retirement date.
- Treating public benchmark rank as proof for our task.
- Embedding real customer text as few-shot examples.
- Adding a fallback model that was never evaluated.

## Related docs
- [23-azure-foundry-standards.md](./23-azure-foundry-standards.md): mechanics for the policies here.
- [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md): manifests that record model and prompt hashes.
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md): eval thresholds.
- [12-governance-and-compliance.md](./12-governance-and-compliance.md): inventory, vendor approval.
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md): data classes and PIA.
- [18-reliability-and-operations.md](./18-reliability-and-operations.md): degradation and incident handling.
- [05-decision-playbook.md](./05-decision-playbook.md): model tier selection.
- [26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md): risk tiers per use case.

## Sources
- Model versioning in Microsoft Foundry Models: https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/model-versions
- Foundry Models lifecycle and support policy: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
- Foundry Models quotas and limits: https://learn.microsoft.com/en-us/azure/foundry/foundry-models/quotas-limits
