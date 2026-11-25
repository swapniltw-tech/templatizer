# Shipping AI-Generated Code at Scale Without AI Slop

**Audience:** an AI assistant or agent (or a human) helping design engineering standards, tooling and workflows for this initiative.
**Status:** initial guidance, written 2026-11-25. Treat it as a starting baseline to adapt, not a finished standard.

---

## 1. Context and goal

- We are starting **greenfield** projects.
- We expect to create **many microservices** and **many AI-related codebases** (including products that embed LLMs).
- Most code will be generated or heavily assisted by AI.

**Problem to solve:** ship AI-generated code at scale *without* drowning in "AI slop". Slop means code that looks plausible but is low quality. Typical forms:
- code that solves the wrong problem, or only the happy path
- duplicated or dead code, and over-engineering
- tests that assert nothing
- inconsistent styles and patterns across services
- hallucinated or typosquatted dependencies
- subtle security and correctness bugs that survive a skim review

**Is there a single standard or framework for this?** No. There is no authoritative "AI code quality standard". The effective approach combines established engineering practices (contracts, platform engineering, CI quality gates, secure SDLC, delivery metrics) and enforces them more strictly and more automatically than before. The reason is that AI raises code *volume* while human review capacity stays flat.

## 2. Core principle

> Generation is now cheap. **Verification is the bottleneck.**

Slop gets through when human review is the only quality gate. The remedy is to **automate verification** so humans spend their attention on intent, design and risk, not on syntax and style. The same gates should run *inside the agent's own loop* (not only in CI), so the agent self-corrects before a human sees the code.

## 3. Practices

### 3.1 Define "good" before generating

| Practice | What it means | Examples / tools |
|---|---|---|
| Spec-driven development | The written spec is the source of truth, and code is derived from it. Directly counters "plausible code that solves the wrong problem". | GitHub Spec Kit, AWS Kiro, OpenSpec |
| Contract-first interfaces | Every service boundary is defined by a machine-readable schema before implementation. Add contract tests so services cannot silently drift. | OpenAPI, protobuf/gRPC, AsyncAPI, Pact, schema-diff checks in CI |
| Architecture Decision Records (ADRs) | Record the "why" in the repo, so humans and agents share context. | `docs/adr/NNNN-title.md` |
| Agent instruction files | Per-repo conventions, forbidden patterns, how to run tests, and the preferred libraries. Keep a shared org-wide baseline plus per-repo overrides. | `AGENTS.md` (emerging cross-tool convention), `CLAUDE.md` |

### 3.2 Golden paths (highest leverage for many microservices)

- Provide **service templates** with logging, auth, tracing, CI, lint config, Dockerfile, health checks and test scaffolding already wired in (Backstage software templates, Cookiecutter, Copier, or similar).
- Instruct agents to **start from the template, never from scratch**. Without this, 40 services end up in 40 styles.
- Maintain an **approved stack list** (languages, frameworks, libraries). A smaller menu means fewer hallucinated dependencies and less inconsistency.
- Build the template first. Retrofitting gates into existing services is much harder.

#### Templating and bootstrapping tools

The main risk with many services is **drift**: services diverge from the template over time. So prefer tools that can *update* existing services, not just generate them once.

| Tool | Strengths | Weaknesses |
|---|---|---|
| **Copier** (Python; generates any language) | Template **updates** via `copier update`. Versioned through git tags. Questionnaires and conditional files. | Python-based tool. |
| **Cookiecutter** | Most popular, huge ecosystem, simple. | No built-in update story, so generated services drift. (Cruft adds update tracking, but Copier does it natively.) |
| **Yeoman** | Mature, JS-oriented, programmatic generators. | Aging, less active. |
| **Projen** | Project config as code (TypeScript); files regenerated and locked, which enforces consistency. | Opinionated; best in JS/TS/AWS CDK. |
| **Nx / Turborepo generators** | Good for JS/TS **monorepos**. | Tied to those ecosystems. |
| **Language-native** (`cargo-generate`, `dotnet new`, `create-*`, Spring Initializr) | Idiomatic, simple. | Per language; does not unify an org. |

**Portal layer (optional):** *Backstage* Software Templates (scaffolder) provide a UI that creates the repo, wires CI, and registers the service in a catalog. Managed alternatives include Port, Cortex and OpsLevel. Copier and Backstage are **not both required**:

- Backstage has its **own built-in templating** (Nunjucks via `fetch:template`), but it generates once with **no native update mechanism**.
- Using Copier *inside* Backstage requires writing a **custom scaffolder action**. The effort is real, and the payoff is both self-service and update-ability.

| Situation | Choice |
|---|---|
| Few services, small team, no platform team | **Copier alone** (CLI). |
| Many services, want self-service UI and catalog | **Backstage alone**, plus Renovate and reusable CI workflows to limit drift. |
| Many services and drift is the main pain | **Both**, with a custom action that runs Copier (highest effort, best long-term result). |

**Default recommendation:** start with **Copier alone**, and keep CI logic in **shared reusable workflows** (GitHub Actions reusable workflows, GitLab CI includes) so most of the pipeline is referenced instead of copied into each service. Add Backstage later only when discovery and self-service become real problems.

**Keeping services in sync:** Renovate or Dependabot for dependencies, `copier update` for template drift, and reusable CI workflows for pipeline drift.

**Template hygiene for AI:**
- Ship `AGENTS.md`, lint and type configs, CI references and agent hook config **inside the template**, so every generated repo is agent-ready.
- Add a **template test**: CI for the template generates a sample service and runs its gates, so a broken template never reaches teams.
- Instruct agents to create new services from the template (Copier or the portal), never from a blank directory.

*Tool status changes; verify current maintenance and features before committing.*

### 3.3 Automated quality gates (the "slop filter")

Make these mandatory in CI, and also run them locally and in agent hooks.

- **Static analysis:** strict typing, linting, formatting, cyclomatic/cognitive complexity limits, duplicate-code detection (e.g. jscpd, SonarQube).
- **Tests:** coverage thresholds *plus* **mutation testing** (Stryker, mutmut, PIT). Coverage alone is gameable. Mutation testing exposes AI-written tests that assert nothing.
- **Architecture fitness tests:** enforce layering, module boundaries and allowed dependencies (ArchUnit, dependency-cruiser, import-linter).
- **Security:**
  - SAST (Semgrep, CodeQL) and secret scanning
  - dependency and vulnerability scanning
  - **verification that every dependency actually exists and is legitimate.** Models hallucinate package names, and attackers register them ("slopsquatting").
  - SBOM generation and SLSA build provenance
- **Hygiene:** dead-code and unused-dependency detection, because AI tends to over-generate.

### 3.4 Process and workflow

- **Small PRs with a hard size limit.** Large AI diffs get rubber-stamped.
- **The human author owns the code.** "The AI wrote it" is not an acceptable answer. The author must be able to explain the change.
- **Risk-tiered review.** Auth, payments, data migrations and infra changes get deep human review. Low-risk changes rely on automated gates plus a light review.
- **AI review as a first pass only.** A second model reviewing the first catches real issues, but it must not be the final gate.
- **Safe delivery mechanics:** trunk-based development, feature flags, canary or progressive rollout, and fast rollback. These make mistakes cheap, so teams can move fast safely.
- **Observability from day one** (OpenTelemetry for traces, metrics and logs). It is the safety net for what review misses.

### 3.5 Measurement

Track whether slop is accumulating:

- **DORA metrics**, especially *change failure rate*, *rework rate* and *time to restore*. DORA's AI research finds that AI amplifies existing engineering practices, good or bad, and can hurt delivery stability where fundamentals are weak.
- **AI-code churn:** the share of code reverted or rewritten within about 2 weeks.
- Review time per PR, PR size distribution, and incidents attributed to AI-authored changes.
- Duplication and complexity trends per repo.

## 4. Relevant standards and frameworks

| Area | Reference |
|---|---|
| Secure development lifecycle | NIST SSDF (SP 800-218), OWASP ASVS |
| Software supply chain | SLSA, OpenSSF Scorecard, SBOM (SPDX / CycloneDX) |
| Products that embed LLMs | OWASP Top 10 for LLM Applications, NIST AI RMF, ISO/IEC 42001 |
| Delivery performance | DORA metrics and capabilities |
| Software quality model | ISO/IEC 25010 |

These are **reference frameworks, not turnkey solutions**. None of them specifically certifies AI-generated code.

## 5. Recommended rollout order (greenfield)

1. **Service template** with all gates built in (lint, types, tests, mutation, security scans, observability, CI).
2. **`AGENTS.md` baseline** and an approved-stack list, with the template and the agent instruction file referencing each other.
3. **Contract-first APIs** with contract tests in CI.
4. **CI gates:** mutation testing, architecture fitness tests, dependency verification, secret and SAST scanning.
5. **Agent-loop enforcement:** hooks or equivalent so gates run before the agent declares work done.
6. **PR size limits and risk-tiered review rules** (e.g. CODEOWNERS plus branch protection).
7. **Metrics dashboard** (DORA plus churn and duplication) from the start.

## 6. Guidance for an AI working on this

If you are an AI asked to act on this document:

- **Ask for the stack first.** Languages, cloud, CI system, and repo layout (monorepo or polyrepo) change the concrete tool choices. Don't assume.
- **Prefer enforceable mechanisms over written guidelines.** A CI check or hook beats a paragraph in a wiki.
- **Don't invent tool names, versions or flags.** Verify against current documentation before writing configs. Some tools named here may have changed since this was written.
- **Start with the template and baseline files (steps 1-2).** They have the highest payoff.
- **Keep gates fast.** Slow pipelines get bypassed. Run cheap checks on every commit, and expensive ones (mutation testing, full SAST) on PRs or nightly where appropriate.
- **Flag trade-offs honestly** (e.g. mutation testing is slow, and strict gates slow early prototyping). Don't present the list as costless.

## 7. Possible next deliverables

- An `AGENTS.md` baseline for all repos
- A reference CI pipeline for the service template, for the chosen stack
- Agent hooks configuration to run the gates in-loop
- A PR template and risk-tier policy with CODEOWNERS
- An ADR template and a service-contract checklist
