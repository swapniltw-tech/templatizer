# AI Use-Case Catalog

> **Owner:** AI governance lead with Platform Engineering lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview), [Foundry guardrails](https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview), [Foundry deployment types](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types), [MCP specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28), [A2A specification](https://a2a-protocol.org/latest/specification/), OSFI guidelines E-23, B-10 and B-13 (VERIFY on osfi-bsif.gc.ca)

## Purpose
This catalog gives **direction for ADRs, not code**. It extends [05-decision-playbook.md](./05-decision-playbook.md) (the compact table) with 24 cases. For a real use case, find the closest case, copy its template into `docs/use-cases/<case>.md`, answer its ADR prompts, and record the decision in an ADR ([03-architecture.md](./03-architecture.md)). The catalog is guidance for choosing an approach; it does not replace intake and risk tiering in [12-governance-and-compliance.md](./12-governance-and-compliance.md).

Conventions used in every case:
- **Autonomy rung** identifiers are the canonical ones from [04-engineering-principles.md](./04-engineering-principles.md): `suggest` (0), `assist-read` (1), `propose` (2, acts only after a human approves each action), `act-low-risk` (3, acts alone on allow-listed low-risk reversible actions with sampled review), `act-bounded` (4), `autonomous` (5, not used here).
- **Data classes** are those in [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md): public, internal, confidential, restricted. **PIA trigger** means a privacy impact assessment is required before production when personal information reaches a model.
- **Risk tier** follows [12-governance-and-compliance.md](./12-governance-and-compliance.md): Tier 1 (high), Tier 2 (medium), Tier 3 (low). Tiers here are defaults; the owner and AI governance confirm them at intake.
- **Evals** reference datasets and thresholds owned by [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md); thresholds are not set here.
- **Regulatory notes** are guidance, not legal advice. Dates and clauses are `VERIFY:` against primary text; internal policy names are open item F1.
- Models are placeholders (`<chat-deployment>`); approved models are open item F2.

## Rules

### Using the catalog
- **UCS-001** [MUST] [review] Every production AI use case MUST have `docs/use-cases/<case>.md` copied from the template below and linked from its ADR.
- **UCS-002** [MUST] [review] The ADR MUST answer every ADR prompt of the matching case or state "not applicable" with a reason.
- **UCS-003** [MUST] [review] If a use case spans several cases, the ADR MUST apply the strictest autonomy rung and the union of evals and threats; if none match, the ADR MUST justify the closest case and propose a new case through an MR to this doc.
- **UCS-004** [MUST] [review] The ADR MUST record why a deterministic or classical-ML solution is insufficient before an LLM is chosen ([04-engineering-principles.md](./04-engineering-principles.md)).
- **UCS-005** [SHOULD] [review] Start at the lowest autonomy rung and move up only with eval evidence that meets the thresholds for the next rung ([14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md)).
- **UCS-006** [MUST] [review] The case record MUST list data classes reaching the model and MUST show the PIA status; a PIA MUST be complete before personal information is sent to a model in production ([13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)).
- **UCS-007** [MUST] [review] Customer-facing cases MUST test English and French and state the locale behavior ([22-localization-and-accessibility.md](./22-localization-and-accessibility.md)).
- **UCS-008** [MUST] [ci: make registry-check] Tools and agents named in a case record MUST have manifests ([25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md)).
- **UCS-009** [MUST] [review] A person who owns the use case MUST confirm the regulatory notes in the case record; an AI agent drafting the record MUST NOT mark them confirmed.
- **UCS-010** [SHOULD] [manual] The catalog SHOULD be reviewed at least every six months and after any change of approved models, and `VERIFY:` markers MUST stay until confirmed.

### High-risk cases
- **UCS-011** [MUST] [review] A use case is **high-risk** (Tier 1) when it influences coverage, pricing, underwriting or claims outcomes, takes an autonomous action affecting a customer, or processes restricted data to produce a customer-specific outcome. Cases 02, 04, 11 and 20 default to high-risk; others become high-risk when they meet this test.
- **UCS-012** [MUST] [review] For high-risk cases a human MUST make and record the decision; the AI output MUST be labelled decision support and MUST NOT autonomously deny, rescind, reprice or approve.
- **UCS-013** [MUST] [review] High-risk cases MUST NOT go beyond a prototype without AI governance sign-off, a bias and fairness assessment, an independent review and a revalidation schedule ([12-governance-and-compliance.md](./12-governance-and-compliance.md)).
- **UCS-014** [MUST] [review] High-risk cases MUST NOT run above `propose` and SHOULD run at `suggest`; any higher rung needs a waiver ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)).
- **UCS-015** [MUST] [test] High-risk cases MUST log, for each output, the model version, prompt hash, inputs by reference, source citations and the human reviewer's decision ([10-logging-observability.md](./10-logging-observability.md)).
- **UCS-016** [MUST] [review] The ADR for a high-risk case MUST describe the human review design: what the reviewer sees, how disagreement with the AI is recorded, and how automation bias is measured (for example override rate and time to decision).

## Case template
Copy this into `docs/use-cases/<case>.md`.
```
# <Case name>
- Name:
- When it applies (signals):
- Recommended pattern:
- Why:
- Alternatives and when to escalate:
- Autonomy rung:
- Data classes and PIA trigger:
- Evals required:
- Security threats:
- Regulatory notes:
- Failure modes:
- ADR prompts:
- Sources:
```

## Baseline for all cases
These apply to every case and are not repeated below.
- Calls go through the Foundry adapter ([23-azure-foundry-standards.md](./23-azure-foundry-standards.md)); models pinned ([15-llm-and-model-governance.md](./15-llm-and-model-governance.md)).
- Untrusted text (user input, documents, tool output) is data, never instructions ([02-security.md](./02-security.md)).
- Outputs consumed by code are schema-validated; failure falls back to a human queue.
- Personal data is minimized, redacted from logs and traces, and never in tests ([13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)).
- Evals use synthetic or properly governed data and gate releases ([14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md)).

## Customer and claims cases

### Case 01 Document Q and A
- **Name:** Document question answering over policies and contracts.
- **When it applies (signals):** Staff or customers ask questions whose answers are in long, mostly static documents (policy wordings, product guides, contracts); answers must be traceable.
- **Recommended pattern:** Retrieval-augmented generation with structured or section-aware retrieval first (headings, clause ids, metadata filters), vector search only where structure is weak; answer with quoted citations and "not found" as a valid output ([19-rag-and-retrieval.md](./19-rag-and-retrieval.md)).
- **Why:** Structure gives exact, auditable retrieval; citations let a reader verify; refusing when evidence is missing limits fabrication.
- **Alternatives and when to escalate:** Plain keyword search if users only need to find documents. Add vector retrieval when queries are paraphrased and structure is missing. Escalate to a human-reviewed workflow if answers feed a coverage decision (becomes Case 02 or 04).
- **Autonomy rung:** `suggest`.
- **Data classes and PIA trigger:** Internal to confidential documents; customer-specific contracts are confidential or restricted. PIA when personal information is in the index or prompts.
- **Evals required:** Retrieval hit rate on a golden question set; answer faithfulness to citations; "not found" correctness; EN and FR parity; document-level access test (user without rights gets nothing).
- **Security threats:** Indirect prompt injection in documents; document-level access bypass; sensitive information disclosure across users; index poisoning.
- **Regulatory notes:** Default Tier 3 for internal policy lookup; Tier 2 when customer-facing or personal data is involved; customer-facing answers about coverage may be treated as advice (VERIFY with Compliance).
- **Failure modes:** Confident answer from the wrong version of a policy; stale index; citation that does not support the claim; answering from outside the retrieved set.
- **ADR prompts:** Which document versions are authoritative and how is freshness handled? What is the access-control model at retrieval? What does the system answer when evidence is missing? How are citations verified?
- **Sources:** [19-rag-and-retrieval.md](./19-rag-and-retrieval.md); Foundry Agent Service overview (knowledge tools).

### Case 02 Underwriting support
- **Name:** Underwriting support (summarize, extract, flag).
- **When it applies (signals):** Underwriters review applications, medical evidence and financial information and want summaries, extracted facts and flagged inconsistencies.
- **Recommended pattern:** Extraction and summarization with per-fact source references, plus rule-based flags from the underwriting guidelines; the underwriter decides. LLM output never produces the decision or the premium.
- **Why:** Keeps the decision and accountability with a licensed human while saving reading time; references make review quick.
- **Alternatives and when to escalate:** Deterministic rules engine for guideline checks (preferred where rules exist). Classical ML for risk scoring is a separate model-risk item (Case 11 pattern). Never escalate to automated decisions without a waiver and governance approval.
- **Autonomy rung:** `suggest`.
- **Data classes and PIA trigger:** Restricted (health, financial, identity). PIA required; Quebec transfer test applies (13).
- **Evals required:** Extraction accuracy per field against labelled synthetic cases; omission rate for critical facts; flag precision and recall; bias and fairness checks across protected-attribute proxies; reviewer agreement and override rate.
- **Security threats:** Prompt injection in submitted documents; leakage of restricted data into logs; model inferring or using protected attributes; over-reliance (automation bias).
- **Regulatory notes:** High-risk (Tier 1) by default because it influences underwriting outcomes. Fairness and human-rights considerations apply (VERIFY with Compliance and Legal). Model risk guidance (E-23) applies to AI/ML models (VERIFY scope and effective date). Quebec automated-decision disclosure obligations (VERIFY).
- **Failure modes:** Missed adverse fact; fabricated fact with plausible source; summary omits a contradiction; underwriters rubber-stamp.
- **ADR prompts:** Which decisions stay deterministic? What does the underwriter see and what is logged as their decision? How is bias tested? What is the fallback if the model is unavailable? Who revalidates and when?
- **Sources:** [12-governance-and-compliance.md](./12-governance-and-compliance.md); [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md); OSFI E-23 (VERIFY).

### Case 03 Claims intake and triage
- **Name:** Claims intake and triage (classify, extract, route).
- **When it applies (signals):** High volumes of claim submissions need classification, key-field extraction and routing to queues or priorities.
- **Recommended pattern:** Deterministic workflow: extraction step, classification step with a fixed label set, confidence threshold, then routing rules; low confidence goes to a human queue. LLM never decides coverage and never communicates with the claimant.
- **Why:** Fixed steps are testable and auditable; routing errors are recoverable because a human handles the claim next.
- **Alternatives and when to escalate:** Rules or a small classifier if labels are few and stable. Escalate to Case 04 if the output starts to propose coverage or payment outcomes.
- **Autonomy rung:** `propose` by default (a human confirms each routing before it takes effect), because routing and priority decide who handles a claim and how soon (PRN-018 caps decision-affecting agents at `propose`). `act-low-risk` for routing within a fixed queue set only if AI governance classifies the use as Tier 2 (ASSUMPTION F1) and routing cannot delay urgent claims.
- **Data classes and PIA trigger:** Confidential to restricted (claim details, health data). PIA required.
- **Evals required:** Label accuracy and per-class recall (especially urgent and complex classes); extraction field accuracy; misroute cost-weighted score; EN and FR; confidence calibration.
- **Security threats:** Prompt injection via claim attachments; manipulation of urgency; data leakage via logs; bypass of the human-queue threshold.
- **Regulatory notes:** Default **Tier 1** when routing or priority affects claim handling order or timelines (UCS-011); Tier 2 only if a human confirms every routing or routing cannot affect timelines, as decided by AI governance (ASSUMPTION F1). Escalates further if triage affects claim outcomes or timelines unfairly (VERIFY with Compliance on claims-handling timelines and fair treatment obligations).
- **Failure modes:** Urgent claim classed as routine; systematic misrouting for one language or channel; silent drift in label distribution.
- **ADR prompts:** What is the fixed label set and who owns it? What confidence threshold sends work to a human, and how is it tuned? How is queue delay monitored? What happens when the model is down?
- **Sources:** Foundry Agent Service overview; [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md).

### Case 04 Claims adjudication assistance
- **Name:** Claims adjudication assistance (decision support only).
- **When it applies (signals):** Adjudicators need help assembling facts, checking policy terms and drafting rationale for a coverage or payment decision.
- **Recommended pattern:** Retrieval of the claim file and policy terms (Case 01 pattern) producing a fact sheet, clause references and a draft rationale; the adjudicator reviews, edits and decides. No autonomous denial, rescission or payment.
- **Why:** The decision carries legal and customer consequences; assistance reduces effort while a person remains accountable.
- **Alternatives and when to escalate:** Deterministic rules for clear-cut eligibility checks. Do not escalate to autonomous decisions; any proposal needs a waiver, governance approval and legal review.
- **Autonomy rung:** `suggest`.
- **Data classes and PIA trigger:** Restricted. PIA required; Quebec transfer test applies.
- **Evals required:** Fact extraction accuracy; clause-reference correctness; omission of material facts; rationale faithfulness to evidence; bias and fairness; reviewer override rate and time to decision; adversarial documents.
- **Security threats:** Prompt injection in claim documents; fabricated clause citations; leakage of restricted data; adjudicator over-reliance; tampering with the draft rationale.
- **Regulatory notes:** High-risk (Tier 1). A decision with legal effect needs explainability and a human decision record (VERIFY with Legal and Compliance; Quebec automated-decision disclosure rules, VERIFY). Complaints and appeal processes depend on the rationale being the adjudicator's own.
- **Failure modes:** Plausible but wrong clause reference; draft rationale anchors the adjudicator; important fact omitted; adjudicator copies draft without reading.
- **ADR prompts:** Which fields and clauses must be cited? How is the human decision captured separately from the AI draft? How is automation bias measured? Which decisions never use AI? What audit trail is retained?
- **Sources:** [12-governance-and-compliance.md](./12-governance-and-compliance.md); [19-rag-and-retrieval.md](./19-rag-and-retrieval.md); OSFI E-23 (VERIFY).

### Case 05 Customer service assistant
- **Name:** Customer service assistant (chat).
- **When it applies (signals):** Customers ask routine questions about policies, billing, status and forms through chat; some need a human.
- **Recommended pattern:** Retrieval over approved content (Case 01) plus a small set of read-only tools for account status behind authentication; clear AI disclosure; scripted escalation to a human on trigger topics (complaints, distress, vulnerability, legal, coverage disputes).
- **Why:** Bounded content and tools limit harm; a visible escape hatch protects customers and the business.
- **Alternatives and when to escalate:** FAQ search or a decision tree if questions are few. Escalate to a human immediately for complaints or sensitive topics. Write actions (address change, claim submission) move to Case 14 with approval.
- **Autonomy rung:** `suggest` for answers drafted to staff; `act-low-risk` for read-only answers to customers with citations, once evals pass.
- **Data classes and PIA trigger:** Confidential to restricted if account data is shown. PIA required; Quebec transfer test applies.
- **Evals required:** Answer faithfulness and citation validity; refusal and escalation correctness; EN and FR parity; prompt-injection and jailbreak suite; tone; harmful-content handling.
- **Security threats:** Prompt injection from the customer; leakage of another customer's data; social engineering for account access; excessive agency if tools are added.
- **Regulatory notes:** Default Tier 2. Disclosure that the customer is interacting with AI and complaint handling obligations (VERIFY with Compliance). French service obligations (VERIFY, F6).
- **Failure modes:** Answers outside approved content; fails to escalate a vulnerable customer; mixes up customers' sessions; inconsistent EN and FR answers.
- **ADR prompts:** What content is in scope and who approves it? What triggers a handoff and how is context passed? How is the customer authenticated before any account data is shown? What is the French behavior? How are conversations retained?
- **Sources:** [22-localization-and-accessibility.md](./22-localization-and-accessibility.md); [02-security.md](./02-security.md).

### Case 06 Call centre agent assist
- **Name:** Agent assist for the call centre (summaries and next-best-action).
- **When it applies (signals):** Staff handle calls or chats and want real-time suggestions, after-call summaries and next-step prompts.
- **Recommended pattern:** Staff-facing suggestions only: retrieval of approved scripts and policies, post-call summary drafted for the agent to edit, next-best-action chosen from a fixed list by rules with the LLM only phrasing or ranking.
- **Why:** The human stays in the loop live; fixed action lists prevent invention of offers or promises.
- **Alternatives and when to escalate:** Rules-based prompts from the CRM for simple cases. Escalate to Tier 1 review if suggestions influence coverage, retention pricing or complaint outcomes (Case 20 pattern).
- **Autonomy rung:** `suggest`.
- **Data classes and PIA trigger:** Confidential to restricted; call audio and transcripts are personal information. PIA required; consent and recording notice depend on policy (VERIFY with Legal).
- **Evals required:** Summary faithfulness and omission of commitments; action-list correctness; latency budget in live use; EN and FR; agent acceptance and edit rate.
- **Security threats:** Prompt injection spoken or typed by the caller; transcript leakage; suggestions that disclose other customers' data.
- **Regulatory notes:** Default Tier 2. Recording and consent obligations and retention of transcripts (VERIFY with Legal; see 13).
- **Failure modes:** Summary records a promise the agent did not make; suggestion arrives too late; agents stop listening to the customer.
- **ADR prompts:** What is the latency budget? Which actions are allowed to be suggested? How are summaries reviewed and stored? How is the customer notified?
- **Sources:** [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md); [10-logging-observability.md](./10-logging-observability.md).

### Case 07 Document extraction and OCR
- **Name:** Document extraction and OCR to structured data.
- **When it applies (signals):** Forms, medical reports, statements and scans must become structured fields for downstream systems.
- **Recommended pattern:** Layout-aware OCR or document-intelligence step first, then schema-constrained LLM extraction only for fields OCR cannot parse; validate with deterministic checks (formats, checksums, cross-field rules); low-confidence fields go to human verification.
- **Why:** Deterministic extraction is cheaper and more testable; the LLM handles the long tail; validation catches hallucinated values.
- **Alternatives and when to escalate:** Template-based or form-recognizer-style extraction for fixed forms. Escalate to a human data-entry step when field-level confidence is below threshold or the field drives a decision.
- **Autonomy rung:** `act-low-risk` for low-impact fields with validation; `suggest` for fields feeding underwriting or claims.
- **Data classes and PIA trigger:** Confidential to restricted (medical, financial, identity). PIA required.
- **Evals required:** Field-level accuracy, precision and recall on a labelled synthetic set including poor scans; confidence calibration; handling of handwriting and languages; hallucinated-field rate.
- **Security threats:** Malicious documents with embedded instructions; PII leakage in traces; file-type attacks on parsers (see 02).
- **Regulatory notes:** Tier depends on downstream use (Tier 2 default; Tier 1 if it feeds a decision unreviewed). Retention of source documents and extracted data (VERIFY with 13).
- **Failure modes:** Digit transposition passes format checks; fields inferred rather than read; table rows merged; silent drop of a page.
- **ADR prompts:** Which fields are critical and require human verification? What validation rules exist? How are confidence thresholds set? How are source pages linked to each field?
- **Sources:** [17-api-and-contracts.md](./17-api-and-contracts.md); [24-testing-standards.md](./24-testing-standards.md).

### Case 08 Classification and routing
- **Name:** Classification and routing (email, tickets, documents).
- **When it applies (signals):** Items arrive in free text and must be labelled or sent to the right team.
- **Recommended pattern:** Start with rules and keywords; add a small classifier or an LLM with a fixed label set and confidence threshold; log labels and overrides to retrain and monitor.
- **Why:** Routing is bounded and reversible; a closed label set is easy to test and monitor.
- **Alternatives and when to escalate:** Classical ML (logistic regression, gradient boosting) when labelled data exists and cost or latency matters. Escalate to a human triage queue for low confidence or sensitive labels (complaints, legal).
- **Autonomy rung:** `act-low-risk`.
- **Data classes and PIA trigger:** Internal to confidential. PIA if personal information is in the text.
- **Evals required:** Per-class precision and recall; confusion on sensitive classes; drift over time; EN and FR.
- **Security threats:** Prompt injection in message bodies steering the label; label-flooding attacks; leakage in logs.
- **Regulatory notes:** Default Tier 3 to Tier 2; complaints must not be misrouted (VERIFY with Compliance on complaint-handling obligations).
- **Failure modes:** New topics misfiled into "other"; label set grows without owners; cost grows with volume when rules would do.
- **ADR prompts:** What is the closed label set and who owns changes? What is the cost per item versus a classical model? How are overrides captured?
- **Sources:** [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md).

### Case 09 Summarization
- **Name:** Summarization (meetings, case notes, long documents).
- **When it applies (signals):** People need shorter versions of long material for reading or hand-off.
- **Recommended pattern:** Map-reduce or chunked summarization with a fixed output template (decisions, actions, risks); include quotes or locators; label the output as machine-generated and keep the source linked.
- **Why:** Templates reduce omission and drift; locators let readers verify.
- **Alternatives and when to escalate:** Extractive highlights when exactness matters. Escalate to Case 02 or 04 handling if the summary drives a decision.
- **Autonomy rung:** `suggest`.
- **Data classes and PIA trigger:** Varies; case notes and meetings often contain confidential or restricted data. PIA if personal information.
- **Evals required:** Faithfulness (no unsupported claims); coverage of required sections; omission of commitments and numbers; EN and FR; length control.
- **Security threats:** Prompt injection inside source text; leakage of restricted details into broader distribution; summaries stored without the source's access controls.
- **Regulatory notes:** Summary inherits the source's classification and retention; case notes may be records subject to retention (VERIFY with 13).
- **Failure modes:** Invented action items; dropped negative facts; wrong attribution of statements; summary read in place of the source.
- **ADR prompts:** Which sections are mandatory? How is the summary access-controlled and retained? Who may rely on it for decisions?
- **Sources:** [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md).

### Case 10 Compliance and policy checking
- **Name:** Compliance and policy checking (rules plus LLM).
- **When it applies (signals):** Documents, communications or processes must be checked against policies, regulations or checklists.
- **Recommended pattern:** Deterministic rules for everything expressible as a rule; LLM only for fuzzy interpretation, returning a finding with the clause cited and a confidence; findings go to a compliance reviewer.
- **Why:** Rules are explainable and testable; the LLM extends coverage without becoming the control.
- **Alternatives and when to escalate:** Pure rules engine when policies are formalizable. Escalate to Compliance review for any "fail" outcome; the LLM must not be the sole control for a regulatory obligation.
- **Autonomy rung:** `suggest`.
- **Data classes and PIA trigger:** Internal to restricted depending on what is checked. PIA if personal information.
- **Evals required:** Recall on seeded violations; false-positive rate and reviewer load; clause-citation accuracy; stability across model versions.
- **Security threats:** Prompt injection to hide a violation; reviewers trusting a clean result; leakage of policy details.
- **Regulatory notes:** An AI check does not discharge a regulatory obligation; accountable owners remain (see 12). VERIFY with Compliance before relying on it as a control.
- **Failure modes:** Missed violation presented as "no findings"; policy version mismatch; reviewer fatigue from false positives.
- **ADR prompts:** Which checks are rules and which fuzzy? What is the policy source of truth and version? How is the miss rate measured on seeded cases?
- **Sources:** [12-governance-and-compliance.md](./12-governance-and-compliance.md).

### Case 11 Fraud and anomaly signals
- **Name:** Fraud and anomaly signals (classical ML versus LLM).
- **When it applies (signals):** Detecting suspicious claims, applications or transactions from structured and unstructured data.
- **Recommended pattern:** Classical ML and rules on structured features as the scoring engine; an LLM, if used at all, summarizes or explains a flagged case or extracts signals from text for an investigator; investigators decide.
- **Why:** Scoring needs calibrated, validated models and monitoring; LLMs are unstable scorers but useful readers.
- **Alternatives and when to escalate:** Rules and graph analytics for known patterns. Escalate any adverse action on a customer to a human investigation with documented evidence.
- **Autonomy rung:** `suggest`.
- **Data classes and PIA trigger:** Confidential to restricted. PIA required; investigative data may carry extra restrictions (VERIFY with Legal).
- **Evals required:** Precision and recall at the working threshold; false-positive harm; fairness across groups; drift; stability of explanations; adversarial attempts to evade.
- **Security threats:** Adversaries probing the detector; prompt injection in claim text; leakage of detection logic.
- **Regulatory notes:** High-risk (Tier 1) by default because flags can lead to adverse treatment. Model risk management (E-23) applies to ML as well as LLMs (VERIFY scope). Fair-treatment concerns (VERIFY with Compliance).
- **Failure modes:** Bias against a group via proxies; LLM explanation sounds convincing but is not the real reason; alert fatigue.
- **ADR prompts:** What is the ML model of record and its validation? What does the LLM add and how is it evaluated separately? What adverse actions follow a flag and who decides? How is bias monitored?
- **Sources:** [12-governance-and-compliance.md](./12-governance-and-compliance.md); [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md).

## Internal productivity and engineering cases

### Case 12 Internal knowledge assistant
- **Name:** Internal knowledge assistant and enterprise search.
- **When it applies (signals):** Staff search across wikis, procedures and tickets and want answers with sources.
- **Recommended pattern:** Search-first: keyword and metadata retrieval across approved sources with per-user access filtering; LLM answers with citations; source freshness shown.
- **Why:** Access control and freshness are the main risks in enterprise search; a retrieval layer enforces them before the model sees data.
- **Alternatives and when to escalate:** Plain enterprise search when answers are not needed. Escalate to a narrower, curated knowledge base when sources conflict.
- **Autonomy rung:** `suggest`.
- **Data classes and PIA trigger:** Internal to confidential; sources may contain personal data. PIA if personal information is indexed.
- **Evals required:** Retrieval recall; answer faithfulness; access-control tests per role; staleness detection; "I do not know" rate.
- **Security threats:** Over-sharing via broad indexing; indirect prompt injection from wiki pages; data exfiltration through crafted queries.
- **Regulatory notes:** Default Tier 3; Tier 2 if used for operational decisions. Confidential data must stay within approved boundaries (see 13).
- **Failure modes:** Answers from outdated pages; reveals documents the user could not open directly; conflicting sources merged.
- **ADR prompts:** Which sources are indexed and who owns each? How are permissions mirrored and refreshed? How are conflicts and staleness shown?
- **Sources:** [19-rag-and-retrieval.md](./19-rag-and-retrieval.md).

### Case 13 Code and engineering assistants
- **Name:** Code and engineering assistants (SDLC, internal tools, MCP).
- **When it applies (signals):** Engineers or AI coding agents write code, tests, infrastructure and docs, possibly with MCP tools.
- **Recommended pattern:** Assistants operate on branches with merge requests, tests-first, pre-merge CI gates and human review; tool access via approved MCP servers only, least-privilege and deny-by-default; no production credentials.
- **Why:** The review and CI pipeline are the controls; limiting tools and secrets limits blast radius.
- **Alternatives and when to escalate:** Template generators (Copier) for repeatable scaffolds. Escalate to security review when an assistant needs write access beyond a branch or access to secrets or production.
- **Autonomy rung:** `propose` for command execution outside the sandbox; `act-low-risk` inside a sandboxed workspace producing MRs.
- **Data classes and PIA trigger:** Internal (source code); never confidential or restricted data. PIA not usually triggered if no personal data; confirm.
- **Evals required:** Task success on representative repo tasks; policy compliance (no test weakening, no secret writes); dependency hallucination checks; security scan results on generated code.
- **Security threats:** Prompt injection via repositories, issues and MCP tool output; malicious or hallucinated packages; over-privileged tokens; tool-description poisoning.
- **Regulatory notes:** Generated code is subject to change management and third-party risk (see 12 and 20); licensing review applies.
- **Failure modes:** Tests weakened to pass; fabricated package names; secrets copied to prompts; unreviewed merges.
- **ADR prompts:** Which tools and MCP servers are approved? What can the agent run and where? How is self-approval prevented? How is generated code identified and reviewed?
- **Sources:** [01-codebase-practices.md](./01-codebase-practices.md); [02-security.md](./02-security.md); [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md); MCP specification.

### Case 14 Workflow automation with tools
- **Name:** Workflow automation with tools (workflow versus agent).
- **When it applies (signals):** A business process has several steps, some needing language understanding, with actions in other systems.
- **Recommended pattern:** Deterministic workflow or state machine with LLM steps only where language understanding is needed; each action is a registered tool with idempotency; human approval before external or destructive actions; durable execution for long-running flows.
- **Why:** Fixed steps are testable and recoverable; an agent loop adds cost and unpredictability when the path is known.
- **Alternatives and when to escalate:** A simple script or RPA if no language steps. Escalate to a bounded agent only when the path genuinely varies (see Case 15) and evals show the workflow cannot cover it.
- **Autonomy rung:** `propose` for write and external actions; `act-low-risk` for read-only steps and idempotent internal updates.
- **Data classes and PIA trigger:** Depends on systems touched; often confidential. PIA if personal information is processed by the model.
- **Evals required:** Step-level and end-to-end success on scenarios; tool-argument validity; idempotent retry behavior; failure-injection tests; cost per run.
- **Security threats:** Excessive agency; tool misuse through injected instructions; confused-deputy via shared credentials; duplicated side effects on retry.
- **Regulatory notes:** Actions on customer records are auditable (see 12); customer-affecting actions raise tier to Tier 1 or Tier 2 depending on impact.
- **Failure modes:** Partial completion with no rollback; retry duplicates an action; agent invents a step; approval skipped.
- **ADR prompts:** Which steps need a model? Which actions need approval? How is each step made idempotent and observable? What is the rollback path?
- **Sources:** [18-reliability-and-operations.md](./18-reliability-and-operations.md); [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md).

### Case 15 Multi-step research agents
- **Name:** Multi-step research and analysis agents (bounded autonomy).
- **When it applies (signals):** A question needs several searches, reads and syntheses where the path cannot be fixed in advance.
- **Recommended pattern:** A single agent with a small, read-only tool set, hard limits on steps, tokens, time and cost, a written plan and cited findings; a human reviews the report; no write tools.
- **Why:** Bounded loops limit cost and risk while allowing exploration; read-only tools cap the damage of injection.
- **Alternatives and when to escalate:** A fixed multi-step workflow (Case 14) if steps are predictable. Escalate to Case 22 only after a single agent fails evals for a clear reason.
- **Autonomy rung:** `act-low-risk` within read-only limits; outputs are `suggest`.
- **Data classes and PIA trigger:** Up to internal and confidential; avoid restricted data. PIA if personal information is retrieved.
- **Evals required:** Task completion and citation validity on a golden task set; budget adherence; behavior under injected content in sources; reproducibility variance across runs.
- **Security threats:** Indirect prompt injection from web or document content; data exfiltration via tool calls; runaway loops; poisoned sources.
- **Regulatory notes:** Default Tier 3 to Tier 2; research output used in decisions is reviewed by the owner (see 12).
- **Failure modes:** Plausible but unsupported synthesis; stuck loop burning budget; reliance on low-quality sources.
- **ADR prompts:** What limits bound the loop? What sources are allowed? How are claims tied to evidence? Who reviews the report?
- **Sources:** [04-engineering-principles.md](./04-engineering-principles.md); [02-security.md](./02-security.md).

### Case 16 Text to SQL data analysis
- **Name:** Data analysis and text-to-SQL (read-only, schema-scoped).
- **When it applies (signals):** Analysts or staff want answers from governed data using natural language.
- **Recommended pattern:** Semantic layer or curated views; the model proposes SQL only against an allow-listed schema through a read-only role; queries are validated (parse, allow-list tables and functions, row and time limits) and shown to the user; results are not sent back to the model unless classified for it.
- **Why:** A semantic layer constrains ambiguity; read-only roles and validation limit damage and data exposure.
- **Alternatives and when to escalate:** Pre-built dashboards or parameterized reports when questions repeat. Escalate to analyst-written SQL when accuracy must be certain.
- **Autonomy rung:** `suggest` (user sees and runs the query); `act-low-risk` only for approved read-only views.
- **Data classes and PIA trigger:** Depends on schema; restrict to non-restricted views by default. PIA if personal information columns are reachable.
- **Evals required:** Query correctness on a labelled question set; refusal outside scope; row-level and column-level access tests; resource-limit tests; result accuracy.
- **Security threats:** Injection producing destructive or exfiltrating SQL; access to unauthorized columns; expensive queries; leaking results into logs.
- **Regulatory notes:** Reports used for regulatory or financial reporting need controls beyond this pattern (VERIFY with Finance and Compliance); data lineage matters.
- **Failure modes:** Wrong join gives a confident wrong number; hidden filter changes meaning; stale view; users trust unexplained results.
- **ADR prompts:** Which views and columns are exposed? How is the role limited? How are numbers explained and verified? What resource limits apply?
- **Sources:** [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md); [02-security.md](./02-security.md).

### Case 17 Content generation and communications
- **Name:** Content generation and communications (letters, emails).
- **When it applies (signals):** Staff draft letters, emails or notices, possibly personalized, in English and French.
- **Recommended pattern:** Template-first generation: approved templates with variable slots filled from structured data; the LLM edits tone or fills narrative parts within constraints; mandatory human review and approval before sending; checks for prohibited claims and required disclosures.
- **Why:** Regulated communications need approved wording; templates keep control with the business.
- **Alternatives and when to escalate:** Pure templates when personalization is limited. Escalate to compliance review for new template families or any content about coverage, rights or complaints.
- **Autonomy rung:** `suggest` (draft) or `propose` (send after approval).
- **Data classes and PIA trigger:** Confidential to restricted if personal details are in the letter. PIA required.
- **Evals required:** Fidelity to the template and facts; prohibited-claim detection; EN and FR quality and parity; tone and readability; no leakage of other customers' data.
- **Security threats:** Prompt injection from incoming correspondence being replied to; sending to the wrong recipient; disclosure of confidential facts.
- **Regulatory notes:** Customer communications may be subject to prescribed content and language rules (VERIFY with Compliance; F6 for Quebec). Retain the approved version.
- **Failure modes:** Invented commitment; wrong tone with a distressed customer; French that is literal and unnatural; template drift.
- **ADR prompts:** What templates exist and who approves them? What may the model change? Who approves sends? How are EN and FR versions validated?
- **Sources:** [22-localization-and-accessibility.md](./22-localization-and-accessibility.md).

### Case 18 Translation and localization
- **Name:** Translation and localization (English and French).
- **When it applies (signals):** Content or conversations must exist in both official languages, including Quebec French expectations.
- **Recommended pattern:** Glossary-driven translation with approved terminology, a translation memory for reuse, LLM translation as a first draft, and human review for customer-facing or legal content; machine-only for internal low-risk text.
- **Why:** Terminology consistency and legal accuracy matter more than fluency; reuse reduces cost and variance.
- **Alternatives and when to escalate:** Professional translators for contracts, policy wording and regulatory notices. Escalate to certified translation where required.
- **Autonomy rung:** `suggest` for customer-facing; `act-low-risk` for internal low-risk.
- **Data classes and PIA trigger:** Depends on content; personal data triggers a PIA.
- **Evals required:** Terminology adherence; semantic fidelity (back-translation checks are weak, so use bilingual reviewers); Quebec French style; numerals, dates and currency formats.
- **Security threats:** Prompt injection inside content; leakage of confidential text to non-approved services.
- **Regulatory notes:** Quebec language requirements apply to customer-facing documents (VERIFY with Legal; F6). Contract language rules (VERIFY).
- **Failure modes:** Meaning drift in clauses; anglicisms; wrong register; inconsistent terms across documents.
- **ADR prompts:** What is the glossary source and owner? Which content needs human or certified review? How are Quebec expectations tested?
- **Sources:** [22-localization-and-accessibility.md](./22-localization-and-accessibility.md).

### Case 19 Voice and conversational interfaces
- **Name:** Voice and conversational interfaces.
- **When it applies (signals):** Customers or staff speak to a system by phone or microphone.
- **Recommended pattern:** Use the managed voice-based prompt agent path where Foundry supplies speech recognition, turn-taking and synthesis; keep the dialogue narrow (Case 05 scope), with clear handoff to a human and call recording policy applied. VERIFY: voice features and preview opt-ins on Learn before design; some voice features are preview.
- **Why:** Voice adds latency and recognition error; a narrow scope and handoff limit harm; a managed path reduces custom audio infrastructure.
- **Alternatives and when to escalate:** IVR menus or callbacks for simple needs. Escalate to a human for identity verification failures, distress or ambiguity.
- **Autonomy rung:** `suggest` or `act-low-risk` for read-only information.
- **Data classes and PIA trigger:** Voice is personal information; transcripts are confidential to restricted. PIA required.
- **Evals required:** Word error rate on representative accents in English and French; intent accuracy; latency; barge-in and interruption handling; escalation correctness; adversarial audio.
- **Security threats:** Voice spoofing and social engineering; spoken prompt injection; recording leakage; misrecognized identifiers.
- **Regulatory notes:** Recording notice, consent and biometric considerations (VERIFY with Legal and Privacy). Voice monitoring and evaluation have limitations (single-turn and simulated evaluation not supported for voice agents per Learn at verification; VERIFY).
- **Failure modes:** Misheard policy number; talks over the caller; unclear handoff; inconsistent French dialect handling.
- **ADR prompts:** Which authentication steps are required by voice? What does the system do when recognition confidence is low? How are recordings stored and deleted?
- **Sources:** Foundry Agent Service overview (voice-based prompt agents); [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md).

### Case 20 Recommendation and personalization
- **Name:** Recommendation and personalization (fairness, consent).
- **When it applies (signals):** Suggesting products, next steps or content tailored to a customer or agent.
- **Recommended pattern:** Classical ranking or rules on consented, minimal features as the engine; LLM only for wording; suitability and eligibility checks are deterministic; recommendations to customers about products are staff-reviewed or restricted to approved content.
- **Why:** Personalization can create unfair outcomes and suitability problems; deterministic rules and consent controls are auditable.
- **Alternatives and when to escalate:** Segment-based content with no individual profiling. Escalate to governance for any use of sensitive attributes or inferred traits.
- **Autonomy rung:** `suggest`.
- **Data classes and PIA trigger:** Confidential to restricted. PIA required; consent and purpose limitation apply.
- **Evals required:** Fairness metrics across groups; suitability rule coverage; consent enforcement tests; explanation quality; click or acceptance versus harm review.
- **Security threats:** Profile leakage; manipulation of recommendations; inference of sensitive traits; prompt injection in profile fields.
- **Regulatory notes:** High-risk (Tier 1) by default when recommendations influence pricing, coverage or suitability. Privacy consent and automated-processing disclosures (VERIFY with Privacy and Compliance). Fair treatment and conduct guidance (VERIFY).
- **Failure modes:** Discriminatory proxy features; unsuitable product recommended with confident wording; consent not honored in downstream systems.
- **ADR prompts:** Which features are used and what is the consent basis? How is suitability enforced outside the model? How are fairness and drift monitored? How can a customer opt out?
- **Sources:** [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md); [12-governance-and-compliance.md](./12-governance-and-compliance.md).

## Platform and agent patterns

### Case 21 Evaluation and monitoring agents
- **Name:** Evaluation and monitoring agents (LLM-as-judge, red-team).
- **When it applies (signals):** Using models to score outputs, monitor production traffic or generate adversarial tests.
- **Recommended pattern:** LLM-as-judge with a rubric, calibrated against human labels and re-calibrated when the judge model changes; red-team agents run in isolated environments with synthetic data; judge results inform humans and gates but a calibrated threshold sets the gate.
- **Why:** Judges are biased and unstable; calibration and isolation make them usable as evidence.
- **Alternatives and when to escalate:** Programmatic checks (schemas, regex, exact match) wherever possible. Escalate to human review for borderline scores and for any high-risk system.
- **Autonomy rung:** `suggest` for judges that inform people; `act-low-risk` for CI gates with human-calibrated thresholds.
- **Data classes and PIA trigger:** Synthetic data in CI; production sampling may include personal information and needs redaction and a PIA.
- **Evals required:** Judge agreement with human labels (per rubric item); stability across runs; sensitivity to position and verbosity bias; red-team coverage against injection and misuse categories.
- **Security threats:** Judge prompt injection from evaluated content; red-team tooling escaping its sandbox; leaking test attacks.
- **Regulatory notes:** Evaluation results are audit evidence; retain with model version and prompt hash (see 14 and 12).
- **Failure modes:** Judge prefers the same model family; gates pass because the judge is lenient; red-team results not acted on.
- **ADR prompts:** Which judge model and rubric, and how is it calibrated? How is judge drift detected? Where do red-team agents run and with what data?
- **Sources:** [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md); [02-security.md](./02-security.md).

### Case 22 Multi-agent systems
- **Name:** Multi-agent systems (usually avoid).
- **When it applies (signals):** Distinct roles with different tools or trust boundaries appear to need separate agents, or work must be parallelized.
- **Recommended pattern:** Default to one agent or a deterministic workflow. Use multiple agents only when (a) tool sets or trust boundaries must be separated, (b) context size makes one agent unreliable, or (c) independent parallel subtasks exist; give each agent its own identity, manifest and limits; treat peer output as untrusted.
- **Why:** Each agent adds cost, latency, failure paths and attack surface; separation is justified only by clear boundaries.
- **Alternatives and when to escalate:** Single agent with tool search or workflow with LLM steps. Escalate to architecture and security review before adoption.
- **Autonomy rung:** `propose` for cross-agent actions that write; `act-low-risk` for read-only parallel research.
- **Data classes and PIA trigger:** Highest class among participating agents; each agent receives only what it needs. PIA if personal information is shared.
- **Evals required:** End-to-end task success versus single-agent baseline; message-level injection tests between agents; cost and latency comparison; failure-injection of one agent.
- **Security threats:** Inter-agent prompt injection; privilege escalation through agent chains; rogue or spoofed agents; trust in agent cards (A2A cards are self-descriptions).
- **Regulatory notes:** Inventory each agent separately (see 12); accountability remains with named owners for the whole system.
- **Failure modes:** Agents amplify each other's errors; infinite delegation loops; unclear accountability; cost explosion.
- **ADR prompts:** What boundary justifies separate agents? What does the single-agent baseline score? How do agents authenticate each other and what do they trust? What limits cap delegation depth?
- **Sources:** [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md); A2A specification; [02-security.md](./02-security.md).

### Case 23 Human in the loop approval flows
- **Name:** Human-in-the-loop approval flows.
- **When it applies (signals):** AI proposes actions or content that a person must approve (write actions, outbound messages, decisions).
- **Recommended pattern:** Approval enforced in code at the tool boundary: the AI submits a proposal object (action, arguments, evidence); an authorized human approves, edits or rejects in a purpose-built UI; the system records who, when and what changed; approvals expire; segregation of duties where needed.
- **Why:** Prompt-level "ask first" is not a control; a recorded approval at dispatch is auditable and non-bypassable.
- **Alternatives and when to escalate:** Sampling-based review for low-risk `act-low-risk` actions. Escalate to dual approval for destructive or high-value actions.
- **Autonomy rung:** `propose`.
- **Data classes and PIA trigger:** Whatever the action touches; the approval UI must respect classification. PIA if personal information is shown.
- **Evals required:** Bypass tests (agent cannot execute without approval); approval-UI comprehension and reviewer accuracy; override and rejection rates; time-to-approve.
- **Security threats:** Approval fatigue; prompt injection crafting misleading proposals; time-of-check versus time-of-use changes; forged approvals.
- **Regulatory notes:** Approval records are audit evidence (see 12); the approver must be accountable and authorized.
- **Failure modes:** Reviewers rubber-stamp; proposal shows summary that differs from what executes; stale approvals reused.
- **ADR prompts:** Who may approve what? What exact action is bound to the approval? How is expiry handled? How is reviewer quality monitored?
- **Sources:** [04-engineering-principles.md](./04-engineering-principles.md); [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md).

### Case 24 Batch and offline LLM pipelines
- **Name:** Batch and offline LLM pipelines versus real-time.
- **When it applies (signals):** Large volumes of documents or records can be processed asynchronously (classification, extraction, enrichment, evaluation).
- **Recommended pattern:** A queue-driven pipeline with idempotent jobs, checkpointing, per-item validation and a dead-letter queue; use the synchronous `Standard` deployment type for personal information. VERIFY: Foundry batch exists only as `GlobalBatch` and `DataZoneBatch`, which are not approved for personal information in this org (see 23).
- **Why:** Offline processing is cheaper and easier to control, but residency rules limit which batch service is usable.
- **Alternatives and when to escalate:** Real-time calls for low volume. Escalate to a data-minimized or synthetic pipeline if the only available batch service violates residency; request a waiver only with PIA and governance approval.
- **Autonomy rung:** `act-low-risk` with sampled review of outputs.
- **Data classes and PIA trigger:** Depends on the data; batch of personal information triggers a PIA and deployment-type restriction.
- **Evals required:** Per-item validation rate; sample-based quality audits per run; drift between runs; cost per item; resumability tests.
- **Security threats:** Poisoned items affecting a whole batch; large-scale leakage if misconfigured; retries amplifying cost; storing intermediate data in unprotected locations.
- **Regulatory notes:** Bulk processing of personal information needs data-minimization and retention controls (see 13); outputs used in decisions inherit the tier of the decision.
- **Failure modes:** Partial runs mistaken for complete; reprocessing duplicates records; silent quality drop on a new document type; quota exhaustion.
- **ADR prompts:** Which deployment type is used and why does it meet residency? How are failures isolated per item? How is quality sampled? How is the run audited and reproducible?
- **Sources:** [23-azure-foundry-standards.md](./23-azure-foundry-standards.md); Foundry deployment types.

## Checklist
- [ ] Closest case identified; `docs/use-cases/<case>.md` created from the template.
- [ ] ADR answers all ADR prompts of the case or marks them not applicable with a reason.
- [ ] Risk tier proposed; high-risk test (UCS-011) applied.
- [ ] Autonomy rung stated and justified; no higher than the case allows.
- [ ] Data classes and PIA status recorded; EN and FR behavior defined for customer-facing cases.
- [ ] Deterministic alternative considered and the reason it is insufficient recorded.
- [ ] Tools and agents have manifests; evals and thresholds exist.
- [ ] A named owner confirmed the regulatory notes; `VERIFY:` items resolved or tracked.

## Common AI failure modes
- Treating a case as an implementation recipe and skipping the ADR.
- Copying the closest case without checking that the use case actually triggers high-risk.
- Raising the autonomy rung "because the demo worked".
- Writing regulatory notes from memory (dates, clauses) and presenting them as confirmed.
- Using an LLM where the case says rules or classical ML come first.
- Forgetting French, or testing French only by machine translation of English tests.
- Choosing batch processing without checking the deployment type's processing location.
- Marking human-in-the-loop as satisfied by a prompt instruction.

## Related docs
- [05-decision-playbook.md](./05-decision-playbook.md): compact decision table that links here.
- [04-engineering-principles.md](./04-engineering-principles.md): autonomy ladder and simple-first principles.
- [12-governance-and-compliance.md](./12-governance-and-compliance.md): tiers, intake, inventory.
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md): data classes and PIA.
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md): evals and thresholds.
- [19-rag-and-retrieval.md](./19-rag-and-retrieval.md): retrieval patterns.
- [22-localization-and-accessibility.md](./22-localization-and-accessibility.md): EN and FR.
- [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md): manifests.
- [23-azure-foundry-standards.md](./23-azure-foundry-standards.md): platform.
- [15-llm-and-model-governance.md](./15-llm-and-model-governance.md): models and prompts.

## Sources
- Foundry Agent Service overview: https://learn.microsoft.com/en-us/azure/foundry/agents/overview
- Foundry deployment types: https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types
- Foundry guardrails overview: https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview
- MCP specification 2026-07-28: https://modelcontextprotocol.io/specification/2026-07-28
- A2A Protocol specification: https://a2a-protocol.org/latest/specification/
- OSFI guidelines E-23, B-10, B-13: VERIFY on the OSFI site for current text and effective dates.
