# Python style (always loaded)

- Run `make fmt` after edits and `make check` before declaring work done.
- Type every function; `mypy --strict` must pass. A `# type: ignore[code]` needs a reason comment.
- Keep functions small and named for the domain (`approve_claim`, not `process`).
- No `print`, no bare `except`, no mutable default arguments.
- Raise typed domain errors from `domain/errors.py`; never return error strings.

<!-- Implements AGT-010 (one topic, <= 100 lines), AGT-011 (no frontmatter: always loaded), STR-016, STR-022, OBS-001. -->
