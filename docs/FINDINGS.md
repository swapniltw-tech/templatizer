# Findings from building the service template

Contradictions, ambiguities and gaps found in the standards docs (`canada-life/docs/`) while building `templates/service/`. The standards docs were **not edited**. Each entry says what I did instead; a human owner decides the fix.

Status key: **open** = needs a decision; **worked around** = the template picked a side and says so in the generated files.

| ID | Docs | Status | Summary |
|---|---|---|---|
| F-01 | 00, 03, 17 | open | No web framework is named |
| F-02 | 00, 24 | open | pytest config and `make test` differ between the two docs |
| F-03 | 24 | open | `--disable-socket` alone breaks every asyncio-based test |
| F-04 | 00, 03, 09 | open | Where `lint-imports` runs (`make lint` vs the doc 00 Makefile) |
| F-05 | 10, 13 | open | Redaction key list is owned by doc 13, which has none |
| F-06 | 10, 17 | open | `trace_id` in problem details: correlation ID or OTel trace ID |
| F-07 | 03, 09, brief | open | ARC-016 vs STR-005 vs the out-of-scope AI layer |
| F-08 | 16, 17, 18 | open | Probe endpoints vs API-007 "no operation is public by default" |
| F-09 | 00, 16 | open | CIC-007 digest pinning vs the TEC-002 Python-minor matrix |
| F-10 | 00, 07 | open | Dockerfile digest placeholders fail the build by design |
| F-11 | 08 | open | No `AGENTS.md` template; the `CLAUDE.md` template assumes AI-layer directories |
| F-12 | 08, 09, 00 | open | Doc scripts are not clean under doc 00's own Ruff config |
| F-13 | 00, 24 | open | No test-client dependency named; Starlette now wants `httpx2` |
| F-14 | 08 | open | Settings-schema validation of `.claude/settings.json` is not wired |
| F-15 | 08, 09 | worked around | Which `.claude/` files the template ships |
| F-16 | PLAN, README | open | Stale rule count in PLAN.md |
| F-17 | 02, 17, 24 | open | No authentication pattern for the example endpoint |
| F-18 | 08, brief | worked around | Files that cannot cite rule IDs |
| F-19 | 01, 00, 08, 09, 16 | open | Contradictions found by the independent cold-read (doc 01 and others) |

## F-01 No web framework is named
- **Docs:** 00 (reference stack), 03 (contracts forbid `fastapi` in `domain/`), 17 (OpenAPI, pydantic models, problem details).
- **Problem:** doc 03 assumes FastAPI, but no doc chooses a framework, and TEC-021 / ARC-029 require an ADR for any new dependency.
- **Done:** the template uses FastAPI + uvicorn and ships `docs/adr/0001-use-fastapi-for-http-transport.md` with status `proposed` (ARC-031: agents draft, humans accept). `pyproject.toml` carries an `ASSUMPTION:` pointing here.
- **Decision needed:** accept or replace the ADR; add the framework to doc 00's reference stack.

## F-02 pytest config and `make test` differ between docs 00 and 24
- **Docs:** 00 uses `[tool.pytest.ini_options]` with `--cov` in `addopts`, `test` = everything except integration/contract/eval, `test-integration` with `--no-cov`, and `fail_under = 80`. Doc 24 uses native `[tool.pytest]`, coverage only when `--cov` is passed, `test: test-unit test-integration`, and tier floors 90/85/80 (TST-025).
- **Also:** doc 24's rules need `pytest-socket`, `pytest-randomly` and `pytest-timeout`, which doc 00's `dev` group omits; doc 24 uses `uv run`, doc 00 `uv run --locked`.
- **Done:** doc 24 wins for tests (it owns testing); doc 00 for everything else. `make` uses `uv run --locked`. The coverage floor comes from the `service_tier` question (A/B/C → 90/85/80), marked `ASSUMPTION:` (F17).
- **Decision needed:** one canonical pytest block and one `test` definition, in doc 00 or doc 24.

## F-03 `--disable-socket` alone breaks asyncio-based tests
- **Doc:** 24 (TST-008, reference config `--disable-socket`).
- **Observed:** with only `--disable-socket`, Starlette's `TestClient` fails because asyncio opens a local `AF_UNIX` socketpair for its event loop; `filterwarnings = error` then turns the unclosed-loop warnings into a wall of errors.
- **Done:** added `--allow-unix-socket` (pytest-socket 0.8.1). Network (`AF_INET`) sockets stay blocked.
- **Decision needed:** doc 24 should show the flag, or say how async tests are to be written.

## F-04 Where `lint-imports` runs
- **Docs:** ARC-015 requires `lint-imports` as part of `make lint`; STR-007 says it runs in `make check`; doc 00's "standard Makefile" `lint` target is `ruff check .` only, and TEC-009 / the failure-modes table say to copy that Makefile.
- **Also:** PRC-015 says no check may exist only in CI without a local equivalent, yet IGN-016, AGT-001 and the other doc 08/07 checks have no Makefile hook.
- **Done:** `lint` runs `ruff check .`, `lint-imports` (ARC-015), `scripts/check_ignore.sh` and `scripts/check_agent_config.py` (so they run in `make check` and CI). `check_ignore.sh` needs a git work tree, so run `git init` before `make check`. The commit-subject check stays CI-only (it needs a git range); TODO in the CI file.
- **Decision needed:** update doc 00's Makefile.

## F-05 Redaction key list has no owner text
- **Docs:** doc 10 says the sensitive-key list is "owned by doc 13"; doc 13 contains no such list (only classification tiers).
- **Done:** `observability.SENSITIVE_KEYS` is the six-key placeholder from doc 10's spike, marked `ASSUMPTION:`.
- **Decision needed:** doc 13 (or doc 10) publishes the real list; OBS-009 says a test must prove it scrubs "the keys listed by the data-classification standard".

## F-06 `trace_id` in problem details
- **Docs:** API-009 requires "a correlation ID extension member (`trace_id`)". Doc 10 uses `trace_id` for the OTel trace ID and a separate request correlation ID (OBS-006).
- **Done:** the problem body's `trace_id` carries the request correlation ID (works without a tracer). Marked `ASSUMPTION:` in `api/errors.py`.
- **Decision needed:** which value API-009 means; ideally one of them is renamed.

## F-07 Every canonical package vs no placeholder directories vs scope
- **Docs/brief:** ARC-016 says the template MUST create every canonical package with an `__init__.py` or the import-linter contracts fail ("Module ... does not exist") and says contracts MUST NOT be trimmed. STR-005 says no empty or placeholder directories. The brief puts the AI-agent layer out of scope and the brief's tree omits `ai/` and `security/`.
- **Done:** docstring-only `__init__.py` files for every package a contract names (`ai/`, `ai/agents/`, `ai/tools/`, `security/`, the five `adapters/*` packages, `common/`). Omitted (not named by any contract): `adapters/llm/`, `ai/prompts/`, `ai/retrieval/`, `ai/guardrails/`, `application/workflows/`, `api/deps.py`. A unit test asserts the packages exist (ARC-016).
- **Decision needed:** state whether ARC-016 overrides STR-005 for these packages, and whether `adapters/llm` should ship once the AI layer is built.

## F-08 Probes vs "no operation is public by default"
- **Docs:** API-007 says every operation declares its auth scheme and none is public by default; REL-019 requires liveness and readiness endpoints; no doc says how probes authenticate.
- **Done:** probes are explicitly unauthenticated (`security: []` in the OpenAPI document) and a contract test asserts it.
- **Decision needed:** confirm that platform probes are exempt, or define how they authenticate.

## F-09 Digest pinning vs the Python-minor matrix
- **Docs:** CIC-007 requires job images pinned by digest or immutable tag; TEC-002 requires `make check` on the two newest minors; TEC-004 says `.python-version`, Dockerfile and CI name the same minor (two CI minors cannot all match).
- **Done:** two explicit jobs (`check-py314`, `check-py315`), each with its own placeholder digest. `parallel: matrix` with a variable in `image:` was left out: docs.gitlab.com does not confirm matrix variables there. TEC-004 is read as "the default minor" (`3.14`).
- **Not verified:** the CI file was not linted with GitLab's CI lint or run (no GitLab access). Checked against docs.gitlab.com on 2026-11-25: `junit` accepts a list, `coverage_report` syntax, the `coverage:` regex form, `CI_MERGE_REQUEST_DIFF_BASE_SHA` (merge request pipelines only).
- **Related (doc 16 is outdated):** it names the templates `Security/SAST.gitlab-ci.yml` and `Security/Secret-Detection.gitlab-ci.yml`; docs.gitlab.com now shows `Jobs/SAST.gitlab-ci.yml` and `Jobs/Secret-Detection.gitlab-ci.yml`, available in Free, Premium and Ultimate (MR widgets need Ultimate). The template uses the `Jobs/` paths.

## F-10 Dockerfile placeholders fail the build by design
- **Docs:** doc 00 ships `REPLACE_WITH_DIGEST` so the build fails until real digests are set; the brief expects `docker build` to succeed.
- **Done:** placeholders kept. **`docker build` was not verified**: no container daemon was running during this build.

## F-11 No `AGENTS.md` template; `CLAUDE.md` template assumes AI-layer paths
- **Docs:** AGT-006 requires `@AGENTS.md` first when an `AGENTS.md` exists, but doc 08 provides no `AGENTS.md` content and its `CLAUDE.md` template is one file. The template's "Where things live" table lists `registry/`, `prompts/`, `evals/` thresholds and `infra/`, which STR-005 forbids creating as empty directories.
- **Done:** tool-neutral content (the doc 08 template, trimmed to paths that exist) lives in `AGENTS.md`; `CLAUDE.md` is `@AGENTS.md` plus Claude-specific notes (AGT-006, AGT-007). `@AGENTS.md` expansion was **not** verified in a live Claude Code session (`VERIFY:` in the file).

## F-12 Doc scripts are not clean under doc 00's Ruff config
- **Docs:** doc 08 says `check_agent_config.py` passes `ruff` and `mypy --strict`; doc 09 shows `check_commit_msg.py`.
- **Observed:** under doc 00's rule set both fail `ruff format --check`; `check_agent_config.py` also trips `C901`/`PLR0912` and an unused `# noqa: TRY004`; `check_commit_msg.py` trips `PLR2004`.
- **Done:** formatted both, removed the unused `noqa`, and added a narrow `scripts/**` ignore (`T201, C901, PLR0912, PLR2004`).

## F-13 Test-client dependency
- **Docs:** none name an HTTP test client. Starlette's `TestClient` now emits a deprecation warning for `httpx` and asks for `httpx2` (the warning becomes an error under `filterwarnings = ["error"]`, TST-011).
- **Done:** dev dependency `httpx2>=2,<3`. The doc 03 contracts still list `httpx` as forbidden for `domain/api/application/ai`; they do not cover `httpx2`.
- **Decision needed:** record the test client in doc 00 and decide whether `httpx2` joins the forbidden lists.

## F-14 Settings-schema validation is not wired
- **Doc:** AGT-016 says `.claude/settings.json` MUST validate against the published schema; doc 08's script supports `--schema <file>` but CI would have to fetch it (egress, F4) or vendor it.
- **Done:** the CI job runs `check_agent_config.py` without `--schema`. `jsonschema` is not a dependency. `claude doctor` was not run here.

## F-15 Which `.claude/` files the template ships
- **Docs:** 08 and 09 list rules `python-style`, `testing`, `security`, `llm-and-agents`, `api-contracts`, `infra-terraform`, plus skills and subagents. Doc 08 gives text only for four rules, four skills and two subagents; `security.md` and `api-contracts.md` have no text.
- **Done:** shipped `settings.json`, both hooks, and the `python-style` and `testing` rules (all marked as tested in doc 08). Left out: `llm-and-agents` and `infra-terraform` (their directories are out of scope), skills and subagents (doc 08 marks them `VERIFY:`, never run live), `.mcp.json` (no approved servers exist). Add them when the matching scope exists.

## F-16 Stale rule count
- `PLAN.md` says 820 rules; `check_docs.py` reports 821 and the new `rules.yml` export contains 821 (3 retired).

## F-17 No authentication pattern for the example endpoint
- **Docs:** API-007 (every operation declares its auth scheme; none is public by default), TST-046 (every endpoint that enforces authorization needs a deny-path test). The docs I used (00, 03, 06, 07, 08, 09, 10, 16, 24) do not define the org's authn/authz mechanism; doc 02 owns it and was out of this task's reading list.
- **Done:** the reference service's premium-estimate operation is declared public (`security: []`) with a `TODO:`; no authorization is enforced, so TST-046 does not yet apply. Do not copy this endpoint into a real service without adding auth.

## F-18 Files that cannot cite rule IDs
The brief says every generated file cites the rule IDs it implements. Three kinds cannot carry a comment: `.claude/settings.json` (AGT-016 requires strict JSON), `.python-version` (a bare version, TEC-004), and generated files (`uv.lock`, `docs/api/openapi.yaml`, `.copier-answers.yml` carries a provenance comment only). Their rules: `settings.json` implements AGT-016..AGT-019 and AGT-021; `.python-version` implements TEC-001 and TEC-004; `uv.lock` implements TEC-005; `docs/api/openapi.yaml` implements API-001 and API-002. Every other template file carries a citation (checked by script against `rules.yml`: all cited IDs exist and none is retired).

## F-19 Contradictions found by the independent cold-read
A fresh subagent read only the routing row's docs (README row, then 09, 00, 03, 01, 24, 16, 06, 07, 08) and listed what blocks a newcomer. It had no access to my notes. Items already covered above are not repeated (F-01, F-02, F-04, F-07, F-09, F-10, F-11, F-13). The rest, with what the template did:

| # | Contradiction | Template choice |
|---|---|---|
| 1 | PRC-011 (01): new services MUST come from the org Copier template, hand copying is forbidden (VERIFY: Copier). Docs 00, 07, 09 and README say the template is future work and tell you to copy from the docs. | This template is the Copier template; PRC-011's `VERIFY:` on Copier still stands. |
| 2 | TEC-010: CI runs `make check`. CIC-001 and the doc 16 skeleton run the targets separately and omit `registry-check` and the 3.14/3.15 matrix (TEC-002). | CI runs `make check` on both minors (F-09). |
| 3 | PRC-014 lists 12 standard targets; TEC-009 lists 14 (adds `fmt-check`, `registry-check`). | All 14. |
| 4 | Doc 09's ADR headings ("MADR minimal", STR-025) differ from doc 03's template (ARC-030, which has `Confirmation` that ARC-033 needs). | Doc 03's template. |
| 5 | The doc 01 command table lets agents run `git commit`, `make build`, `make security`, `make run`; doc 08's settings make `git commit` and `make build` `ask`, and the allow list omits `make security`, `make run` and `make fmt-check`. | Doc 08's `settings.json` verbatim (it is the tested one). |
| 6 | PRC-032 [MUST] requires an agent trailer on commits; STR-032 [SHOULD] says the format is undecided (F5). | The commits in this repo carry the `Co-Authored-By` trailer; the template adds nothing. |
| 7 | `thresholds.yaml` is `evals/thresholds.yaml` (09 tree, 07) or `evals/<suite>/thresholds.yaml` (PRC-026, 09 CODEOWNERS, README note). | CODEOWNERS uses `evals/**/thresholds.yaml`; no thresholds file ships. |
| 8 | PRC-026 and CIC-010 protect `Makefile`, `Dockerfile`, lint/type/import config and `evals/`; doc 09's CODEOWNERS example omits them, and omits the architecture owner ARC-019 requires. | Added all of them to `CODEOWNERS`. |
| 9 | STR-008 says `domain/` imports nothing from other layers; doc 03's layer map and contract allow `common/` (ASSUMPTION). | Contract unchanged; the `domain-pure` list does not ban `common`. |
| 10 | TEC-016 says config lives in `pyproject.toml`, but import-linter config is `.importlinter` (doc 00 note; doc 03 says `pyproject.toml` support is unverified). | `.importlinter` file. |
| 11 | Doc 08's `llm-and-agents.md` path glob (`src/*/ai/**`) differs from doc 09's tree (`src/**/agents/**`). | Rule not shipped (F-15). |

Undecided points the reader could not resolve (all still open): runtime and hosting platform (SCR-007/012/030 branch on it); database, queue and ASGI server choices; F3, F4, F9, F10, F14, F15; service risk tier and coverage floor (F17) versus doc 00's `fail_under = 80` default and TST-026; image signing, SBOM, SAST, IaC scanner, image builder, approved registry; whether Claude Code is approved (F16); rotation period, privileged elevation and Key Vault settings (SCR-008, SCR-009, SCR-019); how a non-AI service trims `ai/`, `registry/`, `prompts/`, `evals/` (STR-001 requires an ADR to drop a standard directory).

Missing steps the reader listed, and what the template covers: bootstrap (`uv lock`, renaming placeholders, `.python-version`) and source skeletons (`main.py`, `observability.py`, `api/*`, ports, errors, health endpoint), `tests/conftest.py` Hypothesis profiles, the integration, contract and eval smoke tests, the missing dev dependencies, and a `docs/api/openapi.yaml` are all generated. Still missing from the standards: `scripts/registry_check.py`, `scripts/deploy.sh`, `scripts/mutation_gate.py` as files; `security.md`, `api-contracts.md` and the `code-reviewer` subagent have no text; three of the four starter skills; a runbook template; manual GitLab and Azure setup steps (branch protection, protected environments, squash template, Key Vault, federated credentials, the Terraform state bootstrap); a `Dockerfile.context-check` CI job; SBOM, scan, sign, `tf-apply`, scheduled-job and `.dockerignore` content jobs in the doc 16 skeleton (TODOs in the CI file).

Reader's lint trap, checked: doc 08's `# noqa: TRY004` in `check_agent_config.py` is unused under doc 00's rule set (RUF100); the template removed it (F-12). PRC-023 also forbids agents from adding `noqa` or per-file ignores; the template's `scripts/**` ignore is therefore a human-reviewed template decision, not something an agent should copy elsewhere.

## Cold-read status
The independent pass above is the cold-read of the row "Start a new service from scratch". It was a single fresh subagent read; I did not re-run it after the template fixes.
