@AGENTS.md

<!-- Implements AGT-001 (committed, <= 200 lines), AGT-006 (@AGENTS.md first line, Claude-specific
content only below), AGT-004 (no restated standards). VERIFY: run /context and confirm the
AGENTS.md content loads (doc 08 checked this against the docs only). ASSUMPTION: (F16) Claude Code
is approved developer tooling; do not use it on repos holding restricted data until confirmed. -->

## Claude Code specifics

- Rules are in `.claude/rules/`. Always loaded: `python-style.md`, `security.md`, `clean-code.md`. Path-scoped: `api-contracts.md`, `architecture.md`, `domain-code.md`, `observability.md`, `testing.md`. They cite rule IDs; keep them short and one topic each, and add rules that are only enforced by review.
- Permissions and hooks are in `.claude/settings.json`. Deny rules are guardrails, not a security boundary; CI is the control.
- After editing any file under `.claude/`, run `claude doctor` and confirm there is no "Invalid settings" section, then `/status`.
- Do not widen your own permissions or edit `.claude/settings.json` to unblock a task; ask a human.

## GitLab Duo

- Duo reads `AGENTS.md` (Chat and flows, not Code Review Flow). `.gitlab/duo/chat-rules.md` and `.gitlab/duo/mr-review-instructions.yaml` are generated from the same rule selection as `.claude/rules/`; never edit them by hand (AGT-004).
