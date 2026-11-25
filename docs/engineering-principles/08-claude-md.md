# CLAUDE.md, AGENTS.md and Agent Configuration

> **Owner:** Platform Engineering lead with Security lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** code.claude.com/docs (memory and CLAUDE.md, settings, permissions, hooks, skills, sub-agents, MCP, managed settings pages); published JSON schema for Claude Code settings; behavior checked against Claude Code 2.1.332 on 2026-11-25

## Purpose
Specify the files that steer AI coding agents in a repository: `CLAUDE.md` and `AGENTS.md`, `.claude/rules/`, `.claude/settings.json`, hooks, skills, subagents and `.mcp.json`, plus the personal files that stay out of Git and the organization-level baseline. Instruction files shape what an agent *tries*; permissions and hooks shape what it can *do*; CI and protected branches are what actually *enforce*. This doc keeps those three straight.

Every block below that is marked "Checked" was validated against the real tool on 2026-11-25 (see "How these were checked"). Anything else is marked `VERIFY:`.

ASSUMPTION (F16): Claude Code is approved developer tooling. "Foundry only" in the recorded decisions covers the LLMs that products call at runtime; it does not say whether coding assistants are approved. Confirm with AI governance and Security (F2, F5) before using Claude Code on repositories that hold restricted data. Claude Code is developer tooling, not a runtime dependency of any service.

## Rules

### CLAUDE.md and AGENTS.md
- **AGT-001** [MUST] [ci: scripts/check_agent_config.py] Every repo MUST have a committed `CLAUDE.md` at the repository root, at most 200 lines. Claude Code's own guidance is to stay under about 200 lines; longer files cost context and reduce adherence.
- **AGT-002** [MUST] [review] `CLAUDE.md` MUST contain: purpose in one sentence, the exact commands (matching Makefile targets), an architecture summary with the dependency rule, where things live, a "never" list, the workflow, how to find the org standards, and when to escalate. The template below is the starting point.
- **AGT-003** [MUST] [review] `CLAUDE.md` MUST NOT contain secrets, credentials, customer data, personal data, internal production URLs or anything that would be a leak if the repo were cloned by a contractor.
- **AGT-004** [MUST] [review] `CLAUDE.md` MUST NOT restate standards or tool configuration that live elsewhere (linter rules, formatter settings, the standards docs). Link or name the source and say when to read it.
- **AGT-005** [MUST] [review] Every instruction MUST be specific and checkable ("run `make check`", not "write good code"), and every command MUST be copy-paste runnable and match a `Makefile` target.
- **AGT-006** [MUST] [review] If the repo has an `AGENTS.md`, `CLAUDE.md` MUST import it with `@AGENTS.md` as its first line and add only Claude-specific content below. Per Claude Code docs, when both files exist Claude reads only `CLAUDE.md`, so a prose pointer ("see AGENTS.md") is dead text. A symlink is NOT allowed (Windows contributors, and edit tools refuse to write through it).
- **AGT-007** [MUST] [review] There MUST be one source of truth for tool-neutral instructions: either `AGENTS.md` (imported) or `CLAUDE.md`, never two diverging copies.
- **AGT-008** [SHOULD] [review] Contradictory or stale instructions SHOULD be removed at least quarterly and after any incident involving agent behavior; the docs warn that conflicting instructions are resolved arbitrarily.
- **AGT-009** [MAY] [review] Maintainer notes MAY be written as block-level HTML comments; Claude Code strips them before injecting the file into context.

### Rules files, skills, subagents
- **AGT-010** [MUST] [ci: scripts/check_agent_config.py] Topic or path-specific guidance MUST go in `.claude/rules/*.md`, at most 100 lines each, one topic per file. Path-scoped rules MUST use YAML frontmatter with a `paths:` list and every glob MUST be quoted (an unquoted `**/*.py` is a YAML error, and Claude Code then ignores the frontmatter and loads the rule for every file).
- **AGT-011** [MUST] [ci: scripts/check_agent_config.py] `paths` is the only frontmatter field Claude Code reads in a rule; other fields are silently ignored. Rules MUST NOT use any other frontmatter field.
- **AGT-012** [MUST] [review] Skills MUST live at `.claude/skills/<name>/SKILL.md` with `name` and a `description` that says what the skill does and when to use it. Skills with side effects (scaffolding, commits, deployments) MUST set `disable-model-invocation: true` so only a human starts them.
- **AGT-013** [MUST] [review] `allowed-tools` in a skill MUST list only the exact commands the skill needs. Unknown frontmatter fields are silently ignored, so field names MUST be checked against the lists in this doc.
- **AGT-014** [MUST] [ci: scripts/check_agent_config.py] Subagents MUST live at `.claude/agents/<name>.md`, MUST set an explicit `tools` allowlist, and review-style subagents MUST also set `disallowedTools: Write, Edit, Bash`.
- **AGT-015** [SHOULD] [review] Subagents SHOULD set `maxTurns` and `model: inherit` unless an ADR justifies another model. Models inside Claude Code are developer tooling; product models follow the governance list.

### Settings and permissions
- **AGT-016** [MUST] [ci: scripts/check_agent_config.py] `.claude/settings.json` MUST be committed, be strict JSON (no comments or trailing commas), start with the `$schema` line, and validate against the published schema. Changes MUST be approved by the security code owners (see [09-structure-and-format.md](./09-structure-and-format.md)).
- **AGT-017** [MUST] [review] Allow rules MUST name specific commands (`Bash(make check)`, `Bash(uv run --locked pytest *)`). `Bash`, `Bash(*)`, `Bash(bash *)`, `Bash(sh *)`, `Bash(python *)` and a bare `Bash(uv run *)` MUST NOT be allowed, because each lets an agent run arbitrary code.
- **AGT-018** [MUST] [ci: scripts/check_agent_config.py] (the script checks the `.env*` denies; the rest is reviewed) The shared settings MUST deny reading `.env*` (with the `.env.example` carve-out), key files and `secrets/`, MUST deny editing `uv.lock` and state files, and MUST deny `terraform apply`, `terraform destroy`, force push, `curl`, `wget` and secret-printing commands.
- **AGT-019** [MUST] [review] `git commit` and `git push` MUST be `ask` rules, and edits to `.claude/`, `.mcp.json`, `CODEOWNERS` and `.gitlab-ci.yml` MUST be `ask` rules, so a human sees each one.
- **AGT-020** [MUST] [review] Deny and ask rules MUST NOT be described or relied on as a security boundary. The permissions docs state that `Bash(...)` rules match command text (so `/usr/bin/curl`, `sh -c '...'` and `git -C . push` can slip past), and that `Read` deny rules do not stop a shell command or script from reading the file. Real controls are CI, protected branches, per-identity least privilege, network egress limits and sandboxing.
- **AGT-021** [MUST] [ci: managed settings] `bypassPermissions` and `auto` MUST NOT be the default mode in any repo file, and bypass mode MUST be disabled by managed settings (`permissions.disableBypassPermissionsMode: "disable"`). `--dangerously-skip-permissions` MUST NOT be used on a machine or runner that can reach real credentials.
- **AGT-022** [MUST] [review] Developers MUST NOT put allow rules for production tooling in `.claude/settings.local.json`; approvals given with "Yes, and don't ask again" are saved there and MUST be reviewed periodically.
- **AGT-023** [MUST] [manual] After editing any agent file, the author MUST run `claude doctor` in the repo and confirm there is no "Invalid settings" section, and run `/status` to confirm which setting sources loaded.

### Hooks
- **AGT-024** [MUST] [review] Hooks MUST be scripts under `.claude/hooks/` (reviewed code), referenced with `${CLAUDE_PROJECT_DIR}` in exec form (`"args": []`). Inline shell one-liners in settings MUST NOT be used.
- **AGT-025** [MUST] [test: unit] A hook that protects something MUST fail closed (exit 2 when its input cannot be parsed), and every hook script MUST be tested with sample stdin before it is committed.
- **AGT-026** [MUST] [review] Hooks are guardrails and fast feedback; CI is the enforcement. A hook MUST NOT be the only control for any `MUST` rule.
- **AGT-027** [SHOULD] [review] `PostToolUse` hooks SHOULD be quick (formatter and linter on the edited file only, timeout 60 seconds or less). Whole-repo gates belong in `make check`.

### MCP
- **AGT-028** [MUST] [review] `.mcp.json` MUST contain only organization-approved servers that exist in the registry, each with an explicit `"type"` (a `url` without `type` is a configuration error). Vetting rules are in [02-security.md](./02-security.md) and [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md).
- **AGT-029** [MUST] [ci: gitleaks] `.mcp.json` MUST NOT contain credentials; use `${VAR}` expansion with the value set in the developer's environment or fetched at login. Unset variables only produce a warning, so a missing token fails at first use.
- **AGT-030** [MUST] [review] `enableAllProjectMcpServers` MUST NOT be set to `true` in a shared file. Developers approve project servers individually.

### Personal files and org baseline
- **AGT-031** [MUST] [ci: scripts/check_ignore.sh] `.claude/settings.local.json` and `CLAUDE.local.md` MUST be gitignored (rules in [07-ignore-files.md](./07-ignore-files.md)). Personal files MUST NOT carry team rules; a local file can add allow rules but cannot override a deny.
- **AGT-032** [MUST] [review] The platform team MUST deliver an organization baseline through managed settings on every developer machine and CI image (macOS `/Library/Application Support/ClaudeCode/`, Linux `/etc/claude-code/`, Windows `C:\Program Files\ClaudeCode\`). Managed settings sit above every other scope and cannot be overridden by `--settings` or local files.
- **AGT-033** [SHOULD] [review] The baseline SHOULD set behavior guidance in a managed `CLAUDE.md` and technical enforcement in managed settings; the docs recommend settings for blocking and CLAUDE.md for guidance.
- **AGT-034** [MUST] [review] Developers MUST NOT use Claude Code on repositories that contain restricted data, and MUST NOT paste restricted data into prompts, until the classification rules in [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md) and the assumption above are confirmed.

## File inventory

| File | Purpose | Committed |
|---|---|---|
| `CLAUDE.md` | Project context: commands, architecture summary, never-list, pointers | yes |
| `AGENTS.md` | Tool-neutral instructions for other agents; imported by `CLAUDE.md` with `@AGENTS.md` | yes (optional) |
| `.claude/rules/*.md` | Scoped rules; `paths:` frontmatter loads them only for matching files | yes |
| `.claude/settings.json` | Permissions, hooks, env | yes |
| `.claude/hooks/*.sh` | Scripts the hooks call | yes |
| `.claude/skills/<name>/SKILL.md` | Reusable procedures | yes |
| `.claude/agents/<name>.md` | Subagents with restricted tools | yes |
| `.mcp.json` | Approved MCP servers only | yes |
| `.claude/settings.local.json`, `CLAUDE.local.md` | Personal overrides | **no (gitignored)** |
| `managed-settings.json`, managed `CLAUDE.md` | Org baseline, outside the repo | no (platform team) |

### How Claude Code loads these (from the docs)
- `CLAUDE.md` and `CLAUDE.local.md` load from the working directory and every directory above it at launch; files in subdirectories load on demand when Claude touches files there. All discovered files are concatenated, not overridden.
- `.claude/CLAUDE.md` is an accepted alternative location; this standard uses the root file.
- `@path/to/file` imports expand into context (relative to the importing file, up to four hops of recursion). Imports do not reduce context cost. Imports inside code spans and fenced blocks are not expanded.
- `AGENTS.md`: with no `CLAUDE.md` anywhere above the working directory, Claude reads `AGENTS.md`; with both, only `CLAUDE.md` (hence AGT-006). A `CLAUDE.local.md` also counts as a `CLAUDE.md` for that check. Reading `AGENTS.md` directly needs Claude Code v2.1.277 or later.
- Rules without `paths` load at launch; with `paths` they load when Claude reads, writes or edits a matching file. Patterns are relative to the directory containing `.claude/`.
- Settings precedence, highest first: managed, command line, project local, shared project, user. List keys such as `permissions.allow` merge across files. Within permissions, deny is evaluated before ask before allow, and the first match wins, so an allow cannot carve an exception out of a deny.
- Allow rules in the committed `.claude/settings.json` apply only after each developer trusts the folder (running `claude doctor` in an untrusted folder reports "Ignoring N permissions.allow entries ... has not been trusted"). `deny` and `ask` rules apply immediately.

## Template: `CLAUDE.md`

82 lines. Checked: the file is under the 200-line limit and passes `scripts/check_agent_config.py`. It deliberately does not cite other docs' rule IDs, because IDs are owned by those docs; agents are told to cite IDs in MR descriptions using the standards repo. Replace the placeholders in angle brackets.

```markdown
# <service-name>

<One sentence: what this service does, for whom, and its risk tier.>

<!-- Maintainer note (stripped from context): keep this file under 200 lines. Move topic detail
into .claude/rules/, and put commands and facts here only if an agent cannot derive them from code.
If this repo has an AGENTS.md, keep tool-neutral content there and make the first line of this
file the import `@AGENTS.md`; Claude Code reads only CLAUDE.md when both exist. -->

## Commands (always use these, never ad-hoc equivalents)

| Task | Command |
|---|---|
| Install | `make install` |
| Format | `make fmt` |
| Lint, types | `make lint`, `make typecheck` |
| Tests | `make test-unit`, `make test`, `make test-integration` |
| Model evals | `make eval` (costs money; ask first) |
| Full gate (same as CI) | `make check` |
| Security scan | `make security` |
| Run locally | `make run` |

Run `make check` and see it pass before you say a task is done or open a merge request (MR).

## Architecture in five lines

- `src/<package>/` is layered: `api -> application -> domain`; `adapters` implement `application/ports.py`.
- `domain/` is pure: no I/O, no framework, no LLM imports.
- All outbound I/O lives in `adapters/`; models are called only through `adapters/llm/`.
- `ai/tools/` call `application/` use cases, never adapters. `ai/agents/` never import `api/`.
- `config.py` is the only place that reads the environment; `main.py` is the only composition root.

Dependency rules are enforced by import-linter in `make check`. Do not add an exception; ask.

## Where things live

| Path | What |
|---|---|
| `docs/api/openapi.yaml` | API contract (change it first) |
| `docs/adr/` | Decisions (MADR); add an ADR for any new dependency, layer or pattern |
| `registry/` | Tool and agent manifests; every tool and agent is registered |
| `prompts/` | Versioned prompts (never inline prompts in Python) |
| `evals/` | Datasets (synthetic only), evaluators, `thresholds.yaml` |
| `infra/` | Terraform; plan only |
| `.claude/rules/` | Path-scoped rules; load when you touch matching files |

## Hard rules (never)

- Never commit, print, log or paste secrets, tokens, customer data or personal data. Use fake values.
- Never read or edit `.env*` (except `.env.example`), `secrets/`, key files or `uv.lock` by hand.
- Never run `terraform apply` or `destroy`, `git push --force`, or anything against production.
- Never weaken, skip or delete a test to make it pass. Write the failing test first.
- Never add a dependency, MCP server, tool or model without an ADR and registry entry.
- Never approve your own MR, edit `CODEOWNERS`, grant yourself a waiver, or bypass a `MUST` rule.
- Never use `git add -f`, `--no-verify` or `--dangerously-skip-permissions`.
- Never invent a flag, version, config key or SDK call. If unsure, say so and mark it `VERIFY:`.

## Workflow

1. Read the relevant rule file in `.claude/rules/` and the code you will touch.
2. Write the failing test, then the smallest change that passes it.
3. Run `make check`. Fix everything it reports; do not silence checks.
4. Commit with a Conventional Commit subject (`feat(api): ...`, `fix(domain)!: ...`).
5. Open a small MR. Cite rule IDs (format `AREA-NNN`) in the description for each deviation or notable decision.

## Org standards (single source of truth; do not copy them here)

Standards repo: `<standards-repo-url>`. Read only what the task needs:

| Task | Read |
|---|---|
| New endpoint | API and contracts, architecture, structure, testing |
| New agent or tool | Registry, security, LLM governance, evals |
| Logging or telemetry | Logging and observability, data classification |
| Secrets or config | Secrets and environment |
| Anything unclear or a possible rule conflict | Ask a human; do not guess |

## Escalate to a human when

- A rule seems to conflict with the task, or a `MUST` would have to be bypassed (waiver process).
- The change touches auth, personal data, payments, claims or coverage decisions.
- `make check` fails for a reason you cannot fix without changing a standard or a threshold.
```

## Template: `.claude/rules/`

All four files were parsed with PyYAML (frontmatter) and have quoted globs. `python-style.md` has no frontmatter, so it always loads; the others load only for matching files.

`.claude/rules/python-style.md`
```markdown
# Python style (always loaded)

- Run `make fmt` after edits and `make check` before declaring work done.
- Type every function; `mypy --strict` must pass. A `# type: ignore[code]` needs a reason comment.
- Keep functions small and named for the domain (`approve_claim`, not `process`).
- No `print`, no bare `except`, no mutable default arguments.
- Raise typed domain errors from `domain/errors.py`; never return error strings.
```

`.claude/rules/testing.md`
```markdown
---
paths:
  - "tests/**"
  - "evals/**"
---

# Tests and evals

- Write the failing test first, then the code. Never weaken, skip or delete a test to make it pass.
- Unit tests never call the network or a live model; inject the fake model client.
- Test data is synthetic. Never paste real customer data or real identifiers.
- Mirror the source tree: `tests/unit/<layer>/test_<module>.py`; name tests `test_<behavior>`.
- Mark slow or external tests with `@pytest.mark.integration`; model-quality checks with `@pytest.mark.eval`.
```

`.claude/rules/llm-and-agents.md`
```markdown
---
paths:
  - "src/*/ai/**"
  - "registry/**"
  - "prompts/**"
---

# LLM and agent code

- Models are called only through `adapters/llm/` (retries, timeouts, redaction, schema validation).
- A tool in `ai/tools/` implements exactly one manifest in `registry/tools/` and calls `application/` use cases, never adapters.
- Agents never import `api/`. Prompts live in `prompts/` and load through `ai/prompts/loader.py`.
- Never log prompts, completions or retrieved documents without the redaction step.
- Changing a prompt, tool schema or model deployment means re-running `make eval` and committing the result reference.
```

`.claude/rules/infra-terraform.md`
```markdown
---
paths:
  - "infra/**"
---

# Terraform

- Plan only. Never run `terraform apply` or `destroy`; the pipeline applies after merge.
- No secrets, state files or `*.tfvars` with secrets in the repo; reference Key Vault by name.
- One module per concern, pinned provider versions, and `.terraform.lock.hcl` committed.
- Every resource gets owner and environment tags.
```

## Template: `.claude/settings.json`

Checked three ways on 2026-11-25: (1) strict JSON; (2) validated against the published schema (Draft 7, zero errors, and the same validator rejects a string where `allow` needs an array and an unknown hook type); (3) `claude doctor` reported no "Invalid settings" section, and reported a malformed rule and a misspelled hook event name when I broke the file on purpose. Deny behavior was exercised with real Claude Code reads: `.env`, `secrets/*` and `*.pem` were denied, `.env.example` and an ordinary file were allowed.

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(make check)",
      "Bash(make fmt)",
      "Bash(make lint)",
      "Bash(make typecheck)",
      "Bash(make test)",
      "Bash(make test-unit)",
      "Bash(make test-integration)",
      "Bash(uv run --locked pytest *)",
      "Bash(uv run --locked ruff *)",
      "Bash(uv run --locked mypy *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ],
    "ask": [
      "Bash(make eval)",
      "Bash(make build)",
      "Bash(git commit *)",
      "Bash(git push *)",
      "Edit(./.claude/**)",
      "Edit(./.mcp.json)",
      "Edit(./CODEOWNERS)",
      "Edit(./.gitlab-ci.yml)"
    ],
    "deny": [
      "Read(.env)",
      "Read(.env.*)",
      "Read(!.env.example)",
      "Read(secrets/**)",
      "Read(*.pem)",
      "Read(*.key)",
      "Edit(./uv.lock)",
      "Edit(./**/*.tfstate)",
      "Bash(terraform apply *)",
      "Bash(terraform destroy *)",
      "Bash(git push --force *)",
      "Bash(git push -f *)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(printenv *)",
      "Bash(az keyvault secret show *)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-protected-paths.sh",
            "args": [],
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/lint-after-edit.sh",
            "args": [],
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

Notes on the permission rules:
- Syntax: `Tool` or `Tool(specifier)`. `Bash(make test-unit)` is an exact command; a trailing ` *` (space then asterisk) matches any arguments and also the bare command. `Bash(ls *)` does not match `lsof`; `Bash(ls*)` does.
- Read and Edit rules use gitignore-style patterns. A bare `.env` matches at any depth under the working directory. A leading `//` means an absolute filesystem path and `~/` the home directory. A single leading `/` anchors at the settings file's source, not the filesystem root.
- The carve-out `Read(!.env.example)` must come after the deny it carves from, in the same file. A first attempt written as `Read(!./.env.example)` did **not** allow the file when tested; the form above did. Test any path pattern you write.
- Per the docs a `Read` deny also blocks `Edit` and `Write` on the same path, and the `.env.example` carve-out covers that too. Tested: with `acceptEdits`, a real session wrote `.env.example` and left `.env` unwritten; in that run the agent refused `.env` itself, citing the never-list in `CLAUDE.md`, so VERIFY: the deny's own effect on writes was not isolated.
- `permissions.deny` entries `Bash(curl *)` match the typed command only; the docs recommend WebFetch with a domain allowlist for approved sites.
- Compound commands are split on `&&`, `||`, `;`, `|`; every part must match an allow rule. Deny rules match if any part matches.
- The `Edit(./.claude/**)` ask rule means an agent can still change its own settings after a human confirms. That is intended; the CODEOWNERS rules in [09-structure-and-format.md](./09-structure-and-format.md) are the second lock.

## Template: hooks

Hook schema (from the hooks docs): `hooks` maps an event name to an array of `{ matcher, hooks: [ { type, command, args, timeout } ] }`. For `PreToolUse` and `PostToolUse` the script receives JSON on stdin including `tool_name` and `tool_input.file_path`. Exit 0 means success; exit 2 blocks (on `PreToolUse`) or feeds stderr back to Claude (on `PostToolUse`); any other non-zero exit is a non-blocking error. A `PreToolUse` hook can also print `hookSpecificOutput.permissionDecision` as `deny` with a reason. A `matcher` of letters, digits, `_`, `-`, `,` and `|` is an exact tool-name list (`Edit|Write`); other characters make it a regular expression. Event names are validated: a misspelling is ignored with a warning (see `claude doctor`). The scripts need `jq`.

`.claude/hooks/block-protected-paths.sh` (tested with sample stdin: `.env`, `.env.local`, `uv.lock` and `*.tfstate` are denied; `.env.example` and ordinary source files pass; empty input exits 2):
```bash
#!/usr/bin/env bash
# PreToolUse hook (Edit|Write): block edits to files that agents must never change by hand.
# Fails closed: if jq is missing or the input is unreadable, the edit is blocked.
set -u
FILE=$(jq -r '.tool_input.file_path // empty' 2>/dev/null) || FILE=""
if [ -z "$FILE" ]; then
  echo "block-protected-paths: could not read tool_input.file_path; blocking edit" >&2
  exit 2
fi
case "$FILE" in
  */.env.example) exit 0 ;;
  */.env|*/.env.*|*/uv.lock|*.tfstate|*.tfstate.*|*/.git/*)
    jq -n --arg f "$FILE" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: ("Protected file, edit it through the proper tool or ask a human: " + $f)
      }
    }'
    exit 0
    ;;
esac
exit 0
```

`.claude/hooks/lint-after-edit.sh` (tested: unfixable lint error exits 2 with the message; clean Python and non-Python files exit 0):
```bash
#!/usr/bin/env bash
# PostToolUse hook (Edit|Write): format and lint the edited Python file.
# Exit 2 sends the output back to the agent as feedback; CI remains the real gate.
set -u
FILE=$(jq -r '.tool_input.file_path // empty' 2>/dev/null) || exit 0
case "$FILE" in
  *.py) ;;
  *) exit 0 ;;
esac
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
uv run --locked ruff format --quiet "$FILE" >/dev/null 2>&1
if ! OUTPUT=$(uv run --locked ruff check --fix "$FILE" 2>&1); then
  printf 'ruff check failed for %s:\n%s\n' "$FILE" "$OUTPUT" >&2
  exit 2
fi
exit 0
```

Both scripts must be executable (`chmod +x .claude/hooks/*.sh`). VERIFY: the hook scripts were run directly with sample JSON, not through a live Claude Code edit; run one real edit after adopting them. Optional hooks (for example a `Stop` hook running `make check`) were not tested and are not part of the standard.

## Template: skill

Fields accepted in `SKILL.md` frontmatter per the skills docs: `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`. Unknown fields are ignored without an error. `.claude/commands/*.md` still works, but skills are recommended for new work. Starter skills for the template: `add-endpoint`, `add-eval`, `write-adr`, `add-tool` (each with `disable-model-invocation: true`).

`.claude/skills/add-endpoint/SKILL.md` (frontmatter parsed with PyYAML, field names checked against the list above):
```markdown
---
name: add-endpoint
description: Adds a new HTTP endpoint following the layered structure (OpenAPI first, router, use case, tests). Use when the user asks to add or change an API endpoint.
argument-hint: "[METHOD /path]"
disable-model-invocation: true
allowed-tools:
  - Bash(make check)
  - Bash(make test-unit)
---

# Add an endpoint: $ARGUMENTS

1. Update `docs/api/openapi.yaml` first (path, request and response schemas, error responses as problem details).
2. Add or reuse a use case in `src/<package>/application/use_cases/`. Business rules go in `domain/`, never in the router.
3. Add the router function and schemas in `src/<package>/api/`. Routers only translate and call the use case.
4. Write the failing unit test first, then the code. Add a contract test if the OpenAPI file changed.
5. Run `make check`. Do not finish until it passes.
6. In the MR description list which OpenAPI paths changed and any new error codes.
```

VERIFY: skills were not invoked in a live session during authoring.

## Template: subagents

Fields per the subagents docs (case-sensitive camelCase; only `name` and `description` required; unknown fields ignored): `name`, `description`, `tools`, `disallowedTools`, `model` (`sonnet`, `opus`, `haiku`, `fable`, a full model ID or `inherit`), `permissionMode`, `maxTurns`, `autoCompactWindow`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `omitClaudeMd`, `effort`, `isolation`, `color`, `initialPrompt`, `experimental`. `tools` is an allowlist and `disallowedTools` a denylist applied first. A `Bash(...)` specifier in `disallowedTools` removes Bash entirely; use `permissions.deny` for partial command blocks.

`.claude/agents/security-reviewer.md`:
```markdown
---
name: security-reviewer
description: Read-only security review of the current diff (secrets, injection, authz, unsafe deserialization, prompt-injection paths). Use after code changes and before opening an MR.
tools: Read, Grep, Glob
disallowedTools: Write, Edit, Bash
model: inherit
maxTurns: 20
---

You are a security reviewer for a regulated financial services codebase.

Review the changed files for: committed secrets, missing authorization checks, SQL or command
injection, unsafe deserialization, logging of personal or secret data, and untrusted model or
tool output reaching a privileged action. Report each finding as: file, line, risk, concrete fix.
Do not modify files. If nothing is wrong, say so and list what you checked.
```

`.claude/agents/test-writer.md`:
```markdown
---
name: test-writer
description: Writes failing tests first for a described behavior, using synthetic data and fakes. Use before implementing a feature or bug fix.
tools: Read, Grep, Glob, Edit, Write
model: inherit
maxTurns: 25
---

Write the smallest failing pytest test that captures the requested behavior. Use fakes for the
model client and synthetic data only. Place the test under `tests/unit/` mirroring `src/`.
Do not edit production code and do not weaken or delete existing tests.
```

Frontmatter of both files parses with PyYAML and uses only documented fields. VERIFY: subagent delegation was not exercised in a live session.

## Template: `.mcp.json`

Format per the MCP docs: top-level `mcpServers`; each entry needs `type` (`http`, `stdio`, `sse` deprecated, `ws`); `${VAR}` and `${VAR:-default}` expand in `command`, `args`, `env`, `url` and `headers`. Claude Code asks each developer to approve project servers in interactive sessions (`claude mcp reset-project-choices` resets those choices). The host below is a reserved placeholder name, not a real server.

```json
{
  "mcpServers": {
    "internal-docs": {
      "type": "http",
      "url": "https://mcp.example.invalid/docs",
      "headers": {
        "Authorization": "Bearer ${INTERNAL_DOCS_MCP_TOKEN}"
      }
    }
  }
}
```

Checked: valid JSON, and `claude mcp list` / `claude doctor` parsed the entry; their only complaint was the unset `INTERNAL_DOCS_MCP_TOKEN` variable, which is the intended behavior (the token comes from the developer's environment). The server stays "pending approval" until a developer approves it interactively.

## Organization baseline (managed settings)

The platform team distributes a managed file; developers cannot override it. File locations per the managed-settings docs: macOS `/Library/Application Support/ClaudeCode/managed-settings.json`, Linux and WSL `/etc/claude-code/managed-settings.json`, Windows `C:\Program Files\ClaudeCode\managed-settings.json`; an optional `managed-settings.d/` directory splits ownership across teams; `/status` shows `Enterprise managed settings (file)` when it applies. Other delivery routes (MDM, server-managed) carry the same keys. Merge behavior: permission lists combine across sources, so managed deny rules add to repo deny rules.

Starter baseline (validated against the published schema; not deployed to a machine in authoring, VERIFY: confirm with `/status` after rollout):

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "deny": [
      "Read(.env)",
      "Read(.env.*)",
      "Read(!.env.example)",
      "Bash(terraform apply *)",
      "Bash(terraform destroy *)",
      "Bash(git push --force *)",
      "Bash(git push -f *)"
    ],
    "disableBypassPermissionsMode": "disable"
  },
  "allowManagedMcpServersOnly": true,
  "allowedMcpServers": [
    { "serverName": "internal-docs" }
  ]
}
```

Choices to make deliberately:
- `allowManagedPermissionRulesOnly: true` stops user and project settings from defining allow, ask or deny rules at all. That is stricter and would remove the repo-level allow list in this doc, so it is not in the starter baseline. Use it only if Security wants one central list.
- `allowManagedHooksOnly: true` blocks repo hooks; the hook scripts above would stop working.
- A managed `CLAUDE.md` (same directory as the managed settings file, or the `claudeMd` key) carries behavior guidance for every repo, for example the "never" list. Keep it short.
- The managed `managed-mcp.json` format was not confirmed in this pass; VERIFY: read the managed MCP page before authoring one.

## CI check: `scripts/check_agent_config.py`

Checks the committed agent files: `CLAUDE.md` exists and is within 200 lines, `.claude/settings.json` is strict JSON with no `bypassPermissions` or `auto` default and no over-broad allow rule, required deny rules are present, optional JSON Schema validation (`--schema`), `.mcp.json` entries have a `type`, rule frontmatter parses and has only a `paths` list, skills and subagents have a description, and subagents set `tools`. Tested on 2026-11-25 against the templates above (passes) and against a broken copy (reports an over-broad allow rule, a missing deny rule, an unquoted glob and a subagent without `tools`). Passes `ruff` and `mypy --strict` using the `PyYAML` and `jsonschema` packages (add both, plus `types-pyyaml` and `types-jsonschema`, to the `dev` group). CI fetches the schema from the published URL (follow redirects: `json.schemastore.org` redirects to `www.schemastore.org`; with curl use `-L`) or uses a vendored copy (F4: CI network egress).

```python
#!/usr/bin/env python3
"""Validate committed Claude Code configuration. Exit 1 on any problem.

Usage: scripts/check_agent_config.py [repo-dir] [--schema settings.schema.json]
Needs PyYAML; jsonschema is only needed with --schema.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

MAX_CLAUDE_MD_LINES = 200
MAX_RULE_LINES = 100
REQUIRED_DENY = ("Read(.env)", "Read(.env.*)")
FORBIDDEN_ALLOW = ("Bash", "Bash(*)", "Bash(bash *)", "Bash(sh *)", "Bash(python *)")


def frontmatter(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    _, block, _ = text.split("---\n", 2)
    data = yaml.safe_load(block)
    if not isinstance(data, dict):
        msg = "frontmatter is not a mapping"
        raise ValueError(msg)  # noqa: TRY004
    return data


def check(root: Path, schema: Path | None) -> list[str]:
    errors: list[str] = []
    claude_md = root / "CLAUDE.md"
    if not claude_md.exists():
        errors.append("CLAUDE.md is missing")
    elif len(claude_md.read_text(encoding="utf-8").splitlines()) > MAX_CLAUDE_MD_LINES:
        errors.append(f"CLAUDE.md is longer than {MAX_CLAUDE_MD_LINES} lines")
    settings_path = root / ".claude" / "settings.json"
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [*errors, f"{settings_path}: {exc}"]
    perms = settings.get("permissions", {})
    if perms.get("defaultMode") in {"bypassPermissions", "auto"}:
        errors.append("permissions.defaultMode must not be bypassPermissions or auto")
    errors += [
        f"allow rule too broad: {r}"
        for r in perms.get("allow", [])
        if r in FORBIDDEN_ALLOW
    ]
    errors += [
        f"missing deny rule: {r}"
        for r in REQUIRED_DENY
        if r not in perms.get("deny", [])
    ]
    if schema is not None:
        import jsonschema  # noqa: PLC0415

        validator = jsonschema.Draft7Validator(
            json.loads(schema.read_text(encoding="utf-8"))
        )
        for err in validator.iter_errors(settings):
            errors.append(f"schema: {err.message} at {list(err.path)}")
    mcp = root / ".mcp.json"
    if mcp.exists():
        servers = json.loads(mcp.read_text(encoding="utf-8")).get("mcpServers", {})
        errors += [
            f".mcp.json: {n} has no type"
            for n, srv in servers.items()
            if "type" not in srv
        ]
    for path in sorted((root / ".claude").glob("rules/*.md")):
        if len(path.read_text(encoding="utf-8").splitlines()) > MAX_RULE_LINES:
            errors.append(f"{path}: longer than {MAX_RULE_LINES} lines")
        try:
            fm = frontmatter(path)
        except (yaml.YAMLError, ValueError) as exc:
            errors.append(
                f"{path}: frontmatter does not parse ({exc}); quote every glob"
            )
            continue
        if fm is not None:
            paths = fm.get("paths")
            valid = isinstance(paths, list) and all(isinstance(p, str) for p in paths)
            if set(fm) - {"paths"} or not valid:
                errors.append(
                    f"{path}: frontmatter must be only a 'paths' list of strings"
                )
    skills = sorted((root / ".claude").glob("skills/*/SKILL.md"))
    agents = sorted((root / ".claude").glob("agents/*.md"))
    for path in [*skills, *agents]:
        try:
            fm = frontmatter(path)
        except (yaml.YAMLError, ValueError) as exc:
            errors.append(f"{path}: frontmatter does not parse ({exc})")
            continue
        if not fm or "description" not in fm:
            errors.append(f"{path}: needs frontmatter with a description")
        elif path in agents and "tools" not in fm:
            errors.append(f"{path}: subagent must set an explicit tools allowlist")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--schema", type=Path)
    args = parser.parse_args()
    problems = check(Path(args.root), args.schema)
    for problem in problems:
        print(f"ERROR {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
```

## How these were checked
| Item | Method | Result |
|---|---|---|
| `settings.json` | JSON parse; published schema (Draft 7); `claude doctor`; negative tests | Pass |
| Deny rules | Real Claude Code reads of `.env`, `.env.example`, `secrets/a.txt`, `k.pem`, `notes.txt` (placeholder files, fake content) | Denied, allowed, denied, denied, allowed |
| Edit and write of `.env.example` | Real session with `acceptEdits` | `.env.example` written; `.env` refused by the agent (deny effect not isolated) |
| Hooks | Scripts run with sample stdin, including failure and empty input | Pass |
| Rules, skill, subagents | YAML frontmatter parsed with PyYAML; field names compared with docs | Pass |
| `.mcp.json` | `claude mcp list`, `claude doctor` | Parses; unset env var warning only |
| Managed settings | Schema validation only | VERIFY: deploy and check `/status` |
| Live skill, subagent and hook execution in a session | Not performed | VERIFY |
| `AGENTS.md` import (`@AGENTS.md`) | Docs only | VERIFY: run `/context all` and confirm `CLAUDE.md` memory content |

## Checklist
- [ ] `CLAUDE.md` is committed, under 200 lines, commands match the Makefile, and has no secrets.
- [ ] If `AGENTS.md` exists, `CLAUDE.md` starts with `@AGENTS.md`.
- [ ] Path-scoped rules have quoted `paths:` globs; each rule file is short and single-topic.
- [ ] `.claude/settings.json` has `$schema`, specific allow rules, the standard deny and ask lists, and validates.
- [ ] No `bypassPermissions` or `auto` default; managed settings disable bypass mode.
- [ ] Hook scripts are in `.claude/hooks/`, executable, fail closed and were tested.
- [ ] Skills with side effects set `disable-model-invocation: true`; subagents set `tools`.
- [ ] `.mcp.json` lists approved servers only, with `type` and no credentials.
- [ ] `.claude/settings.local.json` and `CLAUDE.local.md` are gitignored.
- [ ] `claude doctor` shows no "Invalid settings"; `scripts/check_agent_config.py` passes in CI.
- [ ] CODEOWNERS covers `.claude/`, `.mcp.json` and `CLAUDE.md`.

## Common AI failure modes
| Failure | What to do instead |
|---|---|
| Writes a 600-line `CLAUDE.md` that copies the standards | Keep under 200 lines; link; move detail into path-scoped rules |
| Uses `//` comments or trailing commas in `settings.json` | Strict JSON only; run `claude doctor` |
| Invents a setting, hook event or frontmatter field | Check the doc lists above; unknown fields are silently ignored |
| Writes `paths: **/*.py` without quotes | Quote globs; the rule otherwise loads for every file |
| Allows `Bash(*)` or `Bash(python *)` "to avoid prompts" | Allow exact `make` targets and `uv run --locked` tools |
| Believes `Read(.env)` deny makes secrets safe | It does not stop `cat .env` through a shell; keep secrets out of the checkout |
| Adds `--dangerously-skip-permissions` to a CI job or script | Never; use narrow allow rules and a sandbox |
| Puts a token in `.mcp.json` or `settings.json` `env` | `${VAR}` in `.mcp.json`; secrets via the identity and vault |
| Symlinks `CLAUDE.md` to `AGENTS.md`, or writes "see AGENTS.md" | `@AGENTS.md` import as the first line |
| Edits `.claude/settings.json` to remove a deny that blocks its task | Stop and ask a human; do not widen your own permissions |
| Commits `.claude/settings.local.json` | It is gitignored; check with `git check-ignore` |

## Related docs
- [07-ignore-files.md](./07-ignore-files.md): ignoring personal agent files
- [09-structure-and-format.md](./09-structure-and-format.md): repo layout, CODEOWNERS
- [00-tech-stack.md](./00-tech-stack.md): Makefile targets the template references
- [06-secrets-and-env.md](./06-secrets-and-env.md): secrets and `.env`
- [02-security.md](./02-security.md): MCP vetting, agent identity, least privilege
- [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md): tool and agent manifests
- [01-codebase-practices.md](./01-codebase-practices.md): rules for coding agents, MR flow
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md): what may enter prompts
- [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md): waivers
