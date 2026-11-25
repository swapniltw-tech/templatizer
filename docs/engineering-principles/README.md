# Engineering Standards for Agentic AI Development

> **Owner:** Platform Engineering lead · **Last verified:** 2026-11-25 · **Status:** Draft for review
> **Sources:** see each doc. High-level rationale: the writeup "Shipping AI code at scale" (kept outside this repo).

## Purpose
These docs define **what and how** we build services and AI agents in a federally regulated financial institution context. Engineers and AI coding agents both follow them. Every rule is **imperative, numbered and checkable**. This README defines the conventions all docs share. Sections marked **(final pass)** are completed after all docs exist.

## How to use these docs with an AI agent
1. Do **not** load every doc. Use the **task-to-docs routing table** below: read the first three docs in the row fully, then load the others as a rule points to them. [00-tech-stack.md](./00-tech-stack.md) is implied in every row (commands, tooling).
2. Treat `MUST` as a hard requirement and `SHOULD` as the default unless you record a reason. `MAY` is optional.
3. Cite rules by ID (for example `SEC-014`) in MR descriptions, ADRs and review comments.
4. Never invent a flag, version, config key or SDK call. If a doc says `VERIFY:`, confirm it against the primary source before use.
5. A `MUST` rule can only be bypassed through the waiver process in [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md). Agents MUST NOT grant themselves waivers.
6. Run `make check` before declaring work done (see [00-tech-stack.md](./00-tech-stack.md)).

## Conventions (all docs)

### Doc header (first lines of every doc)
```
# <Title>

> **Owner:** <role> · **Last verified:** YYYY-MM-DD · **Status:** Draft | Reviewed | Adopted
> **Sources:** <primary sources, or "none (internal standard)">
```

### Required sections, in this order
`## Purpose` → `## Rules` → (topic sections, may be placed before Rules where clearer) → `## Checklist` → `## Common AI failure modes` → `## Related docs`. Optional: `## Sources`.

### Rule line format (exact; parsed by `scripts/check_docs.py`)
```
- **SEC-014** [MUST] [ci: gitleaks] Secrets MUST NOT be committed to the repository.
```
- `AREA-NNN`: the owning doc's three-letter prefix and a 3-digit number. IDs are unique across all docs, never renumbered, never reused. Retired rules stay with `[RETIRED]` in place of the level.
- Level: `MUST`, `SHOULD`, `MAY` (also written in the sentence).
- Enforcement tag: one of `lint`, `ci`, `test`, `review`, `runtime`, `manual`, optionally with `: <tool or job>`.
- Cross-reference other docs' rules only by IDs that exist. Link docs with relative links.

### AREA prefixes (one per doc; a doc defines rules only with its own prefix)
| Doc | Prefix | Doc | Prefix |
|---|---|---|---|
| 00 tech stack | `TEC` | 14 evals | `EVL` |
| 01 codebase practices | `PRC` | 15 LLM and model governance | `LLM` |
| 02 security | `SEC` | 16 CI/CD and deployment | `CIC` |
| 03 architecture | `ARC` | 17 API and contracts | `API` |
| 04 engineering principles | `PRN` | 18 reliability and operations | `REL` |
| 05 decision playbook | `DEC` | 19 RAG and retrieval | `RAG` |
| 06 secrets and env | `SCR` | 20 dependencies and licensing | `DEP` |
| 07 ignore files | `IGN` | 21 exceptions and waivers | `WVR` |
| 08 CLAUDE.md and agent files | `AGT` | 22 localization and accessibility | `LOC` |
| 09 structure and format | `STR` | 23 Microsoft Foundry standards | `FDY` |
| 10 logging and observability | `OBS` | 24 testing standards | `TST` |
| 11 clean code | `CLN` | 25 AI tool and agent registry | `REG` |
| 12 governance and compliance | `GOV` | 26 AI use-case catalog | `UCS` |
| 13 data classification and privacy | `DAT` | | |

### Canonical terms and markers
- Say **merge request (MR)**, never "PR". Code hosting and CI/CD is **GitLab**. There are no `.github/` files.
- Say **Microsoft Foundry** (formerly Azure AI Foundry). Examples use **placeholder deployment names** like `<chat-deployment>`, never real model names, because the approved model list is unresolved (F2).
- `ASSUMPTION:` marks a decision that depends on an open item (F1-F13). `VERIFY:` marks a flag, config key, SDK call, version or date not yet confirmed against a primary source.
- Examples contain no real customer data, secrets, personal data or local paths.
- One topic has one home doc; other docs link instead of restating.

## Recorded decisions
1. The org is OSFI-regulated and has an internal AI governance / model risk team.
2. Approved LLM platform: **Azure OpenAI / Microsoft Foundry only**. Anything else needs a waiver ([21](./21-exceptions-and-waivers.md)) and vendor approval ([12](./12-governance-and-compliance.md)).
3. No pre-existing enterprise standards; these docs are the baseline.
4. English and French output is in scope ([22](./22-localization-and-accessibility.md)).
5. Terraform for IaC (planned). GitLab for code hosting and CI/CD (confirmed).
6. Language: Python. Tooling: mypy, Ruff, Makefile, Dockerfile, `.dockerignore`, pytest.

## Open items
| # | Item | Owner | Affects |
|---|---|---|---|
| F1 | Names/links of internal AI governance and model risk policies | user | 12, 13, 15 |
| F2 | Which models count as approved under "Azure OpenAI / Foundry only" | AI governance | 15, 05, 23 |
| F3 | Confirm Terraform is final; record in an ADR | platform team | 16 |
| F4 | GitLab self-managed vs GitLab.com (runners, residency, scanner tier) | platform team | 16, 02 |
| F5 | Mandatory corporate security/cloud policies to align with | security | all |
| F6 | Quebec/OQLF language requirements and WCAG target level | legal / product | 22 |
| F7 | License allow/deny list | legal | 20 |
| F9 | Default Python minor (assumed 3.14; 3.15 allowed when deps support it) | platform team | 00, 09 |
| F10 | Approve `uv` as package/lock manager (assumed) | platform / security | 00, 20 |
| F11 | Foundry feature status (guardrails, tracing, hosted agents) and preview policy | AI governance | 23, 15 |
| F12 | Tool/agent registry platform (Git source of truth + Foundry Toolbox/catalog vs API Center) | platform / AI governance | 25 |
| F13 | Pin MCP spec version; research A2A agent cards | platform | 25, 02 |
| F17 | Owner-approved numeric parameters used as proposals across docs (risk-tier cut-offs, coverage floors, waiver durations, retention periods, SLA/retry numbers, revalidation cadences, flaky-test window); each is marked `ASSUMPTION:` where used | doc owners | 02, 12, 18, 21, 24 |
| F14 | May `domain/` import `pydantic`? Settle in an ADR (doc 03 currently allows it, ASSUMPTION) | architecture lead | 03, 09 |
| F15 | May `application` workflows orchestrate agents (import `ai/`)? Settle in an ADR (doc 03 has no contract yet) | architecture lead | 03, 09 |
| F16 | Confirm Claude Code (and its managed settings) is approved tooling (ASSUMPTION in doc 08) | security / AI governance | 08, 01 |

(F8, the CI system question, is resolved: GitLab.)

## File index
All docs: Last verified 2026-11-25, Status Draft. Rule counts are from `scripts/check_docs.py` and include retired rules.

| # | Doc | Owner (role) | Rules |
|---|---|---|---|
| 00 | [Tech stack](./00-tech-stack.md) | Platform Engineering lead | 26 |
| 01 | [Codebase practices](./01-codebase-practices.md) | Platform Engineering lead | 33 |
| 02 | [Security](./02-security.md) | Head of Application Security | 29 |
| 03 | [Architecture and boundaries](./03-architecture.md) | Architecture lead | 33 |
| 04 | [Engineering principles](./04-engineering-principles.md) | Architecture lead | 31 |
| 05 | [Decision playbook](./05-decision-playbook.md) | Platform Engineering lead with AI governance | 18 |
| 06 | [Secrets and environment](./06-secrets-and-env.md) | Security lead with Platform Engineering lead | 30 |
| 07 | [Ignore files](./07-ignore-files.md) | Platform Engineering lead | 19 |
| 08 | [CLAUDE.md, AGENTS.md and agent configuration](./08-claude-md.md) | Platform Engineering lead with Security lead | 34 |
| 09 | [Structure and format](./09-structure-and-format.md) | Platform Engineering lead | 37 |
| 10 | [Logging and observability](./10-logging-observability.md) | Platform Engineering lead (observability) | 30 |
| 11 | [Clean code](./11-clean-code.md) | Engineering Quality lead | 38 |
| 12 | [Governance and compliance](./12-governance-and-compliance.md) | Head of AI Governance / Model Risk (with Compliance) | 27 |
| 13 | [Data classification and privacy](./13-data-classification-and-privacy.md) | Chief Privacy Officer (with Information Security) | 28 |
| 14 | [Evals and testing for AI systems](./14-evals-and-testing-ai.md) | AI Engineering lead | 34 |
| 15 | [LLM and model governance](./15-llm-and-model-governance.md) | AI governance lead with Platform Engineering lead | 30 |
| 16 | [CI/CD and deployment](./16-cicd-and-deployment.md) | Platform Engineering lead (delivery) | 35 |
| 17 | [API and contracts](./17-api-and-contracts.md) | Architecture lead (API standards) | 35 |
| 18 | [Reliability and operations](./18-reliability-and-operations.md) | Platform Engineering lead (SRE) | 32 |
| 19 | [RAG and retrieval](./19-rag-and-retrieval.md) | AI Engineering lead | 28 |
| 20 | [Dependencies and licensing](./20-dependencies-and-licensing.md) | Platform Engineering lead with Security and Legal | 30 |
| 21 | [Exceptions and waivers](./21-exceptions-and-waivers.md) | Head of Engineering Standards (with AI Governance) | 19 |
| 22 | [Localization and accessibility](./22-localization-and-accessibility.md) | Product Engineering lead | 28 |
| 23 | [Microsoft Foundry standards](./23-azure-foundry-standards.md) | Platform Engineering lead with AI governance | 36 |
| 24 | [Testing standards](./24-testing-standards.md) | Engineering Quality lead | 50 |
| 25 | [AI tool and agent registry](./25-ai-tool-and-agent-registry.md) | Platform Engineering lead with AI governance | 35 |
| 26 | [AI use-case catalog](./26-ai-use-case-catalog.md) | AI governance lead with Platform Engineering lead | 16 |

`ASSUMPTION:` the owner roles are proposed titles; replace them with real role holders before adoption. Background rationale (non-normative; uses generic wording such as "PR" and lists GitHub and GitLab options, where these standards choose GitLab and MRs): [shipping-ai-code-at-scale.md](./shipping-ai-code-at-scale.md). The build plan is [PLAN.md](./PLAN.md).

## Task-to-docs routing table
Load only the docs for the task. Always load [00](./00-tech-stack.md) for commands and tooling.

| Task | Read |
|---|---|
| Start a new service from scratch | 09, 00, 03, 01, 24, 16, 06, 07, 08 |
| Add or change an HTTP endpoint | 17, 03, 09, 24, 02 |
| Add an LLM call to a service | 15, 23, 13, 02, 14, 10 |
| Build a new AI agent or LLM workflow | 04, 25, 05, 15, 23, 02, 13, 14, 26 (its case plus UCS rules only), then 12 (intake, tier), 18 (kill switch, fallback), 10 (traces, redaction), 21 (waivers), 03/09 (layout), 24 (tests) |
| Add or change an AI tool (action) | 25, 02, 14, 17, 04 |
| Build RAG or search over documents | 19, 13, 14, 02, 26 |
| Choose an approach for an AI use case, write an ADR | 26, 05, 04, 12, 13, 03 |
| Handle personal or restricted data | 13, 12, 02, 10, 24 |
| Write or fix tests | 24, 14, 11 |
| Add logging, tracing or metrics | 10, 13, 18 |
| Handle secrets or environment config | 06, 07, 02, 16 |
| Change CI/CD, Terraform or deployment | 16, 06, 02, 20 |
| Add or upgrade a dependency | 20, 02, 00 |
| Update `CLAUDE.md`, rules, skills or agent settings | 08, 01, 02 |
| Improve reliability, timeouts, incident readiness | 18, 10, 04 |
| Add French/English output or UI accessibility | 22, 14, 17 |
| Request an exception to a MUST rule | 21, 12 |
| Prepare for governance or audit review | 12, 13, 25, 14, 10, 21 |

## Suggested full read order (humans onboarding)
12 → 13 → 00 → 02 → 04 → 01 → 24 → 03 → 05 → 15 → 23 → 25 → 26 → 14 → 16 → 17 → 18 → 19 → 06 → 10 → 09 → 11 → 07 → 08 → 20 → 21 → 22.

## Maintenance
- Each doc has one owner role (index above). Review at least every six months and on any change to a regulatory instrument, Foundry feature status or a pinned tool.
- Run `python3 -I scripts/check_docs.py` before merging any change to `docs/`. It checks rule format, ID uniqueness, required sections, links, banned wording and secrets.
- Rules are never renumbered. Add new rules with the next free number; retire with `[RETIRED]`.
- Future work: export all rules to a `rules.yml` registry and generate the Copier template, CI jobs and `CLAUDE.md` rule files from it.
