@AGENTS.md

<!-- Implements AGT-001 (committed, <= 200 lines), AGT-006 (@AGENTS.md first line, Claude-specific
content only below), AGT-004 (no restated standards). VERIFY: run /context and confirm the
AGENTS.md content loads (doc 08 checked this against the docs only). ASSUMPTION: (F16) Claude Code
is approved developer tooling; do not use it on repos holding restricted data until confirmed. -->

## Claude Code specifics

- Path-scoped rules are in `.claude/rules/` (`python-style.md` always loads; `testing.md` loads for `tests/**` and `evals/**`).
- Permissions and hooks are in `.claude/settings.json`. Deny rules are guardrails, not a security boundary; CI is the control.
- After editing any file under `.claude/`, run `claude doctor` and confirm there is no "Invalid settings" section, then `/status`.
- Do not widen your own permissions or edit `.claude/settings.json` to unblock a task; ask a human.
