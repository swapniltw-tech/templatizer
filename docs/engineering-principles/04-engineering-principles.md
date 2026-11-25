# Engineering Principles

> **Owner:** Architecture lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** none (internal standard). Ladder entry thresholds are owned by [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md).

## Purpose
These principles decide how much machinery a solution is allowed to have. The default is the simplest thing that works, deterministic code before model calls, fixed workflows before agents, and humans in the loop for anything consequential. This doc owns the **principles** and the **autonomy ladder**. Boundaries (import rules, service separation) live in [03-architecture.md](./03-architecture.md); concrete option choices live in [05-decision-playbook.md](./05-decision-playbook.md) and [26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md); security controls live in [02-security.md](./02-security.md).

## Approach ladder (what to try first)
Move to the next row only when evidence shows the row above cannot meet the requirement. Record the evidence in an ADR ([03-architecture.md](./03-architecture.md)).

| Step | Approach | Typical fit |
|---|---|---|
| 1 | Deterministic code and rules | Anything with a stated rule, formula, lookup or validation |
| 2 | Classical software with data (queries, search, statistics, small ML) | Matching, ranking, anomaly signals |
| 3 | One model call with structured output and schema validation | Extract, classify, summarize, draft |
| 4 | Fixed workflow (code decides the steps, model fills in steps) | Multi-step processing with known order |
| 5 | Agent (model chooses tools and next steps) within bounds | Open-ended tasks where steps cannot be known in advance |
| 6 | Multiple cooperating agents | Rarely justified; see PRN-009 |

## Autonomy ladder
Every AI agent runs at exactly one rung, declared in its registry manifest ([25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md)). A rung limits what the agent may do without a human. Entry criteria below are necessary, not sufficient: the evidence is the eval results and thresholds defined for that rung in [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md) (this doc states no numbers).

| Rung | Name | What the agent may do | Max tool side effects | Human role | Entry criteria (all required) |
|---|---|---|---|---|---|
| 0 | Suggest | Produce text or analysis shown to a human; no tool calls | none | Human reads and acts on everything | Registered manifest; owner named; schema-validated output; passes the rung 0 evals in 14 |
| 1 | Assist (read) | Call read-only tools to gather information and answer | none, read | Human reviews every output before use | Rung 0 criteria; tools registered and evaluated; per-user data access enforced; passes the rung 1 evals in 14 |
| 2 | Propose (approve each action) | Prepare write or external actions; none executes until a human approves that specific action | write, external, only after approval | Human approves each action | Rung 1 criteria; approval flow tested; audit logging in place; passes the rung 2 evals in 14, including adversarial and injection suites |
| 3 | Act (low risk, reversible) | Execute allow-listed low-risk, reversible actions on its own within budgets | none, read, low-risk reversible write | Sampled post-hoc review; kill switch tested | Rung 2 criteria; stable at rung 2 for an observation period agreed with AI governance (ASSUMPTION: period set per risk tier); passes the rung 3 evals in 14; runbook and kill switch exercised; governance sign-off |
| 4 | Act (bounded, higher risk) | Execute a wider set of actions, still within hard budgets and an allow-list; destructive and external actions still need approval | as rung 3 plus higher-risk writes | Review by exception and by sampling; automatic alerting | Rung 3 criteria; passes the rung 4 evals in 14; continuous online monitoring live; governance sign-off recorded in the inventory ([12-governance-and-compliance.md](./12-governance-and-compliance.md)) |
| 5 | Autonomous | Open-ended multi-step operation without per-action review | any | Oversight only | Not permitted by default. Requires a waiver ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)) and governance approval |

**Canonical rung identifiers** (used verbatim in registry manifests, `evals/<suite>/thresholds.yaml`, ADRs and the use-case catalog): `suggest` (0), `assist-read` (1), `propose` (2), `act-low-risk` (3), `act-bounded` (4), `autonomous` (5, waiver only). No other spelling is valid.

ASSUMPTION: the number of rungs and the cap in PRN-018 are proposals for AI governance (F1) to confirm.

## Rules

### Simplicity
- **PRN-001** [MUST] [review] The simplest design that meets the requirement MUST be chosen; added complexity (a new layer, service, framework, queue, model or agent) MUST be justified in the MR or ADR with the requirement it serves.
- **PRN-002** [MUST] [review] Code MUST NOT include speculative generality: no unused parameters, configuration flags, extension points, plugin systems or abstractions for requirements nobody has stated (YAGNI). An AI agent MUST NOT add features, endpoints or options beyond its task.
- **PRN-003** [SHOULD] [review] An abstraction SHOULD be introduced on the third real use, not the first or second; duplication of two similar blocks is cheaper than the wrong abstraction.
- **PRN-004** [SHOULD] [review] Existing standard-library and already-approved dependencies SHOULD be preferred over adding a package ([20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md) owns dependency rules).
- **PRN-005** [MUST] [review] Each module, function and class MUST have one clear reason to change; a change that touches many unrelated files MUST prompt a design review before more code is generated.

### Deterministic first
- **PRN-006** [MUST] [review] A requirement that can be met by a stated rule, formula, schema check or lookup MUST be implemented as deterministic code, not by a model call; business rules for coverage, pricing, eligibility and claims MUST live in `domain/` code that has unit tests ([24-testing-standards.md](./24-testing-standards.md)).
- **PRN-007** [MUST] [review] A solution MUST climb the approach ladder one step at a time; moving to a higher step MUST be justified by evidence (an eval or a prototype result) that the lower step fails the requirement.
- **PRN-008** [MUST] [review] If the steps are known in advance, the solution MUST be a fixed workflow written in code, with model calls only inside steps; an agent MUST NOT be used merely to avoid writing the workflow.
- **PRN-009** [MUST] [review] A multi-agent design MUST NOT be adopted without an ADR that shows a single agent or workflow was tried and failed measurable evals; inter-agent messages MUST be treated as untrusted input ([02-security.md](./02-security.md)).
- **PRN-010** [MUST] [review] An orchestration framework MUST NOT be added without an ADR; the default for a single call or a fixed workflow is no framework ([05-decision-playbook.md](./05-decision-playbook.md)).
- **PRN-011** [MUST] [test: tests/unit] Model output MUST be treated as untrusted input: it MUST be parsed against a schema and validated before it drives a branch, a tool call, a query or a user-visible claim.

### Autonomy ladder
- **PRN-012** [MUST] [ci: make registry-check] Every agent MUST declare its rung in its manifest, and the declared rung MUST NOT exceed what the agent's tools allow in the rung table; new agents MUST start at the lowest rung that delivers the use case.
- **PRN-013** [MUST] [review] An agent MUST NOT operate at a rung until all entry criteria for that rung are met and the owner (and, from rung 3, AI governance) has recorded the approval with a link to the eval results.
- **PRN-014** [MUST] [review] Rungs MUST be climbed one at a time; skipping a rung requires a waiver ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)).
- **PRN-015** [MUST] [ci: evals] Changing a prompt, model deployment, tool schema or tool set MUST re-run the evals for the agent's current rung before release ([14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md)).
- **PRN-016** [MUST] [runtime] An agent MUST be demoted by at least one rung, or stopped, when monitoring shows eval-threshold regression, an incident, or unexplained drift; promotion back repeats the entry criteria.
- **PRN-017** [MUST] [review] Rung 5 MUST NOT be used without a waiver and AI governance approval.
- **PRN-018** [MUST] [review] An agent whose output affects coverage, pricing, claims, eligibility or other decisions about a customer MUST NOT exceed rung 2, and the human who approves MUST be able to decide differently without the agent's help. ASSUMPTION: cap to be confirmed by AI governance (F1) and [12-governance-and-compliance.md](./12-governance-and-compliance.md).
- **PRN-019** [MUST] [review] Every rung change MUST be recorded in an ADR and in the model and agent inventory.

### Human in the loop
- **PRN-020** [MUST] [runtime] Destructive, irreversible, financial, external-communication and restricted-data-exposing actions MUST require human approval at every rung below 5; detail and controls live in [02-security.md](./02-security.md).
- **PRN-021** [MUST] [runtime] An approval request MUST show the exact action, its parameters and its risk; the approver MUST be a human other than the requester; approvals MUST be logged with who, what and when ([10-logging-observability.md](./10-logging-observability.md)).
- **PRN-022** [MUST] [runtime] An agent MUST NOT approve, bypass or reword its own approval requests, and MUST NOT cause another agent to approve them.
- **PRN-023** [MUST] [runtime] When the agent is uncertain, out of scope, or output validation fails, it MUST hand off to a human or return a safe refusal; it MUST NOT guess.
- **PRN-024** [SHOULD] [runtime] From rung 3, a sample of agent actions SHOULD be reviewed by humans at the rate set in [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md).
- **PRN-025** [RETIRED] [runtime] Superseded by REL-024 in [18-reliability-and-operations.md](./18-reliability-and-operations.md), which owns the kill switch.

### Bounded tool permissions
- **PRN-026** [MUST] [ci: make registry-check] An agent MUST be granted tools by explicit allow-list (tool id and version range) and deny by default; an unlisted tool MUST fail to bind ([25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md)).
- **PRN-027** [MUST] [test: tests/unit] Every agent loop MUST have hard limits on steps, tokens, wall-clock time and cost, and tests MUST show that exceeding a limit stops the loop with an error.
- **PRN-028** [MUST] [review] Tools that read data MUST act with the end user's permissions, not the agent's broader rights, so the agent cannot reveal what the user could not see ([19-rag-and-retrieval.md](./19-rag-and-retrieval.md) for retrieval).
- **PRN-029** [MUST] [review] Each tool MUST declare its side-effect class (none, read, write, destructive, external) and limits (rate, timeout, payload); the agent's rung MUST NOT allow a class above the rung table.
- **PRN-030** [MUST] [runtime] An agent MUST NOT modify its own prompts, tools, permissions, manifest or registry entries at runtime.
- **PRN-031** [MUST] [review] AI coding agents used in development MUST work within bounded permissions as well (allow-listed commands, no production access); the working rules are in [01-codebase-practices.md](./01-codebase-practices.md).

## Example: bounded loop with deny-by-default tools
Run on Python 3.14 with pytest, mypy strict and Ruff (tests passed; Ruff with `--select ALL` flagged only style items such as exception messages, not logic). It illustrates PRN-026 and PRN-027; real loops live in `ai/agents/` and call tools through the registry.

```python
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

READ_ONLY = frozenset({"lookup_policy"})


@dataclass(frozen=True)
class Budget:
    max_steps: int = 5
    max_tokens: int = 20_000


class BudgetExceededError(RuntimeError):
    pass


class ToolNotAllowedError(PermissionError):
    pass


def run_agent(
    next_action: Callable[[list[str]], tuple[str, str] | None],
    tools: dict[str, Callable[[str], str]],
    allowed: frozenset[str],
    budget: Budget,
) -> list[str]:
    """Deny-by-default tool loop with a hard step limit."""
    transcript: list[str] = []
    for _ in range(budget.max_steps):
        action = next_action(transcript)
        if action is None:
            return transcript
        name, arg = action
        if name not in allowed or name not in tools:
            raise ToolNotAllowedError(name)
        transcript.append(tools[name](arg))
    raise BudgetExceededError(f"more than {budget.max_steps} steps")
```
The example enforces the step limit only; token, time and cost limits (`max_tokens` is declared but not enforced here) must be enforced by the real loop. Tests that passed: a tool outside the allow-list raises, a never-ending loop stops at the step limit, and a finishing loop returns its transcript.

## Checklist
- [ ] The solution sits at the lowest step of the approach ladder that works; any step-up has evidence (PRN-007).
- [ ] No speculative parameters, flags or abstractions were added (PRN-002).
- [ ] Rules that can be code are code in `domain/` with tests (PRN-006).
- [ ] The agent's rung is declared, entry criteria are met, and eval results are linked (PRN-012, PRN-013).
- [ ] Decisions about customers are capped at rung 2 and a human decides (PRN-018).
- [ ] Destructive, financial and external actions require approval; the agent cannot approve itself (PRN-020, PRN-022).
- [ ] Tools are allow-listed and deny-by-default; loop limits are enforced and tested (PRN-026, PRN-027).
- [ ] A kill switch exists and has been exercised (REL-024).
- [ ] An ADR records any framework, multi-agent design or rung change (PRN-009, PRN-010, PRN-019).

## Common AI failure modes
- Reaches for an agent or framework when a fixed workflow or a single call suffices.
- Asks the model to apply a business rule that is a simple formula or lookup.
- Adds config options, extension points and base classes "for future use".
- Gives an agent a broad tool set "just in case", or reuses the agent's service identity for reads on behalf of users.
- Treats model output as trusted and uses it in a query, command or decision without validation.
- Builds loops with no step, token, time or cost limit.
- Lets an agent approve its own action, or merges the approver and requester roles.
- Claims a higher rung based on a demo instead of eval results.
- Designs several cooperating agents where one prompt and a workflow would do.

## Related docs
- [03-architecture.md](./03-architecture.md): boundaries and ADRs.
- [05-decision-playbook.md](./05-decision-playbook.md), [26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md): choosing patterns per case.
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md): thresholds that gate each rung.
- [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md): manifests that declare rung and tools.
- [02-security.md](./02-security.md): agentic threats and approval controls.
- [12-governance-and-compliance.md](./12-governance-and-compliance.md), [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md), [18-reliability-and-operations.md](./18-reliability-and-operations.md).
