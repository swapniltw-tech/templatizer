# Clean Code

> **Owner:** Engineering Quality lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** docs.astral.sh/ruff (rules, settings); mypy.readthedocs.io (config file, strict mode); radon docs (cross-check tool only). Rule codes and config keys below were confirmed by running Ruff and mypy on a toy package (see "Tested with").

## Purpose
This doc defines what clean code means for output that is mostly written by AI agents: small, typed, boring code with no dead weight. It owns **quality lint rules and complexity limits**, the **comments policy**, error-handling style, and the **AI-slop anti-pattern checklist**. Formatting, line length, naming of files, and the baseline mypy and Ruff format settings are owned by [09-structure-and-format.md](./09-structure-and-format.md). Layering is owned by [03-architecture.md](./03-architecture.md). Simplicity principles are owned by [04-engineering-principles.md](./04-engineering-principles.md). Logging style is owned by [10-logging-observability.md](./10-logging-observability.md).

Limits are enforced by tools wherever a rule code exists; the rest are review rules. A limit is a trigger to refactor, not a target to reach.

## Limits at a glance

| Measure | Limit | Ruff rule | Config key (`[tool.ruff.lint...]`) |
|---|---|---|---|
| Cyclomatic complexity per function | 10 | `C901` | `mccabe.max-complexity` |
| Arguments per function | 5 | `PLR0913` | `pylint.max-args` |
| Positional arguments per function | 3 | `PLR0917` | `pylint.max-positional-args` |
| Branches per function | 12 | `PLR0912` | `pylint.max-branches` |
| Return statements per function | 6 | `PLR0911` | `pylint.max-returns` |
| Statements per function | 50 | `PLR0915` | `pylint.max-statements` |
| Magic values in comparisons | none | `PLR2004` | n/a |

Review-only targets: functions SHOULD stay under about 20 lines of logic; modules SHOULD stay under about 400 lines; nesting SHOULD stay at three levels or fewer. VERIFY: Ruff's nested-blocks rule (`PLR1702`), `PLR0914` (locals) and `PLR0916` (boolean expressions) are preview rules (Ruff reported "no effect because preview is not enabled"), so they are not part of the standard set.

## Rules

### Functions and structure
- **CLN-001** [MUST] [lint: ruff C901] Cyclomatic complexity per function MUST NOT exceed 10; a function above the limit MUST be split, not given a `# noqa`.
- **CLN-002** [MUST] [lint: ruff PLR0911,PLR0912,PLR0915] A function MUST NOT exceed 6 returns, 12 branches or 50 statements.
- **CLN-003** [MUST] [lint: ruff PLR0913,PLR0917] A function MUST NOT take more than 5 arguments or 3 positional arguments; related values MUST be grouped in a frozen dataclass or model, and the rest MUST be keyword-only.
- **CLN-004** [MUST] [lint: ruff FBT] Boolean flags MUST be keyword-only; a boolean argument that switches behavior SHOULD become two functions.
- **CLN-005** [SHOULD] [review] A function SHOULD do one thing, read top to bottom, and use early returns and guard clauses instead of nesting beyond three levels.
- **CLN-006** [MUST] [lint: ruff PLR2004] Magic numbers and strings in comparisons MUST be named constants or enums with a domain name (for example `MAX_CLAIM_ATTACHMENTS`).
- **CLN-007** [SHOULD] [review] Modules SHOULD stay under about 400 lines and classes SHOULD have a single responsibility; a file named `utils`, `helpers`, `misc` or `common_stuff` MUST NOT hold business logic ([03-architecture.md](./03-architecture.md) limits `common/`).
- **CLN-008** [SHOULD] [review] Domain values SHOULD be immutable (frozen dataclasses or frozen models); module-level mutable state MUST NOT be used, and `global` MUST NOT appear (`PLW0603` is in the selected `PL` set).
- **CLN-009** [SHOULD] [lint: ruff PERF] Simple accumulation loops SHOULD be comprehensions or built-ins (`PERF401` and related rules).

### Naming and typing
- **CLN-010** [MUST] [review] Names MUST state intent in domain language (`PremiumQuote`, `is_eligible_for_waiver`), functions MUST be verbs or questions, and the same concept MUST have the same name everywhere.
- **CLN-011** [MUST] [lint: ruff A001,A002,N] Code MUST NOT shadow built-ins (`id`, `type`, `input`, `list`) and MUST follow PEP 8 naming (pep8-naming, `N` rules).
- **CLN-012** [MUST] [ci: mypy] All code MUST pass `mypy --strict` with the repo config; baseline settings are owned by [09-structure-and-format.md](./09-structure-and-format.md). `warn_unreachable` and the error codes `ignore-without-code`, `redundant-expr` and `truthy-bool` SHOULD be enabled (tested).
- **CLN-013** [MUST] [lint: ruff ANN401] `Any` MUST NOT appear in public signatures; use a Protocol, `TypedDict`, a generic or a concrete model.
- **CLN-014** [MUST] [ci: mypy] `# type: ignore` MUST name the error code and carry a one-line reason; `typing.cast` MUST NOT be used to silence a mismatch that a real fix would remove.
- **CLN-015** [MUST] [lint: ruff UP] Code MUST use modern syntax for the target Python (`list[str]`, `X | None`, `match` where it clarifies); target version follows [00-tech-stack.md](./00-tech-stack.md).

### Error handling
- **CLN-016** [MUST] [lint: ruff E722,BLE001] Code MUST NOT use bare `except:` or `except Exception:` except at a process boundary that logs and re-raises or converts to a defined error response.
- **CLN-017** [MUST] [lint: ruff S110,SIM105] Exceptions MUST NOT be swallowed (`try`/`except`/`pass`); handle, translate or let them propagate.
- **CLN-018** [MUST] [lint: ruff B904] A translated exception MUST be raised with `raise NewError(...) from err` (or `from None` with a reason).
- **CLN-019** [MUST] [review] Failure MUST be signalled by raising a specific domain exception (defined in `domain/errors.py` or `application`); functions MUST NOT return `None`, `-1`, empty strings or `False` to mean "something went wrong".
- **CLN-020** [MUST] [lint: ruff S101] `assert` MUST NOT be used in `src/` for input or business validation (tests excepted); validate explicitly and raise.
- **CLN-021** [MUST] [lint: ruff B006] Mutable default arguments MUST NOT be used.
- **CLN-022** [MUST] [lint: ruff DTZ] Datetimes MUST be timezone-aware and obtained from an injected clock, not `datetime.now()` or `utcnow()` in logic (a `TID251` ban entry on `datetime.datetime.utcnow` is in the reference config).

### Dead code and noise
- **CLN-023** [MUST] [lint: ruff F401,F841,ARG] Unused imports, variables, arguments and private functions MUST be removed, not commented out or silenced.
- **CLN-024** [MUST] [lint: ruff ERA001] Commented-out code MUST NOT be committed; version control is the history.
- **CLN-025** [MUST] [lint: ruff T201] `print` MUST NOT be used in `src/`; use the structured logger ([10-logging-observability.md](./10-logging-observability.md)).
- **CLN-026** [MUST] [lint: ruff RUF100] A `# noqa` MUST name its rule code, carry a reason, and MUST still be needed (unused `noqa` is an error with `RUF100`).

### Comments and docstrings
- **CLN-027** [MUST] [review] Comments MUST explain why (a constraint, a business rule source, a non-obvious trade-off), never what the next line does; a comment that restates code MUST be deleted and the code renamed if it was unclear.
- **CLN-028** [MUST] [review] Comments MUST NOT contain narration of the edit (`# added`, `# now handles X`, `# fixed`), author or date stamps, ticket history, emoji, banners, or statements that the code was AI-generated; history belongs in version control.
- **CLN-029** [MUST] [lint: ruff FIX002] `TODO`, `FIXME` and `XXX` comments MUST NOT be merged (`FIX002` flags every one); open a ticket instead. `TD002` and `TD003` (author and issue link) are in the selected set for any suppressed case.
- **CLN-030** [SHOULD] [review] Public functions and classes SHOULD have a one-line docstring stating purpose and non-obvious behavior (units, side effects, raised errors); docstrings MUST NOT repeat parameter types that the annotations already give.
- **CLN-031** [MUST] [review] A regulatory or business-rule comment MUST cite the rule source by identifier or document name so a reviewer can check it; MUST NOT invent a citation.

### Governing the lint config
- **CLN-032** [MUST] [review] Lint, type and complexity configuration (`[tool.ruff*]`, `[tool.mypy]`) MUST NOT be loosened to make code pass; changes require human approval via `CODEOWNERS`, and agents MUST NOT edit them for that purpose.
- **CLN-033** [MUST] [review] A per-file ignore or `noqa` for a rule in the limits table MUST have a waiver reference ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)).
- **CLN-034** [MUST] [ci: make lint] `make lint` MUST run `ruff check` and `make typecheck` MUST run `mypy`; CI MUST fail on any finding, with no baseline file that hides existing violations.
- **CLN-035** [MAY] [manual: radon] radon (`radon cc -s -n C src`) MAY be run as a cross-check on complexity, but Ruff `C901` is the gate. VERIFY: radon's thresholds and maintenance status before adopting it in CI.

### AI-slop review
- **CLN-036** [MUST] [review] Reviewers MUST check every AI-authored MR against the anti-pattern table below, and the author MUST remove findings before review.
- **CLN-037** [MUST] [review] Imports, function names and library calls MUST exist in the pinned dependency versions; unresolved or invented APIs are failures of `mypy` or tests and MUST NOT be "fixed" by adding `# type: ignore` or `Any` ([20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md) covers hallucinated packages).
- **CLN-038** [MUST] [review] The diff MUST be limited to the task: no drive-by reformatting, renames, new files or dependencies unrelated to the request.

## AI-slop anti-pattern checklist

| Anti-pattern | Why it is a problem | Detected by |
|---|---|---|
| Comment above each line restating it ("increment counter") | Noise that goes stale | review (CLN-027) |
| Narrating comments ("Added new helper", "now handles X") | Changelog in code | review (CLN-028) |
| `try/except Exception: pass` or `return None` on error | Hides failures | Ruff `BLE001`, `S110`, `SIM105` |
| Blanket `except Exception` that logs and continues in business logic | Corrupt state | Ruff `BLE001` |
| Defensive checks for impossible states, duplicate validation at every layer | Obscures real rules | review |
| Wrappers that only call another function; single-use base classes and factories | Speculative abstraction | review ([04-engineering-principles.md](./04-engineering-principles.md)) |
| Unused parameters, config flags, fallback branches | Dead code | Ruff `ARG`, `F841` |
| Commented-out alternatives | Dead code | Ruff `ERA001` |
| Magic numbers, repeated string literals | Hidden rules | Ruff `PLR2004` |
| `Any`, `dict[str, Any]` passed through layers | Types lost | Ruff `ANN401`, mypy strict, review |
| `# type: ignore` and `# noqa` sprinkled to silence tools | Hides defects | mypy `ignore-without-code`, Ruff `RUF100`, review |
| Long functions doing parse, call, map and format together | Untestable | Ruff `C901`, `PLR0915` |
| Many boolean or optional parameters | Hard to call correctly | Ruff `FBT`, `PLR0913`, `PLR0917` |
| `print` debugging left in | Leaks data, bypasses logging | Ruff `T201` |
| Invented library functions or old API versions | Runtime failure | mypy, tests, review (CLN-037) |
| Re-implementing standard library or an existing util | Duplication | review |
| Over-broad `utils.py` | Becomes a dumping ground | review (CLN-007) |
| Tests that mirror the implementation | Prove nothing | [24-testing-standards.md](./24-testing-standards.md) |
| Hard-coded example values, names or emails left in code | Data leakage, wrong behavior | review, secret scanning |
| Edits to lint config, tests or fixtures to get green | Weakens gates | review (CLN-032) |

## Reference configuration
Tested with: Python 3.14, Ruff 0.17, mypy 2.4 on a toy package (all files passed `ruff check`, `ruff format --check`, and `mypy`; negative samples triggered `PLR0913`, `PLR0917`, `PLR2004`, `ERA001`, `T201`, `TID251`, `DTZ003`, `SIM105`, `S110`, `BLE001`, `C901`, `SIM114`, `FIX002`, `TD002`, `TD003`; mypy flagged `no-untyped-def` and `unused-ignore`). This is a "tested with" record, not a pin; versions live in [00-tech-stack.md](./00-tech-stack.md). The type-checking-block rules (`TC`) were deliberately left out because they move imports under `if TYPE_CHECKING:`, which breaks runtime use by Pydantic and weakens the import-boundary tests in [03-architecture.md](./03-architecture.md). VERIFY: if the service uses Pydantic, evaluate the Pydantic mypy plugin per its docs.

```toml
[tool.mypy]
strict = true
python_version = "3.14"
mypy_path = "src"
files = ["src", "tests"]
explicit_package_bases = true
exclude = ["^mutants/"]
warn_unreachable = true
enable_error_code = ["ignore-without-code", "redundant-expr", "truthy-bool"]

[tool.ruff]
line-length = 100
extend-exclude = ["mutants"]
target-version = "py314"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
  "E", "W", "F", "I", "N", "UP", "B", "A", "C4", "C90", "SIM", "RET", "ARG", "PTH",
  "PL", "PERF", "RUF", "S", "T20", "ERA", "PT", "DTZ", "FBT", "BLE", "TRY", "ANN", "TID",
  "G", "LOG", "TD", "FIX",
]
ignore = ["TRY003"]

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.pylint]
max-args = 5
max-positional-args = 3
max-branches = 12
max-returns = 6
max-statements = 50

[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "all"

[tool.ruff.lint.flake8-tidy-imports.banned-api]
"datetime.datetime.utcnow".msg = "Use an injected clock returning timezone-aware datetimes."

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "PLR2004", "ARG", "FBT"]
```
Notes:
- Tests are type-checked under the same strict mypy settings and keep the `ANN` rules; a test function is annotated `-> None`.
- `TRY003` is ignored because it conflicts with descriptive domain error messages; the choice is a proposal for the engineering leads.
- `ban-relative-imports = "all"` is a style choice (absolute imports only); it is owned here only as lint config, project layout is owned by 09.
- `mutants/` (mutmut output) is excluded from Ruff and mypy ([24-testing-standards.md](./24-testing-standards.md)).
- Run `ruff format` for formatting; this doc sets no formatter options.

### Before and after
Illustrative only (not run); `Policy`, `price` and `IneligibleHolderError` are placeholders.

```python
# Slop: swallowed error, flag argument, magic number, narrating comment
def apply(p, retry=True, strict=False):  # applies the policy
    try:
        if p.age > 65:  # check if age is greater than 65
            return None
        ...
    except Exception:
        pass

# Clean: typed, specific, raises on failure
MAX_ELIGIBLE_AGE = 65


def apply_policy(policy: Policy, *, now: datetime) -> Quote:
    if policy.holder_age(now) > MAX_ELIGIBLE_AGE:
        raise IneligibleHolderError(policy.id)
    return price(policy)
```

## Checklist
- [ ] `make lint` and `make typecheck` pass with no new `noqa` or `type: ignore` (CLN-014, CLN-026).
- [ ] No function exceeds the limits in the table; none needed a suppression (CLN-001, CLN-002, CLN-003).
- [ ] No bare or blind `except`, swallowed errors or sentinel returns (CLN-016, CLN-017, CLN-019).
- [ ] No dead code, commented-out code, `print` or merged TODOs (CLN-023, CLN-024, CLN-025, CLN-029).
- [ ] Comments explain why only, carry no narration, authorship or tool markers (CLN-027, CLN-028).
- [ ] Names use domain language; constants replace magic values (CLN-006, CLN-010).
- [ ] No `Any` in public signatures; types are specific (CLN-013).
- [ ] Lint and type config was not loosened (CLN-032).
- [ ] The diff stays inside the task (CLN-038).
- [ ] The AI-slop table was applied to the diff (CLN-036).

## Common AI failure modes
- Writes a comment for every line, or narrates its own edit in a comment.
- Wraps logic in `try/except Exception` and returns a default.
- Adds `# noqa`, `# type: ignore` or `Any` to silence a tool instead of fixing the cause.
- Raises the complexity limit or edits `pyproject.toml` lint settings to get green.
- Adds parameters, flags and helper layers "for flexibility".
- Leaves commented-out alternatives or `print` debugging.
- Invents a library function or uses an API from an older version.
- Uses vague names (`data`, `result`, `handler`, `process`) and mixes terms for one concept.
- Fixes unrelated style in the same MR, hiding the real change.

## Related docs
- [09-structure-and-format.md](./09-structure-and-format.md): formatter, line length, baseline typing, repo layout.
- [03-architecture.md](./03-architecture.md): layering and fitness tests.
- [04-engineering-principles.md](./04-engineering-principles.md): simplicity and YAGNI.
- [24-testing-standards.md](./24-testing-standards.md): tests that accompany clean code.
- [10-logging-observability.md](./10-logging-observability.md): logging instead of `print`.
- [01-codebase-practices.md](./01-codebase-practices.md): MR and review practice.
- [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md): waivers for lint suppression.
