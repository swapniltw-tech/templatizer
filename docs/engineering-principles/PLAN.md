# Plan: Engineering standards docs for agentic AI development (canada-life)

## Context
Greenfield org building many microservices and AI/agent codebases, mostly AI-generated, inside a **federally regulated financial institution (FRFI) context** (life insurer; OSFI-regulated with an internal AI governance team, per user). The earlier writeup ("Shipping AI code at scale", kept outside this repo; cite by title only, no local paths or links in docs) covers *why* and the high-level approach. This task produces the *what and how*: a set of standards docs that engineers and AI agents follow when building. Output is meant to be handed to another AI, so docs must be explicit, scannable, imperative and **machine-citable** (every rule has an ID).

Decisions from user: **multiple files** in `canada-life/docs/`, **Python** examples/tooling, **Azure** for secrets. Repo `canada-life/` is currently empty (no existing patterns to reuse).

Revision note: v5 (final sweep). Earlier versions incorporated a gap review (regulatory, PII, evals, agent security, LLM governance, CI/CD, APIs, reliability, RAG, licensing, waivers, ownership, verification).

## Decisions from open questions (all 5 answered; copy into `README.md`)
Status: **all original open questions resolved.** Non-blocking follow-ups are listed below; docs mark anything depending on them `ASSUMPTION:`.

Questions asked: (1) OSFI and internal AI governance team, (2) approved LLM providers, (3) existing enterprise standards, (4) EN/FR scope, (5) IaC and CI/CD tooling.

### Answers (recorded)
1. **OSFI-regulated, internal AI governance / model risk team exists.** Docs 12/13 align to OSFI E-23/B-10/B-13 and must reference that team's policies. Follow-up: user to share policy names/links; until then mark references `ASSUMPTION:`.
2. **Approved LLM provider: Azure OpenAI / Microsoft Foundry only.** Doc 15 fixes this as the approved list; no non-Azure providers (adding one requires a waiver per 21 and vendor approval per 12). Data residency story: Azure Canada Central, PIA still required per 13. Note: Anthropic models in Foundry are NOT assumed approved; verify with governance team.
3. **No existing enterprise standards (greenfield).** These docs are the baseline. Still check for any mandatory corporate security/cloud policies before adoption.
4. **EN/FR bilingual in scope.** Keep `22` (no longer conditional); add translation evals to `14` and locale handling to `17`.
5. **IaC: Terraform (planned, mark `ASSUMPTION:` until final, F3). Code hosting and CI/CD: GitLab (confirmed).** Record the choice in an ADR. Doc 16 uses Terraform + GitLab CI for worked examples (`.gitlab-ci.yml`, protected branches/environments, CODEOWNERS, merge request approvals, GitLab CI OIDC / ID tokens to Azure workload identity federation, remote state in Azure Storage with locking). Verify all GitLab and Terraform azurerm provider specifics against current docs. Knock-on: SAST/SCA/secret scanning may use GitLab built-in scanners as well as or instead of Semgrep/gitleaks/Trivy (decide in 02/16); replace "PR" wording with "merge request (MR)" across docs; Terraform needs IaC scanning (e.g. Checkov or Trivy config; verify) and policy-as-code (e.g. OPA/Conftest; verify). Any Azure-native Bicep references are removed.

### Non-blocking follow-ups (do not stop writing; track in README "Open items")
| # | Item | Owner | Affects |
|---|---|---|---|
| F1 | Share names/links of internal AI governance / model risk policies | user | 12, 13, 15 |
| F2 | Confirm which models count as approved under "Azure OpenAI / Foundry only" (e.g. are non-OpenAI models in Foundry allowed?) | AI governance | 15, 05 |
| F3 | Confirm Terraform is final (GitLab is confirmed); record in ADR | platform team | 16 |
| F4 | GitLab self-managed vs GitLab.com (runners, data residency, built-in scanner availability by tier) | platform team | 16, 02 |
| F5 | Check for mandatory corporate security/cloud policies before adoption | security | all |
| F6 | Confirm Quebec/OQLF language requirements and WCAG target level with the business/legal | legal / product | 22 |
| F7 | Confirm license allow/deny list | legal | 20 |
| F8 | ~~CI system conflict~~ **Resolved: GitLab for code hosting and CI/CD** (user confirmed). Use `.gitlab-ci.yml`, merge requests, CODEOWNERS. No `.github/` files. Self-managed vs GitLab.com still open (F4) | done | 16, 01, 07, 08 |
| F9 | Default Python minor: 3.14 (mature) or 3.15.2 (latest)? | user / platform team | 00, 09 |
| F10 | Approve `uv` as package/lock manager (or choose pip-tools) | platform / security | 00, 20 |
| F12 | Tool/agent registry platform: Foundry Toolbox + catalog, Azure API Center, or Git-only; org-owned manifests as source of truth | platform / AI governance | 25 |
| F13 | Pin MCP spec version and verify against modelcontextprotocol.io; research A2A agent cards | platform | 25, 02 |
| F11 | Confirm current Foundry feature status (guardrails, tracing, hosted agents) at write time and agree preview-feature policy | AI governance | 23, 15 |

## Files to create (all under `/Users/swapnilmarathe/Documents/code/canada-life/docs/`)
Numbers 01-11 keep the original mapping to the user's 12 items. Files 12-22 are gap-review additions; `00`, `23`, `24` were added after the tech-stack, Foundry and testing review; `25`, `26` after the AI registry/use-case review. **Read order is set in the README** (governance and security before architecture); numbering is not read order.

### Original scope

| File | Covers user item | Contents |
|---|---|---|
| `README.md` | index | Purpose, how to use with an AI (read order, "treat MUST/SHOULD as enforceable"), **rule-ID scheme and enforcement tags**, file index with **owner and last-verified date per doc**, recorded decisions, open items F1-F13, status/date, **task-to-docs routing table** (e.g. "adding an endpoint -> 17, 03, 09, 24") |
| `01-codebase-practices.md` | 1 | Spec/contract-first, trunk-based, small MRs, CI gates (details in 16), definition of done, template-first (Copier), MR/review rules, **rules for AI coding agents themselves** (what they may run, branch/MR permissions, no self-approval, CI sandbox limits), tests (summary only; full standard in `24-testing-standards.md`) |
| `02-security.md` | 2 | Least privilege first (managed identity, RBAC, deny-by-default), SAST (Semgrep, Bandit, CodeQL), DAST (OWASP ZAP), SCA (pip-audit), secret scanning (gitleaks), container scan (Trivy), hallucinated-dependency checks (slopsquatting), SBOM, **LLM threats (OWASP LLM Top 10, 2025 edition; note newer 2026 edition and pin which is followed)**, **agentic threats (OWASP agentic list, late 2025; numbering differs across sources, verify on owasp.org before citing IDs)**: goal hijack, tool misuse, identity/privilege abuse, memory/context poisoning, inter-agent trust, rogue agents. Also: **one managed identity per agent**, human approval for destructive tools, MCP/tool-server vetting, sandboxed code execution, prompt/tool-definition supply chain, Azure network isolation and private endpoints |
| `03-architecture.md` | 3 | Layering/boundary rules, **architecture fitness tests** in Python (import-linter, pytest-archon), contract tests, service boundaries, ADRs, example rules. Owns topic "boundaries"; defers principles to 04 |
| `04-engineering-principles.md` | 4 | KISS/simple-first, YAGNI, **deterministic workflows over autonomous agents**, autonomy ladder (with **entry criteria per rung tied to eval thresholds in 14**), human-in-the-loop, bounded tool permissions |
| `05-decision-playbook.md` | 5 | "When you have X, go with Q" table. Each row: requirement, recommended, why, when to escalate, sources. Seed entries: structured docs -> vectorless/structured retrieval before vector RAG; fixed steps -> workflow not agent; single LLM call suffices -> no framework; deterministic rule exists -> code not LLM; need routing -> classifier/router before multi-agent; long-running -> queue/durable workflow. **Added:** prompt vs RAG vs fine-tune; model tier selection (small vs frontier); structured output vs free text; sync vs async; build vs buy; cache vs recompute; when human review is mandatory; whether to use an orchestration framework at all; per-user permissions in RAG -> filter at retrieval; PII present -> classification gate (13) first. **Stays a compact table; per-use-case depth lives in `26-ai-use-case-catalog.md`** |
| `06-secrets-and-env.md` | 6, 7 | Azure Key Vault, managed identity/workload identity, no secrets in code/images/logs, rotation, `.env` rules (local only, `.env.example` committed, never prod), config via pydantic-settings, secret scanning pre-commit |
| `07-ignore-files.md` | 8 | Canonical `.gitignore` and `.dockerignore` for Python services (copy-paste blocks), rationale per entry, multi-stage Docker notes |
| `08-claude-md.md` | 9 | Purpose of `CLAUDE.md`/`AGENTS.md`, what to include/exclude, org baseline vs per-repo, a full template (including pointers to rule IDs), size/maintenance guidance |
| `09-structure-and-format.md` | 10 | **Includes the full source-tree layout and dependency rules (see "Source code tree").** Standard repo layout (src layout, tests, docs, ADRs, infra), naming, formatting (Ruff format, line length), typing (mypy strict/pyright), docs format, commit conventions |
| `10-logging-observability.md` | 11 | **See "Observability findings" below for researched constraints.** Structured JSON logging (structlog over stdlib logging), OpenTelemetry traces/metrics/logs with OTLP, Collector-vs-in-process ADR, sampling, cardinality limits, log-trace correlation, correlation IDs, PII/secret redaction (rules from 13), Azure Monitor/App Insights export, LLM telemetry (prompts, tokens, latency, cost, eval results) with redaction, alerting basics, **audit-trail logging for regulated decisions (retention, immutability, who/what/which model version)** |
| `11-clean-code.md` | 12 | Clean code principles tuned for AI output: small functions, naming, SOLID where useful, no dead code, comments policy, error handling, complexity limits (Ruff/radon thresholds), AI-slop anti-patterns checklist |

### Gap-review additions

| File | Contents |
|---|---|
| `12-governance-and-compliance.md` | **Regulatory mapping.** OSFI E-23 (model risk management, covers AI/ML and vendor models; effective **May 1, 2027**; verify against osfi-bsif.gc.ca, secondary sources disagree on transition wording), OSFI B-13 (tech and cyber risk) and B-10 (third-party risk); sources disagree on where cloud/third-party requirements sit, so cite primary text. Contents: AI use-case intake and risk tiering, **model and agent inventory**, validation and ongoing monitoring requirements, accountable owner per system, change management, third-party / LLM-vendor approval, audit and evidence retention, **table mapping each MUST rule ID to the regulatory requirement it supports**. Marked "not legal advice; confirm with Compliance" |
| `13-data-classification-and-privacy.md` | Classification scheme (public / internal / confidential / restricted incl. health, financial, beneficiary data). Matrix of what may go to an LLM, into logs, into tests, into prompts/traces. PIPEDA accountability; **Quebec Law 25: privacy impact assessment before personal information leaves Quebec (test is Quebec, not Canada)**. **Data residency:** Azure Canada Central (Toronto) gives physical residency but not legal sovereignty (US CLOUD Act); doc states the org position and requires the PIA to address foreign-access risk. Synthetic/test data generation, redaction/tokenization libraries (verify current docs), retention and deletion, DSAR support, no real customer data in dev or CI |
| `14-evals-and-testing-ai.md` | **Per-tool and per-agent evals required by the registry (25) are defined here: dataset, thresholds, rerun on any schema/prompt/model change.** Evals as the tests for non-deterministic systems. Golden datasets (sourcing, versioning, no real PII), unit/component/end-to-end evals, LLM-as-judge pitfalls and calibration against human labels, regression gates in CI, red-team / adversarial / prompt-injection suites, thresholds required per autonomy rung (feeds 04), online monitoring and drift, human review sampling, eval result retention as audit evidence, tooling options (pytest-based harness first; verify frameworks before naming) |
| `15-llm-and-model-governance.md` | Approved model/provider list, **pin model versions** (no floating aliases in prod), prompt versioning and review as code, prompt/tool definitions as audited artifacts, fallback and degradation policy, deprecation and migration process (re-run evals), cost budgets and quotas, token limits, Microsoft Foundry config (see 23: guardrails, private endpoints, region), structured output and schema validation requirements |
| `16-cicd-and-deployment.md` | Pipeline standard: required stages and gates (lint, type, test, evals, SAST/SCA/secrets/container scan, SBOM), environments and promotion, IaC with **Terraform** (module standards, remote state in Azure Storage with locking, plan-in-MR / apply-on-merge, drift detection, IaC scanning, policy-as-code), **GitLab CI/CD** (`.gitlab-ci.yml` templates/includes, protected branches and environments, CODEOWNERS and MR approval rules, runner security), signed images/provenance, rollout, rollback and feature flags, protected deploy credentials (GitLab ID tokens/OIDC to Azure workload identity federation, no long-lived secrets), policy-as-code enforcement. Terraform is `ASSUMPTION:` until final (F3); GitLab is confirmed |
| `17-api-and-contracts.md` | OpenAPI-first, versioning and deprecation, standard error format (RFC 9457 problem details; verify), idempotency keys, pagination, auth, async/event schemas (versioned, schema registry), pydantic models as single source, contract-test requirements (links 03), agent tool schemas as contracts |
| `18-reliability-and-operations.md` | Timeouts, retries with backoff and jitter, circuit breakers, rate limiting and handling provider 429s/quota, idempotent and durable workflows, graceful degradation when LLM is down, SLIs/SLOs, health checks, incident response, runbook template, postmortems, kill switch for agents, cost anomaly alerts |
| `19-rag-and-retrieval.md` | Retrieval patterns (structured/vectorless first, then vector), chunking and embedding choices, index freshness, **document-level access control enforced at retrieval**, citation requirements, retrieval evals (links 14), poisoning and vector/embedding weaknesses (OWASP LLM08), PII in indexes, deletion propagation |
| `20-dependencies-and-licensing.md` | Approved registries, pinning and lockfiles (uv/pip-tools; verify), update cadence (Renovate/Dependabot), license allow/deny list (confirm with Legal), internal package standards, checks for hallucinated/typosquatted packages, SBOM generation, vendor SDK approval |
| `21-exceptions-and-waivers.md` | How to request a waiver for a MUST rule: template, required compensating controls, approver by risk tier, expiry date, registry of active waivers, review cadence. Rule: no silent deviations; agents must not self-grant waivers |
| `22-localization-and-accessibility.md` | **In scope (Open Question 4 answered yes).** EN/FR output, Quebec language requirements, accessibility (WCAG) for user-facing UIs, locale handling, translation evals |

### Additions from tech-stack, Foundry and testing review (v3)

| File | Contents |
|---|---|
| `00-tech-stack.md` | The reference stack (see "Reference tech stack" below): versions, tools, what each is for, what is required vs proposed, and the upgrade policy. Single source for tool choices; other docs link here |
| `23-azure-foundry-standards.md` | Practices for **Microsoft Foundry** (formerly Azure AI Foundry) as the approved LLM platform. See "Foundry findings" below. Covers: SDK choice, agent types (prompt vs hosted), networking, identity, guardrails, evals and tracing integration, model deployment/versioning, regional/data-residency settings, quota and cost controls, preview-feature policy |
| `24-testing-standards.md` | **Testing is a first-class standard, not a section of 01.** Test pyramid and what belongs at each level; unit (pytest), integration (real deps via containers/Azurite-style emulators where they exist; verify), contract tests (links 17), end-to-end, property-based (Hypothesis), mutation testing (mutmut) for deterministic logic, coverage thresholds (line + branch; mandatory floor per service tier), **testing LLM-dependent code** (fake/stub model client by default, recorded-response replay, schema validation, never call live models in unit tests, live-model tests isolated and budgeted), determinism rules (seeded, clocked, no network), fixtures and test data (synthetic only, links 13), flaky-test policy, tests-first workflow for AI agents (write failing test, then code; an agent MUST NOT weaken or delete a test to make it pass), security tests (links 02), performance/load smoke tests, test naming and layout, CI gating and required `make test` targets. Evals for non-deterministic behavior stay in 14; 24 links to it |

#### Foundry findings (from review; verify against learn.microsoft.com before writing, features change fast)
- **Rename:** the platform is now **Microsoft Foundry**; docs and portal names changed. Use current names and note old ones (Azure AI Foundry) once.
- **SDK:** current Learn guidance points to `azure-ai-projects` **v2.x** (the Learn page said `>=2.3.0`; one blog said pin 2.0.1; treat Learn as authoritative and re-check at write time). The separate `azure-ai-agents` package is no longer needed; agents, evals, memory and inference live under `AIProjectClient`. Old `create_agent()` code migrates to `create_version` with a `PromptAgentDefinition`; preview features via `allow_preview=True` on the client. Rule: **pin the SDK version, forbid preview features in prod without a waiver (21)**.
- **Agent types:** prompt agents vs hosted (containerized, VM-isolated sandbox per session) agents. Hosted agents have a migration path from the old preview backend (old backend support was stated to end **August 20, 2026**, i.e. already past; confirm nothing relies on it).
- **Networking:** private networking is available for prompt agents; hosted agents support BYO VNet. A third-party guide says network injection for hosted agents **cannot be added after creation**, so decide at creation (verify). Rule: private endpoints and VNet by default for regulated workloads.
- **Guardrails/content safety:** agent guardrails for content safety were described as **preview**. Rule: treat guardrails as defense in depth, not the sole control; preview status requires waiver or compensating controls.
- **Evaluations:** Foundry evals described as GA, with built-in and custom evaluators and continuous production monitoring on sampled traffic. Decide in 14 which evals run in CI (own harness) vs in Foundry (production monitoring), and keep results as audit evidence.
- **Tracing:** OpenTelemetry-based; hosted agents have built-in tracing. GA status was in flux at the time of review. Align with 10 (OTel to Azure Monitor/App Insights) and apply redaction (13) before export.
- **Agent frameworks:** Microsoft Agent Framework (Python) renamed classes in 2026 (`ChatAgent` -> `Agent`, `@ai_function` -> `@tool`, Foundry client/agent classes renamed). Add to 05 as an "orchestration framework?" row: default is **no framework** for single-call or fixed workflows; if one is needed, evaluate Agent Framework and pin versions. The review found nothing on Semantic Kernel/AutoGen status, so verify before mentioning them.
- **Model availability:** models offered in Foundry vary by region and change; ties to follow-up F2 (which models are approved).

#### Reference tech stack (proposed; user-stated items marked U; all versions "verify at write time")
| Area | Choice | Notes |
|---|---|---|
| Language | **Python** (U). Latest stable is **3.15.2** (python.org, Oct 2026; 3.15 released 2026-10-09, supported to Oct 2031). **3.14** is in bugfix to Oct 2030 and is the mature option | Proposed policy: `requires-python` = latest minor that **all pinned dependencies support wheels for**; CI matrix runs the newest two minors; do not use a minor in security-only phase for new services. **Default (ASSUMPTION, F9): 3.14; 3.15.x allowed once all deps support it.** 3.15 is ~1 month old and ML/native deps may lag. Source: python.org, devguide.python.org/versions |
| Type checking | **mypy** (U), strict mode | pyright as an optional editor-side checker only if desired |
| Lint + format | **Ruff** (U) for both `ruff check` and `ruff format` | one tool; no black/isort/flake8 |
| Task runner | **Makefile** (U) | standard targets below |
| Packaging | proposed: **uv** (lockfile, venv, Python install); `pyproject.toml` only | `ASSUMPTION:` verify uv is acceptable to security/platform; alternative pip-tools |
| Tests | **pytest**, pytest-cov, Hypothesis, mutmut, import-linter / pytest-archon | see 24 |
| Containers | **Dockerfile** (multi-stage, non-root, pinned base digest) + **.dockerignore** (U) | scan with Trivy or GitLab container scanning |
| CI/CD + code hosting | **GitLab** (U, confirmed): `.gitlab-ci.yml`, merge requests, CODEOWNERS, protected branches. Dependency updates via Renovate or GitLab-compatible bot (verify) | F4 self-managed vs SaaS open |
| IaC | **Terraform** (U, planned) | `infra/` directory |
| Config/validation | pydantic v2, pydantic-settings | links 06, 17 |
| Logging | **structlog** (proposed) layered over stdlib `logging`, JSON output, trace/span IDs injected by processor; alternative loguru rejected (not stdlib-native, weaker OTel bridge; verify) | links 10 |
| Telemetry | **OpenTelemetry** (traces, metrics, logs) via `opentelemetry-api`/`sdk`, OTLP; Azure export via `azure-monitor-opentelemetry` distro (`configure_azure_monitor`) to Application Insights, or OTel Collector | links 10 |
| LLM platform | **Microsoft Foundry** via `azure-ai-projects` v2 | links 23, 15 |
| Secrets | Azure Key Vault + managed/workload identity | links 06 |
| Hooks | pre-commit (ruff, mypy, gitleaks) | CI is the enforcement; hooks are convenience |

#### Observability findings (for doc 10; verify at write time)
- **Signal maturity (Python, per opentelemetry.io status and the opentelemetry-python README):** traces **Stable**, metrics **Stable**, logs **Development**. Logs are stable at spec level but not in the Python SDK; the SDK's own `LoggingHandler` was reported deprecated in favor of the one in `opentelemetry-instrumentation-logging`. Rule: pin `opentelemetry-*` versions together, read release notes before upgrades, and keep the log pipeline swappable (app logs to stdout JSON is the fallback that must always work).
- **Azure export:** `azure-monitor-opentelemetry` distro with `configure_azure_monitor(...)`; options include `logger_name` (set it so SDK logs are not collected), `log_record_processors`, `metric_readers`, `enable_trace_based_sampling_for_logs` (default False). Live Metrics is on by default and carried a preview notice (README says default True; third-party page said False, trust Microsoft). Microsoft docs also show a newer `microsoft.opentelemetry` entry point (`use_microsoft_opentelemetry`) whose relationship to the distro was unclear; **resolve before writing 10**.
- **Architecture options (decide in an ADR):** (a) in-process distro to Application Insights (simplest); (b) OTLP to an **OpenTelemetry Collector** (central redaction, sampling, routing, vendor-neutral; preferred for regulated redaction because PII scrubbing happens before data leaves the network). Default recommendation: (b) for production, (a) acceptable for low-risk services.
- **structlog + OTel:** the search found no source confirming how structlog processors interact with the OTel logging handler. Inference only: route structlog through stdlib `logging` and add a processor that injects current `trace_id`/`span_id`. **Must be proven in a spike and covered by a test before it is written into the standard.**
- **GenAI semantic conventions:** `gen_ai.*` attributes are **Development** (not Stable) per several third-party blogs; they moved to a separate repo (`semantic-conventions-genai`) in 2026 with no tagged release at last report; attribute names have changed (e.g. `gen_ai.system` -> `gen_ai.provider.name`). Prompt/response content capture is **opt-in** and the opt-in env var is `OTEL_SEMCONV_STABILITY_OPT_IN` (`gen_ai_latest_experimental`). Rules: content capture OFF by default in prod; if enabled, redact per 13 and treat as restricted data; pin instrumentation versions; abstract gen_ai attribute names behind one internal module so renames are a one-file change. Verify against the official spec repo, not blogs.
- **Foundry tie-in:** Foundry tracing is OTel-based (see 23); avoid double-instrumentation and duplicate spans; agree one trace as the source of truth.
- **Instrumentation scope:** auto-instrument HTTP server/client, DB, and queue libraries; manual spans for LLM calls, tool calls, retrieval, and agent steps; metrics for latency, token usage, cost, error rate, eval scores; log-trace correlation on every log line; sampling policy (always keep errors and slow traces); cardinality limits on metric labels; no PII in span attributes or metric labels.

**Standard Makefile targets (every repo MUST provide):** `make install`, `make fmt`, `make lint`, `make typecheck`, `make test`, `make test-unit`, `make test-integration`, `make eval`, `make security` (SAST/SCA/secrets), `make build` (container), `make run`, `make check` (fmt-check + lint + typecheck + test; the same command CI runs). Agents are told to run `make check` before declaring done.

#### Reference repo layout (documented in 09, generated by the Copier template)
```
<service>/
├── CLAUDE.md                  # agent entry point, short, links to rules
├── AGENTS.md                  # optional cross-tool pointer (verify Claude Code import support)
├── README.md
├── Makefile
├── pyproject.toml             # deps, ruff, mypy, pytest, coverage config
├── uv.lock                    # (if uv adopted)
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example               # committed; real .env never committed
├── .pre-commit-config.yaml
├── .gitlab-ci.yml             # GitLab CI/CD (confirmed)
├── CODEOWNERS
├── .mcp.json                  # approved MCP servers only (project scope)
├── .claude/
│   ├── settings.json          # shared permissions (deny-by-default), hooks, env
│   ├── settings.local.json    # personal, GITIGNORED
│   ├── rules/                 # topic rules, some path-scoped via `paths:` frontmatter
│   │   ├── python-style.md
│   │   ├── testing.md         # paths: tests/**
│   │   ├── security.md
│   │   ├── llm-and-agents.md  # paths: src/**/agents/**
│   │   ├── api-contracts.md
│   │   └── infra-terraform.md # paths: infra/**
│   ├── skills/                # repeatable workflows, e.g. new-endpoint, add-eval, write-adr
│   │   └── <name>/SKILL.md
│   ├── agents/                # subagents, e.g. test-writer, security-reviewer, code-reviewer
│   └── commands/              # optional slash commands (skills now cover most uses)
├── src/<package>/             # src layout; canonical tree in "Source code tree" below
├── tests/                     # unit/ mirrors src/; plus integration/ contract/ e2e/
│   ├── unit/  integration/  contract/  e2e/  conftest.py
├── registry/                  # AI tool and agent manifests (see 25)
│   ├── schemas/  tools/  agents/
├── evals/
│   ├── datasets/  (synthetic only)  evaluators/  thresholds.yaml
├── prompts/                   # versioned prompts as files, reviewed like code
├── docs/
│   ├── adr/  use-cases/  runbooks/  api/openapi.yaml
├── infra/                     # Terraform modules and env configs
└── scripts/
```
Personal-only files (`.claude/settings.local.json`, `CLAUDE.local.md`) go in `.gitignore` (07). Notes from the Claude Code docs review (verify exact frontmatter on code.claude.com before writing 08): CLAUDE.md should stay short (docs suggest under ~200 lines) with detail moved to `.claude/rules/` (path-gated rules load only for matching files), skills and subagents; `settings.json` holds permissions, hooks and env; subagents are `agents/*.md` with `tools`/`model`/`skills` frontmatter. A `docs/` folder is a repo convention, not a Claude Code feature.

**Agentic files to specify in 08 (and ship in the template):**
| File | Purpose | Committed? |
|---|---|---|
| `CLAUDE.md` | Project context: commands (`make check`), architecture summary, links to rule IDs, hard "never do" list | yes |
| `AGENTS.md` | Tool-neutral pointer for non-Claude agents; keep one source of truth | yes (optional) |
| `.claude/rules/*.md` | Scoped, enforceable rules (testing, security, LLM code, infra) | yes |
| `.claude/settings.json` | Permissions: allow `make *`, `pytest`, `ruff`, `mypy`; deny reading `.env*`, secrets, `terraform apply`, prod access; hooks: run `ruff`/`mypy` after edits, block edits to protected paths | yes |
| `.claude/skills/*/SKILL.md` | Reusable procedures (scaffold endpoint, add eval, write ADR, add tests) | yes |
| `.claude/agents/*.md` | Subagents: test-writer, security-reviewer, code-reviewer, each with a restricted tool set | yes |
| `.mcp.json` | Only org-approved MCP servers; vetting per 02 | yes |
| `.claude/settings.local.json`, `CLAUDE.local.md` | Personal overrides | **no (gitignored)** |
| Org-level baseline | Managed/enterprise settings and a user-level baseline `CLAUDE.md` distributed by platform team (verify managed-settings mechanism in docs) | outside repo |

### Additions from AI registry, use-case and code-tree review (v4)

| File | Contents |
|---|---|
| `25-ai-tool-and-agent-registry.md` | **Every AI tool/action and every agent is a registered, versioned, spec'd artifact.** Answer to "should they be registered for discovery?": **yes, with an owner and an approval state; discovery is not the same as permission** (a listed tool is not callable by every agent). See "Registry findings" below. Defines the manifest schema, lifecycle (draft -> evaluated -> approved -> deprecated -> retired), required evals per tool, required docs, risk tier, side-effect class, permission scope, rate/cost limits, owner, and rules for how agents discover and bind tools |
| `26-ai-use-case-catalog.md` | **Case-by-case catalog that gives direction for ADRs (not code).** Extends 05. Honest note: as originally planned, `05` was a decision *table* with about 15 rows, which is not extensive. 26 is the extensive part. Each case uses one fixed template (below). Cases are guidance for choosing an approach and recording it in an ADR; they do not prescribe implementation |

#### Registry findings (verify at write time; several sources are secondary)
- **MCP is the likely tool-interface standard.** Current spec revision reported as **2026-07-28** (previous stable 2025-11-25); tool **annotations** arrived 2025-03-26; **JSON Schema 2020-12** default since 2025-11-25. The 2026-07-28 revision reportedly went stateless and deprecated some features (Roots, Sampling, Logging, Dynamic Client Registration). Rule: **pin an MCP spec version** and SDK version; re-check against modelcontextprotocol.io; do not rely on blog summaries. (F13)
- **Foundry already has a catalog layer:** tool catalog, and **Toolbox** (bundles tools behind one MCP-compatible endpoint with auth, guardrails on tool inputs/outputs, observability, version management, Entra/OAuth identity passthrough). Hosted agents get a dedicated Entra agent identity. Published agents can be shared via the Entra Agent Registry. Some toolbox features (skills, MCP tasks) were reported as preview by one third-party source; confirm. Decision for an ADR (F12): use Foundry Toolbox + catalog as the runtime registry, with an **org-owned Git registry (source of truth for manifests)** that CI syncs from, vs Azure API Center private MCP registry (secondary-source claim only; verify).
- **Catalog drift risk:** an MCP server can add tools without the catalog changing. Rule: pin server versions, hash/lock the tool list, and fail CI or block binding when a server's tool set or schema differs from the approved manifest.
- **A2A agent cards** (agent-to-agent discovery): the search returned nothing usable. Mark as `TO RESEARCH` before specifying inter-agent discovery; until then, inter-agent calls go through the same registry and are treated as untrusted input (02).

**Tool manifest (JSON, validated by JSON Schema in CI; one file per tool in `registry/tools/`):**
```
id, name, version (semver), owner (team + role), description (for model),
status (draft|evaluated|approved|deprecated|retired),
risk_tier (low|medium|high), side_effects (none|read|write|destructive|external),
requires_human_approval (bool + conditions),
input_schema (JSON Schema 2020-12), output_schema, error_schema,
auth (identity, scopes, least-privilege role), data_classification_max (links 13),
limits (rate, timeout, cost, max_payload), idempotent (bool),
evals (dataset ref, thresholds, last_run, result link),
docs (usage, failure modes, examples, runbook link),
mcp (server, pinned version, spec version), observability (span name, metrics),
regulatory (inventory id, links 12), deprecation (date, replacement)
```
**Agent manifest** (one per agent in `registry/agents/`): id, version, owner, purpose and non-goals, autonomy rung (04), allowed tools (by id and version range), model deployment (15/23), data classes handled, eval suite and thresholds (14), guardrails, human-approval points, kill switch, runbook, inventory id (12). Prompts live in `prompts/` and are referenced by hash.

**Registry rules (to number in 25):** MUST NOT call a tool absent from the registry; MUST NOT bind a tool beyond the agent manifest's allow-list; tool descriptions are security-relevant (prompt-injection surface), so they are reviewed like code; any schema change bumps version and re-runs evals; unregistered tools fail CI (`make registry-check`); registry is exported for the model inventory (12) and audit.

#### Use-case catalog template (every case in 26 uses this)
`Name` | `When it applies (signals)` | `Recommended pattern` | `Why` | `Alternatives and when to escalate` | `Autonomy rung` (04) | `Data classes and PIA trigger` (13) | `Evals required` (14) | `Security threats` (02) | `Regulatory notes` (12) | `Failure modes` | `ADR prompts` (questions the ADR must answer) | `Sources`.

**Cases to cover (seed list; extend during writing):**
1. Document Q&A over policies/contracts (RAG; structured/vectorless first)
2. Underwriting support (summarize, extract, flag; human decides)
3. Claims intake and triage (classify, extract, route)
4. Claims adjudication assistance (high-risk; decision support only, no autonomous denial)
5. Customer service assistant (chat; PII, escalation to human, EN/FR)
6. Agent-assist for call centre (summaries, next-best-action)
7. Document extraction and OCR to structured data (forms, medical reports)
8. Classification and routing (email, tickets, documents)
9. Summarization (meetings, case notes, long documents)
10. Compliance and policy checking (rules plus LLM; deterministic first)
11. Fraud/anomaly signals (classical ML vs LLM; E-23 model risk)
12. Internal knowledge assistant and enterprise search
13. Code and engineering assistants (SDLC, internal tools, MCP)
14. Workflow automation with tools (deterministic workflow vs agent)
15. Multi-step research/analysis agents (bounded autonomy)
16. Data analysis / text-to-SQL (read-only, schema-scoped)
17. Content generation and communications (letters, emails; review and tone; EN/FR)
18. Translation and localization (EN/FR; Quebec requirements)
19. Voice and conversational interfaces
20. Recommendation and personalization (fairness, consent)
21. Evaluation and monitoring agents (LLM-as-judge, red-team)
22. Multi-agent systems (usually avoid; criteria for when justified)
23. Human-in-the-loop approval flows
24. Batch/offline LLM pipelines vs real-time
Each case lists regulatory sensitivity (e.g. anything affecting coverage, pricing or claims decisions is high-risk and needs governance sign-off; confirm with the governance team, F1).

#### Source code tree (inside `src/`, documented in 09; layered per 03; enforced by import-linter contracts)
```
src/<package>/
├── __init__.py
├── main.py                    # app entry (composition root only; wires deps)
├── config.py                  # pydantic-settings, the only place env is read
├── observability.py           # OTel + structlog setup (single init)
├── api/                       # transport layer (HTTP); no business logic
│   ├── routers/  schemas/  deps.py  errors.py  middleware.py
├── domain/                    # pure business logic; NO I/O, NO framework, NO LLM imports
│   ├── models/  rules/  services/  errors.py
├── application/               # use cases / orchestration of domain + ports
│   ├── use_cases/  workflows/  ports.py   # ports = Protocols the adapters implement
├── adapters/                  # all I/O lives here (outbound)
│   ├── db/  http_clients/  queue/  storage/  keyvault/
│   └── llm/                   # Foundry client wrapper: retries, timeouts, redaction, telemetry, structured output validation
├── ai/                        # AI-specific code, isolated from domain
│   ├── agents/                # one dir per agent: agent.py, manifest ref, state, policies
│   ├── tools/                 # one module per tool; implements its manifest in registry/tools/
│   ├── prompts/loader.py      # loads versioned prompts from /prompts, verifies hash
│   ├── retrieval/             # RAG: index, retriever, access-control filter
│   ├── guardrails/            # input/output validation, PII redaction, injection checks
│   └── evals_hooks.py         # runtime sampling for online eval
├── security/                  # authn/authz, identity, permissions helpers
└── common/                    # tiny shared utilities (no business logic; keep small)
```
Dependency rule (fitness test): `api -> application -> domain`; `adapters -> application ports`; `domain` imports nothing outward; `ai/tools` may call `application` use cases, never adapters directly; `ai/agents` may use `ai/tools` and `adapters/llm`, never `api`. Companion top-level dirs: `registry/` (tools/, agents/, schemas/), `prompts/`, `evals/`, `tests/` (mirrors `src/`), `infra/`, `docs/adr/`, `docs/use-cases/`.
```
registry/
├── schemas/tool.schema.json  agent.schema.json
├── tools/<tool-id>.json
└── agents/<agent-id>.json
docs/
├── adr/NNNN-title.md          # MADR-style; uses use-case catalog prompts
├── use-cases/<case>.md        # filled-in catalog template per real use case
└── runbooks/
```

## Rule IDs and enforcement (defined in README, applied in every doc)
- Every rule has a stable ID: `<AREA>-<NNN>` (e.g. `SEC-014`, `LOG-003`) and a level: MUST / SHOULD / MAY.
- Every rule carries an **enforcement tag**: `lint`, `ci`, `test`, `review`, `runtime`, or `manual`, plus the tool where known.
- Rules are never renumbered or reused; retired rules are marked `RETIRED`.
- Future step (not in this task): export rules to a `rules.yml` registry so CI, Copier templates and agents consume the same source.

## Conventions for every doc
- Header block: **owner (role), last-verified date, status, sources (primary preferred)**.
- Short intro, then **MUST / SHOULD / MAY** rules with IDs and enforcement tags.
- Concrete Python/Azure examples; mark any tool/version claim as "verify current docs."
- **Source standard:** primary sources (OSFI, OWASP, Microsoft, tool docs) for regulatory and tool claims. Where only secondary sources exist, say so. Prefer linking to the authoritative page over paraphrasing dates or numbering.
- End with a checklist section for review, and a "common AI failure modes" list.
- **Single owner per topic:** each topic has one home doc; others link, not restate (e.g. logging redaction rules live in 13/10, not repeated in 02; boundaries live in 03, principles in 04, decisions in 05).
- Cross-link related docs; keep each doc scannable (tables, short sections).
- No invented flags or versions; state uncertainty explicitly. Use `ASSUMPTION:` for unresolved follow-ups (F1-F13) and `VERIFY:` for any flag, config key, SDK call, version or date not confirmed against a primary source.
- No real customer data, secrets or personal data in examples.

## Approach
1. Open questions are resolved (see Decisions). Write with explicit `ASSUMPTION:` / `VERIFY:` markers for follow-ups F1-F13. Defaults for F9/F10 are fixed in `00` (Python 3.14 default, 3.15 allowed and tested in CI matrix; uv), both `ASSUMPTION:`.
2. Write order: (a) README **conventions only** (rule format, AREA prefixes, header, terms), (b) `scripts/check_docs.py` checker (outside `docs/`), (c) `00`, `12` (**without** the rule-mapping table), `13`, `02`, then remaining docs in batches grouped by cross-reference, (d) last: doc 12 mapping table, README file index and routing table, checker run, marker reconciliation.
3. Suggested **read order for README**: 12 -> 13 -> 00 -> 02 -> 04 -> 01 -> 24 -> 03 -> 05 -> 15 -> 23 -> 25 -> 26 -> 14 -> 16 -> 17 -> 18 -> 19 -> 06 -> 10 -> 09 -> 11 -> 07 -> 08 -> 20 -> 21 -> 22.
4. Link back to the earlier writeup for the high-level rationale.
5. Don't create any code, CI config or templates yet. That is a later step (the docs reference them as future work).
6. Regulatory content (12, 13) is drafted as guidance and flagged for Compliance/Legal review before adoption.

## Verification
- **Coverage:** all 12 original user items map to a file (tables above); grep headings to confirm. Gap-review items each map to a file (12-22).
- **Structure:** `ls docs/` shows README + `00` through `26` (28 files incl. README) plus `PLAN.md`. Check all internal relative links resolve (script or `grep -o '](\./[^)]*)'` + existence test).
- **Rule hygiene (script):** every rule has a unique ID, a level and an enforcement tag; no duplicate IDs; every doc has header block, checklist and failure-modes sections.
- **Sourcing:** every tool/version/regulatory claim has a source or a "verify" marker. Spot-check E-23 date, B-10/B-13 placement, OWASP list versions and numbering against primary sources.
- **Privacy:** skim for secrets, personal data and real customer data. None allowed.
- **Overlap check:** no topic restated in two docs (link instead).
- **Agent build test (content quality):** give an AI only the docs and ask it to scaffold a small sample service (one API, one LLM call, logging, tests, CI outline). Review for rule violations, ambiguities and missing guidance. Fix docs, then repeat once.
- **Human review order:** (1) `12` and `13` by Compliance/Legal, (2) `05` decision playbook (most subjective), (3) `02` by Security, (4) rest by engineering leads.
- **Waiver and ownership:** confirm every doc has a named owner role and a review cadence.

## Implementation status (2026-11-25)
All 28 files written: `README.md` and `00`-`26`. `python3 -I scripts/check_docs.py` reports 28 files, 820 rules, 0 errors, 0 warnings. Markers left in the docs: about 170 `VERIFY:` and 100 `ASSUMPTION:`; most `ASSUMPTION:` markers cite an F-item; numeric proposals (tiers, floors, durations, retention, SLAs) are covered by the catch-all F17 in the README.

Corrections to this plan found while writing (docs are authoritative where they differ):
- **Foundry residency:** Global deployment types can process outside Canada; Data Zones exist only for US/EU/APAC; only `Standard` and `ProvisionedManaged` stay in a geography. "Global first" is wrong for personal data; doc 23 requires an Azure Policy deny. Batch is Global/DataZone only, so no personal data in batch.
- **Foundry other:** agent guardrail fully overrides the model guardrail; agent guardrails and tool-call intervention points are preview; new agent identities start with no permissions; `azure-ai-projects` was at 2.11.0 (Learn's `>=2.3.0` is a floor).
- **MCP:** revision 2026-07-28 confirmed (stateless; Roots, Sampling, Logging, HTTP+SSE, Dynamic Client Registration deprecated).
- **OpenTelemetry:** Microsoft now recommends `microsoft-opentelemetry` for new apps; `azure-monitor-opentelemetry` stays supported; never initialise both. structlog-to-OTel correlation spike passed (OBS-003 is MUST); OTel logging handler, OTLP and Azure export were not tested.
- **OSFI:** E-23 effective 2027-05-01 confirmed; cloud/third-party requirements are in B-10 (4.3-4.4), B-13 covers the institution's own tech and cyber controls. B-10/B-13 effective dates remain `VERIFY:`.
- **API:** OpenAPI file is the contract, pydantic models are checked against it for drift (not two sources of truth). OpenAPI was at 3.2.1 when checked.
- **Agent files:** `CLAUDE.md` must start with `@AGENTS.md` when both exist (Claude reads only CLAUDE.md). Deny rules are not a security boundary; CI is the real control. CODEOWNERS enforcement needs a higher GitLab tier (F4). gitleaks is feature-complete (security patches only). `.claude/hooks/` added to the layout.
- **Makefile:** added `registry-check` (14 standard targets). No `make` target for mutation testing (proposal in doc 24).
- **Layout:** architecture tests live in `tests/unit/architecture/`.
- **Rule-ID references in the CLAUDE.md template** are by doc link, not ID, in this pass; adding ID cross-references is a follow-up.

Cross-doc vocabulary reconciled: canonical autonomy rung identifiers now live in doc 04 and are used verbatim in docs 14, 25 and 26 (manifest enum re-validated); risk tiers (Tier 1/2/3) map to `high`/`medium`/`low` in doc 25. `registry-check` is part of `make check`. `docs/shipping-ai-code-at-scale.md` is the pre-existing rationale writeup (not normative, not checked by `check_docs.py`), so `docs/` holds README + `00`-`26` + PLAN.md + that writeup.

Cold-read test (fresh agent, 'Build a new AI agent' row) found and drove fixes: claims-triage rung/tier (Case 03 now `propose`, Tier 1 by default), human-approval rule alignment (SEC-014, REG-015, PRN-020), eval-threshold ownership (EVL-023; numbers per system, F17), preview-guardrail conflict (FDY-003/019/021), doc 02 example now uses the project endpoint (FDY-001), one thresholds file per suite (`evals/<suite>/thresholds.yaml`), manifest examples consistent with REG-019, REG-035 (workflows need manifests), and the registry-check sketch now enforces REG-019 (omissions listed in the doc). Overlap check run: kill switch (REL-024), SBOM (DEP-024/025) deduplicated; PRN-025, SEC-013, CIC-005 retired.

Remaining work: Compliance/Legal review of 12, 13, 22; governance review of 05; resolve `VERIFY:` markers against primary sources; run the agent build test (scaffold a sample service from the docs only); then build the Copier template, CI jobs, `rules.yml` export and the checker in CI.
