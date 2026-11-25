# Architecture and Boundaries

> **Owner:** Architecture lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** import-linter docs (import-linter.readthedocs.io, contract types); pytest-archon README (github.com/jwbargsten/pytest-archon); MADR 4.0.0 (MADR project site, adr then github.io). Contracts in this doc were run on a toy package (see "Tested with").

## Purpose
This doc owns **boundaries**: which code may import which, how services are separated, how those rules are enforced by tests, and how architecture decisions are recorded. Principles (KISS, autonomy) live in [04-engineering-principles.md](./04-engineering-principles.md); option choices live in [05-decision-playbook.md](./05-decision-playbook.md). The folder layout itself is owned by [09-structure-and-format.md](./09-structure-and-format.md); this doc owns the dependency rules over it.

AI agents tend to take the shortest import path: a router that calls the database, a tool that calls an adapter, a domain function that calls a model. Boundary rules are therefore enforced by failing tests, not by prose.

## Layer map
Canonical package tree (inside `src/<package>/`; see 09):

| Package | Role | May import | MUST NOT import |
|---|---|---|---|
| `domain/` | Pure business logic | stdlib, `domain/` itself (ASSUMPTION: `common/` allowed) | everything else in the package; I/O, web, database, model SDKs |
| `application/` | Use cases, workflows, `ports.py` (Protocols) | `domain/`, `common/` | `adapters/`, `api/`, model SDKs |
| `adapters/` | All outbound I/O; implements ports | `application/ports`, `domain/`, `common/`, external SDKs | `api/`, `ai/agents`, `ai/tools` |
| `adapters/llm/` | The only module that talks to the model platform | as `adapters/`, plus model SDK | `api/`, `ai/agents`, `ai/tools` |
| `api/` | HTTP transport | `application/`, `domain/` models for mapping, `common/` | `adapters/` (ASSUMPTION: wiring happens in `main.py`, so `api/deps.py` takes injected ports), `ai/agents` internals |
| `ai/tools/` | One module per tool; implements a registry manifest | `application/` use cases, `domain/` models, `common/` | `adapters/`, `api/` |
| `ai/agents/` | One directory per agent | `ai/tools/`, `ai/prompts`, `ai/guardrails`, `adapters/llm`, `application/` | `api/`, other `adapters/` |
| `ai/retrieval/`, `ai/guardrails/` | RAG, input/output validation | `application/` ports, `domain/` | `api/` |
| `security/` | Authn/authz helpers | `common/`, `domain/` | `adapters/`, `ai/` |
| `common/` | Tiny shared utilities | stdlib only | everything else in the package |
| `main.py` | Composition root; wires adapters to ports | everything | nothing imports `main` |
| `config.py`, `observability.py` | Settings, telemetry setup | stdlib and its own SDKs | `domain/` MUST NOT import these |

Direction: `api -> application -> domain`; `adapters -> application ports`; `ai/tools -> application`; `ai/agents -> ai/tools, adapters/llm`.

## Rules

### Layering and dependencies
- **ARC-001** [MUST] [ci: import-linter] Source code MUST follow the canonical package tree and dependency direction in the layer map; new top-level packages require an ADR (ARC-029).
- **ARC-002** [MUST] [ci: import-linter] `domain/` MUST NOT import `api`, `application`, `adapters`, `ai`, `security`, `config`, `observability`, `main`, or any I/O, web, database or model-SDK package; `domain/` MUST be testable with no fakes at all.
- **ARC-003** [MUST] [ci: import-linter] Inbound dependencies MUST run `api -> application -> domain` only; `application` MUST NOT import `adapters` or `api`.
- **ARC-004** [MUST] [ci: import-linter] Adapters MUST implement Protocols declared in `application/ports.py` and MUST NOT import `api`, `ai/agents` or `ai/tools`.
- **ARC-005** [MUST] [ci: import-linter] `ai/tools/` modules MUST reach data and side effects only through `application` use cases and MUST NOT import `adapters` or `api`.
- **ARC-006** [MUST] [ci: import-linter] `ai/agents/` MUST use `ai/tools/` and `adapters/llm` and MUST NOT import `api` or any other adapter (`db`, `http_clients`, `queue`, `storage`, `keyvault`).
- **ARC-007** [MUST] [ci: import-linter] Model-platform SDKs (for example `azure`-namespace AI packages and `openai`) MUST be imported only from `adapters/llm/`; every model call MUST go through that wrapper (retries, timeouts, redaction, telemetry and output validation live there, see [23-azure-foundry-standards.md](./23-azure-foundry-standards.md)).
- **ARC-008** [MUST] [ci: import-linter] `main.py` MUST be the only place that constructs concrete adapters and injects them into use cases; no other module MAY import `main`.
- **ARC-009** [MUST] [ci: import-linter] `common/` MUST NOT import any other package module and MUST NOT contain business logic; if a helper needs domain knowledge, it belongs in `domain/`.
- **ARC-010** [SHOULD] [review] Dependency injection SHOULD be by constructor or function parameter against a Protocol; global singletons and module-level clients SHOULD NOT be used.

### Transport and domain separation
- **ARC-011** [MUST] [review] `api/routers` MUST only parse input, call one use case, and map the result or error to a response; business rules MUST NOT appear in routers or middleware.
- **ARC-012** [MUST] [review] Transport schemas (`api/schemas`) MUST be separate from domain models and MUST be mapped explicitly in one direction at the boundary; domain models MUST NOT be returned directly from an endpoint.
- **ARC-013** [SHOULD] [review] Domain errors SHOULD be mapped to transport errors in `api/errors.py` only; contract and format rules live in [17-api-and-contracts.md](./17-api-and-contracts.md).
- **ARC-014** [MUST] [review] LLM calls, prompt assembly and output parsing MUST NOT appear in `domain/`; a business rule that can be written as deterministic code MUST be written as deterministic code in `domain/` (see [04-engineering-principles.md](./04-engineering-principles.md)).

### Fitness tests
- **ARC-015** [MUST] [ci: lint-imports] Every repo MUST commit an import-linter configuration that encodes ARC-002 to ARC-009 and the `api` row of the layer map and MUST run `lint-imports` as part of `make lint`. ASSUMPTION: the standard Makefile target list has no architecture target, so the check is attached to `make lint`; the platform team confirms.
- **ARC-016** [MUST] [ci: lint-imports] The template MUST create every canonical package with an `__init__.py`, because import-linter fails with "Module ... does not exist" when a contract names a missing package; contracts MUST NOT be trimmed to hide missing packages.
- **ARC-017** [SHOULD] [test: pytest-archon] Rules that import-linter expresses poorly (naming, "every tool module has a manifest", custom predicates) SHOULD be written with pytest-archon in `tests/unit/architecture/`.
- **ARC-018** [MUST] [test: pytest-archon] Every pytest-archon rule MUST be proven to match modules; a `match()` pattern that selects no module fails the rule (verified: `NO CANDIDATES MATCHED`), and a rule with a typo MUST be fixed, not removed.
- **ARC-019** [MUST] [review] Agents MUST NOT edit import-linter configuration, `tests/unit/architecture/`, or add `ignore_imports` entries to make a violation pass; changes to these paths MUST be owned in `CODEOWNERS` by the architecture owner.
- **ARC-020** [MUST] [review] Each `ignore_imports` entry MUST carry a comment with an ADR or waiver reference and an expiry date ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)); stale ignores MUST be removed (import-linter reports unmatched ignores as errors by default).
- **ARC-021** [MUST] [ci: lint-imports] Imports under `if TYPE_CHECKING:` MUST NOT be used to bypass a boundary; the contracts MUST keep counting them (default behavior in the test run: a type-checking-only import of `adapters` from `domain` broke the contracts).
- **ARC-022** [SHOULD] [ci: lint-imports] Contracts SHOULD fail with guidance: set `broken_contract_guidance` or a clear `name` so an agent reading the failure knows which ADR or rule explains the boundary. VERIFY: `broken_contract_guidance` text format in the import-linter docs.

### Service boundaries and contracts
- **ARC-023** [MUST] [review] Each service MUST own its data store; no service MAY read or write another service's database, queue or storage directly.
- **ARC-024** [MUST] [review] Services MUST communicate only through versioned APIs or events ([17-api-and-contracts.md](./17-api-and-contracts.md)); shared libraries MAY hold technical utilities but MUST NOT hold domain logic or models used across services.
- **ARC-025** [SHOULD] [review] Service boundaries SHOULD follow a business capability, not a technical layer; a change that regularly needs coordinated releases of two services SHOULD be merged into one service or re-cut.
- **ARC-026** [MUST] [test: tests/contract] A service that calls another service or publishes events MUST have consumer-side contract tests, and a service that exposes an API or events MUST have provider-side contract tests ([24-testing-standards.md](./24-testing-standards.md) owns the test rules).
- **ARC-027** [MUST] [review] Outbound calls to other services MUST live in `adapters/http_clients` behind a port, with timeouts and retry policy per [18-reliability-and-operations.md](./18-reliability-and-operations.md).
- **ARC-028** [MUST] [review] Agents and tools MUST NOT call another service directly; they go through a use case and port, and each tool is a registered artifact ([25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md)).

### Architecture decision records
- **ARC-029** [MUST] [review] An ADR MUST be written for: a new service, a new data store, a new external dependency or vendor SDK, a new top-level package, an LLM pattern (RAG, agent, workflow), an autonomy rung change ([04-engineering-principles.md](./04-engineering-principles.md)), and any boundary exception.
- **ARC-030** [MUST] [review] ADRs MUST live in `docs/adr/NNNN-short-title.md`, use the MADR-style template below, and be numbered sequentially; an accepted ADR MUST NOT be edited except for its status, and a change of direction MUST be a new ADR that supersedes it.
- **ARC-031** [MUST] [review] A human decision-maker MUST set an ADR's status to `accepted`; AI agents MAY draft ADRs and MUST NOT accept them.
- **ARC-032** [SHOULD] [review] ADRs for AI use cases SHOULD answer the "ADR prompts" of the matching case in [26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md).
- **ARC-033** [MUST] [review] An ADR MUST list at least two considered options including "do nothing" or the simplest option, state consequences, and state how the decision will be verified (a fitness test, an eval, a metric).

## ADR template (MADR-style)
Based on MADR 4.0.0 headings (VERIFY: front matter field names against the MADR project site before generating a template in Copier). Save as `docs/adr/NNNN-short-title.md`.

```markdown
---
status: proposed        # proposed | accepted | rejected | deprecated | superseded by NNNN
date: YYYY-MM-DD
decision-makers: <roles>
consulted: <roles>
informed: <roles>
---

# <Short title: problem and chosen solution>

## Context and Problem Statement
<Two to five sentences. Include the regulatory or risk context if any.>

## Decision Drivers
- <driver, for example data class, latency, cost, autonomy rung>

## Considered Options
- <Option 1: simplest option or do nothing>
- <Option 2>

## Decision Outcome
Chosen option: "<option>", because <reason tied to drivers>.

### Consequences
- Good: <...>
- Bad: <...>

### Confirmation
<How compliance is checked: fitness test name, eval id, dashboard, review.>

## Pros and Cons of the Options
### <Option 1>
- Good, because <...>
- Bad, because <...>

## More Information
<Links to rules, use-case catalog entry, related ADRs, waiver id if any.>
```

## Fitness-test configuration
Tested with: Python 3.14, import-linter 2.17, pytest-archon 0.0.7 (toy package named `svc` with the canonical tree). A "tested with" record, not a pin; pins live in [00-tech-stack.md](./00-tech-stack.md). Keep the file in the repo root as `.importlinter`. VERIFY: import-linter also reads `pyproject.toml` (`[tool.importlinter]`); only the `.importlinter` file form was run.

```ini
[importlinter]
root_package = svc
include_external_packages = True

[importlinter:contract:layers]
name = Inbound layering: api -> application -> domain
type = layers
layers =
    svc.api
    svc.application
    svc.domain

[importlinter:contract:domain-pure]
name = Domain imports nothing outward and no I/O or framework or LLM libraries
type = forbidden
source_modules =
    svc.domain
forbidden_modules =
    svc.api
    svc.application
    svc.adapters
    svc.ai
    svc.security
    svc.config
    svc.observability
    svc.main
    httpx
    fastapi
    openai
    azure
    sqlalchemy

[importlinter:contract:api-no-adapters]
name = API receives adapters by injection and never imports them
type = forbidden
source_modules =
    svc.api
forbidden_modules =
    svc.adapters

[importlinter:contract:application-no-io]
name = Application depends on ports, never on adapters or api
type = forbidden
source_modules =
    svc.application
forbidden_modules =
    svc.adapters
    svc.api

[importlinter:contract:adapters-not-api]
name = Adapters never import the transport layer, agents or tools
type = forbidden
source_modules =
    svc.adapters
forbidden_modules =
    svc.api
    svc.ai.agents
    svc.ai.tools

[importlinter:contract:tools-no-adapters]
name = AI tools call use cases, never adapters or api
type = forbidden
source_modules =
    svc.ai.tools
forbidden_modules =
    svc.adapters
    svc.api

[importlinter:contract:agents-no-api]
name = Agents never import api or non-LLM adapters
type = forbidden
source_modules =
    svc.ai.agents
forbidden_modules =
    svc.api
    svc.adapters.db
    svc.adapters.http_clients
    svc.adapters.queue
    svc.adapters.storage
    svc.adapters.keyvault

[importlinter:contract:main-is-root]
name = Only the entry point may import main
type = forbidden
source_modules =
    svc.api
    svc.application
    svc.domain
    svc.adapters
    svc.ai
forbidden_modules =
    svc.main

[importlinter:contract:model-sdk-only-in-llm-adapter]
name = Model SDKs are imported only by adapters.llm
type = forbidden
source_modules =
    svc.api
    svc.application
    svc.domain
    svc.ai
forbidden_modules =
    azure
    openai
    httpx
allow_indirect_imports = True

[importlinter:contract:common-is-leaf]
name = common imports nothing from the package
type = forbidden
source_modules =
    svc.common
forbidden_modules =
    svc.api
    svc.application
    svc.domain
    svc.adapters
    svc.ai
    svc.security
    svc.config
    svc.observability
```

Results of the test run:
- All 10 contracts were kept on a toy tree that followed the layer map.
- Injecting one violation per contract (a model-SDK stand-in in `domain`, `application` importing `adapters`, a tool importing `adapters`, an agent importing `api`, `domain` importing `application`, a module importing `main`, `adapters` importing `api`, `api` importing `adapters`, a stand-in SDK import in `ai/tools`, `common` importing `domain`) broke the matching contracts (`lint-imports` exits non-zero when any contract breaks).
- External packages must be named at top level (`azure`, not `azure.ai`); the tool rejects subpackages of external packages ("Invalid forbidden module ... subpackages of external packages are not valid").
- `allow_indirect_imports = True` is required on the model-SDK contract, otherwise `ai/agents -> adapters/llm -> SDK` counts as a violation.
- The `layers` contract alone does not stop `domain` importing `adapters` (adapters is not in the stack); the `domain-pure` contract does. Keep both.
- ASSUMPTION: whether `domain/` may import `pydantic` is not settled by the canonical tree ("NO framework"). The contract above allows it. Decide in an ADR (F14); if forbidden, add `pydantic` to the `domain-pure` list.
- ASSUMPTION: `adapters/llm` and `ai/guardrails` both do redaction (see 09 and 23). The contract lets `ai/guardrails` import adapters and lets adapters import `ai/guardrails` and `ai/prompts`/`ai/retrieval`; only `ai/agents` and `ai/tools` are barred from being imported by adapters. Revisit when one home for redaction is chosen.
- ASSUMPTION: the layer map says `application` may be called by `ai/tools`, so `application` importing `ai/` would create a cycle; no contract forbids it yet because workflows that orchestrate an agent are undecided. Record the answer in an ADR before adding one (F15).

Optional pytest-archon test (run, passes on the good tree and fails on the injected-violation tree):

```python
from pytest_archon import archrule


def test_domain_is_pure() -> None:
    (
        archrule("domain-pure", comment="domain imports only domain")
        .match("svc.domain*")
        .should_not_import("svc*")
        .may_import("svc.domain*")
        .check("svc", only_direct_imports=True)
    )


def test_tools_do_not_touch_adapters() -> None:
    (
        archrule("tools-no-adapters")
        .match("svc.ai.tools*")
        .should_not_import("svc.adapters*")
        .check("svc")
    )
```
Without `only_direct_imports=True`, `check` includes transitive imports; use it when direct imports are the intent.

## Checklist
- [ ] New code sits in the correct canonical package and follows the layer map.
- [ ] `lint-imports` passes locally via `make lint`; no `ignore_imports` was added without ADR or waiver reference (ARC-020).
- [ ] Router functions contain no business rules (ARC-011); transport schemas are mapped, not reused (ARC-012).
- [ ] Model calls go only through `adapters/llm` (ARC-007); no business rule is delegated to a model when code can express it (ARC-014).
- [ ] Tools use use cases, not adapters (ARC-005); agents do not import `api` (ARC-006).
- [ ] Cross-service interaction has contract tests on both sides (ARC-026).
- [ ] An ADR exists for any new service, store, dependency, package, LLM pattern or exception (ARC-029).
- [ ] No architecture config or fitness test was edited to make a build pass (ARC-019).

## Common AI failure modes
- Imports an adapter directly from a router, tool or use case because it is the shortest path.
- Puts SQL, HTTP calls or model calls inside `domain/` or inside a Pydantic validator.
- Returns domain or ORM objects from endpoints, leaking internal fields.
- Adds `ignore_imports`, edits the contract, or hides an import behind `if TYPE_CHECKING:` to turn the build green.
- Creates a `utils.py` or `common/` module that grows business logic.
- Builds a new service or shared library with domain models imported by several services.
- Calls the model SDK straight from an agent, skipping the wrapper's redaction and validation.
- Writes an ADR with one option, no consequences, and marks it accepted.

## Related docs
- [09-structure-and-format.md](./09-structure-and-format.md): owns the folder tree these rules constrain.
- [04-engineering-principles.md](./04-engineering-principles.md): KISS, YAGNI, autonomy ladder.
- [05-decision-playbook.md](./05-decision-playbook.md), [26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md): choosing the pattern that an ADR records.
- [24-testing-standards.md](./24-testing-standards.md): contract and fitness test layout.
- [17-api-and-contracts.md](./17-api-and-contracts.md), [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md): the contracts between components.
- [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md): boundary exceptions.
