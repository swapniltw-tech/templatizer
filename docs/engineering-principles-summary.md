# Engineering Principles: Two-Page Summary

> **Status:** Draft summary · **Source of truth:** [engineering-principles/](./engineering-principles/README.md) (27 docs, rules numbered `AREA-NNN`). This page summarizes; it does not replace or restate rules. If it disagrees with a doc, the doc wins.

## Why these standards exist

Most of our code is now written by AI coding agents, in a federally regulated (OSFI) financial institution. Agents are fast and confident, and they take the shortest path: a router that calls the database, a quiet `# type: ignore`, an invented package. So the standards are **imperative, numbered and checkable**, and wherever possible a failing test or CI job enforces them instead of prose. Engineers and agents follow the same rules.

Terms: `MUST` is a hard requirement. `SHOULD` is the default unless a reason is recorded in the MR. `MUST` rules can only be bypassed through a waiver ([21](./engineering-principles/21-exceptions-and-waivers.md)); an agent never grants itself one (PRC-020).

## Seven principles

1. **Simplest thing that works** (PRN-001 to PRN-005). Added layers, services, frameworks or models must name the requirement they serve. No speculative generality; abstract on the third real use.
2. **Deterministic before model** (PRN-006 to PRN-011). Anything with a stated rule or formula is plain code. Business rules for coverage, pricing, eligibility and claims live in unit-tested `domain/` code. Model output is untrusted input: parse it against a schema before it drives anything.
3. **Climb the approach ladder one step at a time.** Deterministic code, then data and search, then one model call, then a fixed workflow, then a bounded agent, then (rarely) several agents. Each step up needs evidence, recorded in an ADR.
4. **Bounded autonomy.** Every agent runs at exactly one rung of a 0 to 5 ladder (`suggest`, `assist-read`, `propose`, `act-low-risk`, `act-bounded`, `autonomous`). Rungs are climbed one at a time with eval evidence. Rung 5 needs a waiver. An agent that affects a customer decision stays at rung 2 or below (PRN-018, an `ASSUMPTION` pending AI governance).
5. **Humans decide what matters.** Destructive, financial, external-communication and restricted-data actions need human approval below rung 5. An agent never approves, rewords or bypasses its own approval (PRN-020 to PRN-022). When unsure, it hands off or refuses; it does not guess (PRN-023).
6. **Least privilege, deny by default.** Tools are granted by explicit allow-list. Every agent loop has hard limits on steps, tokens, time and cost (PRN-026, PRN-027). Tools read with the end user's permissions, not the agent's.
7. **Tests are the proof.** Write the failing test first. Never weaken, skip or delete a test to get green (PRC-024). Evals are the tests for non-deterministic behavior ([14](./engineering-principles/14-evals-and-testing-ai.md)).

## Non-negotiables for AI coding agents

| Rule | ID |
|---|---|
| Never read, print, commit or paste secrets, `.env` files, keys or real customer data | PRC-022, SCR-029 |
| Never bypass checks: no `--no-verify`, no `allow_failure: true`, no new `noqa` or `type: ignore` to get green | PRC-023 |
| Run `make check`, report the real result, list anything not run | PRC-025 |
| Protected paths (`.gitlab-ci.yml`, `CODEOWNERS`, `.claude/`, `.mcp.json`, lint and import config, `Makefile`) need a human CODEOWNER | PRC-026 |
| Keep the diff to the task: no drive-by refactors, files or dependencies | CLN-038 |
| Never invent a flag, version, config key or SDK call; mark it `VERIFY:` | README |
| No new dependency, MCP server, tool or model without an ADR and registry entry | AGENTS.md, [25](./engineering-principles/25-ai-tool-and-agent-registry.md) |

## How the standards are organized

| Area | Docs | Covers |
|---|---|---|
| Foundations | 00 to 05 | Tech stack and Makefile, codebase practices, security, architecture boundaries, principles, decision playbook |
| Hygiene | 06 to 11 | Secrets and env, ignore files, agent config files, structure and naming, logging, clean code |
| Governance | 12, 13, 15, 21 | Risk tiering and inventory, data classification and privacy, model governance, waivers |
| Delivery and runtime | 16 to 18, 20, 24 | CI/CD, API contracts, reliability, dependencies and licensing, testing |
| AI-specific | 14, 19, 23, 25, 26 | Evals, RAG, Microsoft Foundry, tool and agent registry, use-case catalog |
| Cross-cutting | 22 | English and French output, accessibility |

Rule IDs use a three-letter prefix per doc (for example `SEC`, `ARC`, `TST`) and are never renumbered or reused. Each doc has a Checklist and a "Common AI failure modes" section.

## Key defaults

- **Platform:** Python, `uv`, Ruff, mypy `--strict`, pytest, Makefile, Docker. GitLab for code and CI/CD; Terraform for infrastructure (planned). LLMs only through Microsoft Foundry.
- **Layering:** `api -> application -> domain`; `adapters` implement ports; `domain/` is pure (no I/O, no model imports). Boundaries are enforced by import-linter and fitness tests, not review.
- **Quality gate:** `make check` locally equals CI. Coverage floors by service tier A, B, C of 90, 85 and 80 (proposals, `ASSUMPTION`).
- **Secrets:** Azure Key Vault and workload identity; `.env` is local only; `pydantic-settings` is the only env reader.
- **Decisions:** one topic, one home doc; deviations are recorded in an ADR citing the rule ID.

## What agents and engineers load

Do not load every doc. Use the task-to-docs routing table in the [README](./engineering-principles/README.md). In a generated service, the template's `AGENTS.md` carries the commands and never-list, `.claude/rules/` carries the review-only rules scoped by path, and the GitLab Duo files in `.gitlab/duo/` carry the same rules for Duo. Those rule files are generated from the docs, so the standards stay the single source.

## Open items that change the standards

Which models count as approved (F2), GitLab tier and runners (F4), the license allow list (F7), numeric parameters such as tier floors and waiver durations (F17), whether Claude Code is approved tooling (F16), and the Quebec language and WCAG level (F6). Each is marked `ASSUMPTION:` where used. The full list is in the README.
