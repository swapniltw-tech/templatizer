# Decision Playbook

> **Owner:** Platform Engineering lead with AI governance · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** internal standard; platform facts from [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) and [Foundry deployment types](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types)

## Purpose
"When you have X, go with Q." A compact table of default decisions for AI and agent work, with when to escalate and where the reasoning lives. Each row is a default, not a law: deviate only with an ADR that cites the row. Per-use-case depth (templates, evals, threats, regulatory notes) is in [26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md); this doc links to it and does not repeat it.

How to read: apply the **simplest option that passes your evals**. The ladder is: deterministic code, then one LLM call, then a fixed workflow, then a bounded single agent, then (rarely) multiple agents ([04-engineering-principles.md](./04-engineering-principles.md)). Model names are placeholders because the approved list is open item F2.

## Rules
- **DEC-001** [MUST] [review] Every ADR for an AI feature MUST cite the decision row(s) it relies on or state why it deviates and which alternative it chose.
- **DEC-002** [MUST] [review] Decisions MUST follow the ladder: deterministic code, single LLM call, fixed workflow, bounded single agent, multi-agent. A higher step MUST be justified by eval evidence that the lower step fails.
- **DEC-003** [MUST] [review] When a deterministic rule can express the requirement exactly, it MUST be implemented as code, not an LLM prompt.
- **DEC-004** [MUST] [review] An orchestration framework MUST NOT be adopted for a single-call or fixed workflow; if one is needed, record the choice and pin versions ([23-azure-foundry-standards.md](./23-azure-foundry-standards.md)).
- **DEC-005** [MUST] [test] LLM output consumed by code MUST be structured and schema-validated; free text MAY be shown to a human only ([15-llm-and-model-governance.md](./15-llm-and-model-governance.md)).
- **DEC-006** [MUST] [review] Human review MUST be mandatory for the conditions in row 13; the review MUST be enforced in code, not in the prompt ([25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md)).
- **DEC-007** [MUST] [test] Per-user permissions on retrieved content MUST be enforced at retrieval, before content reaches the model ([19-rag-and-retrieval.md](./19-rag-and-retrieval.md)).
- **DEC-008** [MUST] [review] Data classification and the PIA gate MUST be completed before any personal or restricted data reaches a model ([13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)).
- **DEC-009** [SHOULD] [review] Model tier SHOULD be the smallest approved model that passes evals at acceptable cost and latency; the ADR MUST record the eval results and cost per task that justify the tier.
- **DEC-010** [MUST] [review] Prompt, retrieval and fine-tuning MUST be tried in that order; fine-tuning on customer data needs governance approval ([15-llm-and-model-governance.md](./15-llm-and-model-governance.md)).
- **DEC-011** [MUST] [review] Asynchronous and batch designs MUST use deployment types allowed for the data class; Foundry batch types are not allowed for personal information ([23-azure-foundry-standards.md](./23-azure-foundry-standards.md)).
- **DEC-012** [SHOULD] [review] Caching SHOULD be used for deterministic, idempotent and non-personal results; cached content MUST NOT cross user or classification boundaries.
- **DEC-013** [MUST] [review] Build-versus-buy for any LLM capability MUST stay inside Foundry or go through a waiver and vendor approval ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)).
- **DEC-014** [MUST] [review] When a row's "escalate when" condition is met, the team MUST record the escalation and the approver in the ADR.
- **DEC-015** [MUST] [review] A use case that is high-risk per [26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md) MUST follow the autonomy cap in PRN-018 (never above rung 2, human decides) and MUST NOT adopt a row that raises autonomy above it.
- **DEC-016** [SHOULD] [review] AI coding agents SHOULD treat this table as defaults and MUST NOT choose a higher rung (see [04-engineering-principles.md](./04-engineering-principles.md)) than the row recommends without a human decision recorded in the ADR.
- **DEC-017** [MUST] [review] Changes to this table MUST be MRs approved by the owner roles and AI governance; each row MUST cite sources or an internal rule.
- **DEC-018** [MUST] [manual] Rows depending on the approved model list MUST be re-checked when open item F2 is resolved. ASSUMPTION: F2 open.

## Decision table
Case links go to [26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md). "Escalate" means move to a more capable or more controlled option, or to governance.

| # | Requirement | Recommended | Why | When to escalate | Sources |
|---|---|---|---|---|---|
| 1 | Answer questions over structured or semi-structured documents | Structure-aware retrieval (headings, clause ids, metadata filters) first; vector search where structure is weak | Exact, auditable retrieval; cheaper | Paraphrased queries and missing structure: add vector or hybrid; coverage decisions: [Case 04](./26-ai-use-case-catalog.md#case-04-claims-adjudication-assistance) | [19](./19-rag-and-retrieval.md), [Case 01](./26-ai-use-case-catalog.md#case-01-document-q-and-a) |
| 2 | Steps are fixed and known | Deterministic workflow or state machine, LLM only in language steps | Testable, cheap, recoverable | Path truly varies and evals show workflow fails: bounded agent | [Case 14](./26-ai-use-case-catalog.md#case-14-workflow-automation-with-tools) |
| 3 | One LLM call is enough | Direct call through the model adapter; no framework | Fewest moving parts | Multi-step tool use needed: workflow, then agent | [23](./23-azure-foundry-standards.md) |
| 4 | A deterministic rule exists | Write code; no LLM | Exact, free, testable | Rule cannot be fully specified: LLM for fuzzy part, rule for the rest | [04](./04-engineering-principles.md) |
| 5 | Need routing or classification | Rules, then small classifier or LLM with fixed labels and confidence threshold | Reversible, measurable | Many overlapping intents: more evals, not more agents | [Case 08](./26-ai-use-case-catalog.md#case-08-classification-and-routing) |
| 6 | Long-running or multi-step jobs | Queue plus durable workflow with idempotent steps | Survives restarts and retries | Cross-system compensation needed: saga pattern with architecture review | [18](./18-reliability-and-operations.md) |
| 7 | Model lacks knowledge or style | Prompt first, then retrieval for knowledge, fine-tune last | Cheapest first; fine-tuning adds model-risk burden | Retrieval and prompting fail evals: governance review for fine-tuning | [15](./15-llm-and-model-governance.md) |
| 8 | Choose model tier | Smallest approved model that passes evals; larger only on eval evidence | Cost and latency | Quality gap on high-risk task: larger model plus human review | [15](./15-llm-and-model-governance.md) |
| 9 | Output feeds code | Schema-constrained output, validated (pydantic) | Prevents parsing failures and injection into code | Repeated validation failures: simplify schema, add fallback | [15](./15-llm-and-model-governance.md) |
| 10 | Interactive versus background | Synchronous for user waiting; queue for longer or bulk work | Latency and resilience | Volume or cost: batch, but only with an allowed deployment type | [23](./23-azure-foundry-standards.md), [Case 24](./26-ai-use-case-catalog.md#case-24-batch-and-offline-llm-pipelines) |
| 11 | Build or buy a capability | Foundry managed tools first (search, file, code interpreter), custom tool when needed | Less to operate; centrally governed | Capability outside Foundry: waiver and vendor approval | [12](./12-governance-and-compliance.md), [21](./21-exceptions-and-waivers.md) |
| 12 | Cache or recompute | Cache deterministic, non-personal lookups and embeddings; recompute personalized output | Cost without cross-user leakage | Cached data crosses classes: do not cache | [13](./13-data-classification-and-privacy.md) |
| 13 | Human review required | Always for: customer outcomes (coverage, pricing, underwriting, claims), destructive or external actions, Tier 1, low-confidence outputs | Accountability and harm limits | Volume makes review impractical: sample review only for low-risk actions with evals | [Case 23](./26-ai-use-case-catalog.md#case-23-human-in-the-loop-approval-flows), [12](./12-governance-and-compliance.md) |
| 14 | Use an orchestration framework | None by default; if needed evaluate Agent Framework or LangGraph and pin versions | Frameworks change quickly | Need hosting integration or durable state: ADR | [23](./23-azure-foundry-standards.md) |
| 15 | Per-user access in retrieval | Filter at retrieval with user identity; never rely on the prompt | Prevents data leakage | Complex entitlements: pre-filtered indexes per tenant or group | [19](./19-rag-and-retrieval.md) |
| 16 | Personal data present | Classify, minimize and complete PIA before model use | Privacy law and trust | Cross-border or Quebec transfer: Legal review | [13](./13-data-classification-and-privacy.md) |
| 17 | Choose Foundry agent type | Prompt agent if no custom code; hosted agent if custom code or orchestration; Responses API if definition ships with the app | Match control to need | Voice: voice-based prompt agent; networking decision at creation | [23](./23-azure-foundry-standards.md) |
| 18 | Expose an action to a model | Registered tool with manifest, least-privilege identity, limits; MCP where interoperability matters | Auditable and bounded | Destructive or external effects: approval in code | [25](./25-ai-tool-and-agent-registry.md) |
| 19 | Choose deployment type | `Standard` or `ProvisionedManaged` for personal data; Global and Data Zone only for non-personal data | Residency | Throughput limits: provisioned in-geography | [23](./23-azure-foundry-standards.md) |
| 20 | Several agents seem needed | One agent or workflow; multiple only for trust boundaries, context limits or independent parallel work | Cost and attack surface | Single-agent baseline fails evals: architecture and security review | [Case 22](./26-ai-use-case-catalog.md#case-22-multi-agent-systems) |
| 21 | Natural-language data queries | Curated views or semantic layer, read-only role, validated SQL shown to user | Limits exposure and error | Authoritative reporting: analyst-written queries | [Case 16](./26-ai-use-case-catalog.md#case-16-text-to-sql-data-analysis) |
| 22 | Extract fields from documents | OCR or document intelligence first, LLM for long tail, deterministic validation, human check on low confidence | Cheaper and more accurate | Fields drive decisions: human verification | [Case 07](./26-ai-use-case-catalog.md#case-07-document-extraction-and-ocr) |
| 23 | Summaries | Fixed output template with locators; label as machine-generated | Reduces omission; verifiable | Summary drives a decision: treat as Case 02 or 04 | [Case 09](./26-ai-use-case-catalog.md#case-09-summarization) |
| 24 | Fraud or risk scoring | Classical ML and rules for scoring; LLM only to read or explain | Calibrated, validated models | Adverse action: human investigation | [Case 11](./26-ai-use-case-catalog.md#case-11-fraud-and-anomaly-signals) |
| 25 | Customer-facing chat | Retrieval over approved content, read-only tools behind authentication, scripted handoff | Bounded harm | Write actions: workflow with approval | [Case 05](./26-ai-use-case-catalog.md#case-05-customer-service-assistant) |
| 26 | English and French output | Glossary-driven translation, bilingual evals, human review for customer-facing text | Terminology and legal accuracy | Contracts or notices: professional translation | [Case 18](./26-ai-use-case-catalog.md#case-18-translation-and-localization), [22](./22-localization-and-accessibility.md) |
| 27 | Score quality of outputs | Programmatic checks first; LLM-as-judge calibrated against human labels for the rest | Cheap and reliable | Judge disagrees with humans: more labels or human review | [14](./14-evals-and-testing-ai.md), [Case 21](./26-ai-use-case-catalog.md#case-21-evaluation-and-monitoring-agents) |
| 28 | AI coding assistants | Branch plus MR, tests first, approved tools only, no production credentials | Pipeline is the control | Access beyond a branch: security review | [Case 13](./26-ai-use-case-catalog.md#case-13-code-and-engineering-assistants), [01](./01-codebase-practices.md) |
| 29 | Personalization or recommendations | Rules or ranking on consented features; LLM for wording only | Fairness and consent | Pricing, coverage or suitability influence: Tier 1 | [Case 20](./26-ai-use-case-catalog.md#case-20-recommendation-and-personalization) |
| 30 | Voice interface | Managed voice-based prompt agent with narrow scope and human handoff | Less custom audio infrastructure | Identity verification or distress: human | [Case 19](./26-ai-use-case-catalog.md#case-19-voice-and-conversational-interfaces) |

## Checklist
- [ ] ADR cites the rows used and any deviation.
- [ ] Simplest viable step on the ladder chosen, with eval evidence for any higher step.
- [ ] Deterministic alternative considered and recorded.
- [ ] Human review conditions (row 13) mapped to enforcement in code.
- [ ] Data classification and PIA done before model use.
- [ ] Deployment type and model tier justified and consistent with 23 and 15.
- [ ] Escalations triggered by "when to escalate" recorded with approver.

## Common AI failure modes
- Reaching for an agent framework for a one-call task.
- Choosing vector RAG by default when the documents have clear structure.
- Making the "agent" decide a path that is the same every time.
- Using the largest model because it "feels safer" without eval evidence.
- Relying on prompt wording for permissions or approval.
- Caching a personalized answer and serving it to another user.
- Reading a table row as a rule that overrides the high-risk constraints in the catalog.
- Treating the playbook as complete and not consulting the catalog case.

## Related docs
- [26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md): per-use-case depth.
- [04-engineering-principles.md](./04-engineering-principles.md): simple-first, autonomy ladder.
- [15-llm-and-model-governance.md](./15-llm-and-model-governance.md): models and prompts.
- [23-azure-foundry-standards.md](./23-azure-foundry-standards.md): Foundry platform mechanics.
- [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md): tools and agents.
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md): data gates.
- [19-rag-and-retrieval.md](./19-rag-and-retrieval.md): retrieval.
- [12-governance-and-compliance.md](./12-governance-and-compliance.md): tiers and approvals.
