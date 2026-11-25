# Testing Standards

> **Owner:** Engineering Quality lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** docs.pytest.org (customize, reference); hypothesis.readthedocs.io (settings reference); coverage.readthedocs.io (config); github.com/boxed/mutmut (README); import-linter and pytest-archon project docs; docs.gitlab.com (code coverage visualization). Config in this doc was run on a toy package (see "Tested with").

## Purpose
Testing is the most important practice in this standard set. Most of our code is AI-generated, so tests are the only reliable proof that code does what the spec says. This doc owns: the test pyramid, test layout, determinism, coverage and mutation floors, how to test LLM-dependent code, test data, flaky-test policy, the rules AI agents follow when writing or changing tests, and CI gating of tests.

It does not own: evals for non-deterministic behavior (see [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md)), architecture fitness-test design ([03-architecture.md](./03-architecture.md)), API contract design ([17-api-and-contracts.md](./17-api-and-contracts.md)), or pipeline definition ([16-cicd-and-deployment.md](./16-cicd-and-deployment.md)).

## Test levels

| Level | Location | Dependencies | Runs in | Marker | Gate |
|---|---|---|---|---|---|
| Unit | `tests/unit/` (mirrors `src/<package>/`) | None. Fakes for ports. No network, no real clock | `make test-unit`, every MR | none | blocking |
| Architecture (fitness) | `tests/unit/architecture/` | Imports only | `make test-unit` | none | blocking |
| Integration | `tests/integration/` | Real dependencies via containers or emulators | `make test-integration`, every MR | `integration` | blocking |
| Contract | `tests/contract/` | Spec files, schemas, recorded provider examples | `make test-integration` (ASSUMPTION: no separate target in the standard Makefile list) | `contract` | blocking |
| End-to-end | `tests/e2e/` | Deployed non-production environment | scheduled and post-deploy job | `e2e` | blocking for release, not for MR |
| Property-based | beside unit tests, Hypothesis | None | `make test-unit` | none | blocking |
| Mutation | domain logic only | None | scheduled and MR-on-domain CI job | n/a | floor, see TST-021 |
| Live-model | `tests/unit/` or `tests/e2e/` | A real Foundry deployment | scheduled job only | `live_llm` | budgeted, advisory then blocking per rung |

Shape: many fast unit tests, fewer integration tests, very few e2e tests. A test belongs at the lowest level that can prove the behavior.

## Rules

### Process and layout
- **TST-001** [MUST] [ci: make check] Every repo MUST provide `make test`, `make test-unit` and `make test-integration`, and `make check` MUST run the tests; CI MUST run the same targets.
- **TST-002** [MUST] [review] Every change that alters behavior MUST include a test that fails without the change; only docs-only or config-only MRs may omit tests.
- **TST-003** [MUST] [review] Developers and AI agents MUST write the failing test first, run it, confirm it fails for the expected reason, then write the code; the MR description MUST record the failing run.
- **TST-004** [MUST] [review] Test files under `tests/unit/` MUST mirror the `src/<package>/` tree (`src/pkg/domain/services/pricing.py` is tested in `tests/unit/domain/services/test_pricing.py`).
- **TST-005** [MUST] [ci: pytest] Markers MUST be registered and unknown markers MUST fail the run (pytest `strict`, see the reference config).
- **TST-006** [SHOULD] [review] Test names SHOULD state behavior, for example `test_quote_rejects_negative_premium`, not `test_quote_1`; each test SHOULD assert one behavior.
- **TST-007** [SHOULD] [review] The unit suite SHOULD finish in under 5 minutes on CI. ASSUMPTION: threshold to be confirmed by the platform team.

### Determinism
- **TST-008** [MUST] [ci: pytest-socket] Unit tests MUST NOT use the network; the unit run MUST use `--disable-socket`, and only tests marked `enable_socket` and `integration` MAY open sockets.
- **TST-009** [MUST] [review] Code under test MUST receive time, randomness and identifiers through injected parameters or ports (a `Clock` Protocol, a seeded `random.Random`, an ID factory); tests MUST NOT call `sleep` to wait for time to pass.
- **TST-010** [MUST] [ci: pytest-randomly] Tests MUST pass in random order; CI MUST run with `pytest-randomly` and print the seed so failures reproduce.
- **TST-011** [MUST] [ci: pytest] Warnings MUST fail tests (`filterwarnings = ["error"]`); an ignored warning MUST name the exact warning and carry a comment with a ticket.
- **TST-012** [MUST] [ci: pytest-timeout] Every test MUST run under a per-test timeout (reference config uses 30 seconds).
- **TST-013** [MUST] [review] Tests MUST NOT read real environment variables, home directories or the working directory for state; they MUST use `tmp_path` and `monkeypatch`.

### Integration, contract and end-to-end
- **TST-014** [MUST] [review] Integration tests MUST use real dependencies (containers or vendor emulators) for databases, queues and storage, and MUST NOT mock the adapter they claim to test.
- **TST-015** [SHOULD] [review] Where no faithful emulator exists (for example Key Vault), tests SHOULD put a fake behind the port and add a contract test that pins the adapter's assumptions. VERIFY: current Azure emulator coverage (for example Azurite for storage) before naming one in a service.
- **TST-016** [MUST] [review] Integration tests MUST create uniquely named resources, clean up after themselves and be safe to run in parallel.
- **TST-017** [MUST] [test: tests/contract] Every HTTP endpoint and event schema MUST have contract tests that validate real responses and payloads against the published spec; spec rules live in [17-api-and-contracts.md](./17-api-and-contracts.md).
- **TST-018** [MUST] [test: tests/contract] Every AI tool MUST have a contract test that validates its inputs and outputs against its registry manifest schema ([25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md)).
- **TST-019** [SHOULD] [ci] End-to-end tests SHOULD cover only the few critical user journeys, run against a deployed non-production environment with synthetic data, and run after deploy, not inside `make check`.

### Property-based and mutation testing
- **TST-020** [MUST] [test: hypothesis] Pure domain logic that computes money, dates, eligibility or rules MUST have Hypothesis property tests for its invariants (bounds, monotonicity, idempotence, round trips); other pure functions SHOULD.
- **TST-021** [MUST] [ci: mutmut] Tier A deterministic domain logic (`domain/rules`, `domain/services`) MUST be mutation tested with mutmut, and the mutation score MUST meet the floor in the tier table; the CI job MUST fail below the floor using the gate script in this doc, because mutmut has no built-in threshold.
- **TST-022** [MUST] [review] Surviving mutants MUST be killed by a new test or marked `# pragma: no mutate` with a one-line reason; blanket `do_not_mutate` patterns MUST NOT be used to raise the score.
- **TST-023** [MUST] [review] Mutation testing MUST NOT target adapters, prompt code or LLM-dependent code; those are covered by TST-029 to TST-034 and by evals.
- **TST-024** [MUST] [ci: hypothesis] Property tests MUST run under a derandomized `gate` profile in CI, and every failure Hypothesis finds MUST be committed as an `@example` regression case.

### Coverage
- **TST-025** [MUST] [ci: pytest-cov] Coverage MUST be measured with `branch = true` and gated by `fail_under` per the service tier table; coverage.py reports one combined line-plus-branch total, so the floor applies to that total.
- **TST-026** [MUST] [ci] Coverage floors MUST only ratchet upward; lowering a floor requires a waiver ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)).
- **TST-027** [SHOULD] [ci: coverage] Tier A services SHOULD also gate `domain/` at a higher floor with `coverage report --include='src/*/domain/*' --fail-under=<n>`.
- **TST-028** [MUST] [review] Tests MUST NOT game metrics: no assertion-free tests, no `# pragma: no cover` without a reason on the same line, no tests that only execute code.

### Testing LLM-dependent code
- **TST-029** [MUST] [test: tests/unit] Unit tests MUST use a fake model client that implements the same port as the real client; unit tests MUST NOT call a live model or any network.
- **TST-030** [MUST] [test: tests/unit] Every code path that consumes model output MUST parse it through schema validation, and tests MUST cover malformed JSON, missing fields, wrong types, empty output, refusal, truncation, timeout and quota (429) responses.
- **TST-031** [SHOULD] [review] Recorded-response replay MAY be used for integration-level tests; cassettes MUST be synthetic, committed, keyed by prompt text or hash, and re-recorded only deliberately in a reviewed MR. ASSUMPTION: no replay library is mandated; a small in-repo replay client is acceptable.
- **TST-032** [MUST] [ci: pytest] Live-model tests MUST carry the `live_llm` marker, MUST be excluded from default runs, MUST run only in a scheduled job against a non-production deployment (`<chat-deployment>`), and MUST have a per-run call and token budget enforced by the test harness.
- **TST-033** [MUST] [review] Tests MUST NOT assert exact free-text model output; they MUST assert schema validity, invariants and routing decisions. Output quality is measured by evals in [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md).
- **TST-034** [MUST] [test: tests/unit] Prompt loading MUST be tested: a prompt file whose hash differs from its pinned hash MUST be rejected ([15-llm-and-model-governance.md](./15-llm-and-model-governance.md) owns the prompt rules).
- **TST-035** [MUST] [test: tests/unit] Agent tool-call loops MUST be tested with scripted fake replies, including a tool call outside the allow-list, an invalid argument, a tool error and a loop that exceeds its step limit.

### Test data
- **TST-036** [MUST] [review] Test data MUST be synthetic; production extracts, real customer data and real-looking identifiers MUST NOT appear in tests, fixtures, cassettes or snapshots ([13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)).
- **TST-037** [SHOULD] [review] Tests SHOULD build data with small factories or builders with explicit overrides, not large shared JSON fixtures; names, policy numbers and addresses SHOULD be obviously fake.
- **TST-038** [MUST] [review] Snapshot or golden files MUST be small, human-reviewed in the MR, and regenerated only by an explicit, named command, never automatically in CI.

### Flaky tests
- **TST-039** [MUST] [ci] A test that fails and then passes on retry is a defect; gating jobs MUST NOT use automatic rerun plugins.
- **TST-040** [MUST] [review] A flaky test MUST be quarantined (marked with a reason and ticket) within one business day and fixed or deleted within 14 days. ASSUMPTION: the 14-day window; confirm with the Engineering Quality lead.
- **TST-041** [MUST] [ci: pytest] `skip` and `xfail` MUST include a reason and a ticket reference, and `xfail` MUST be strict so an unexpectedly passing test fails the run.

### Rules for AI coding agents
- **TST-042** [MUST] [review] An agent MUST NOT delete, skip, `xfail`, weaken or loosen a test, widen a tolerance, replace a specific assertion with a looser one, or regenerate a golden file in order to make a failing test pass; it MUST fix the code, or stop and report that the test appears wrong.
- **TST-043** [MUST] [review] An agent that believes a test is wrong MUST NOT edit it itself; it MUST say so in the MR description and request human approval of the test change.
- **TST-044** [MUST] [review] Agents MUST NOT mock the unit under test, assert only that a mock was called when behavior can be observed, or write a test that cannot fail; each new test SHOULD be shown to fail once against a deliberately broken implementation.
- **TST-045** [SHOULD] [ci] CI SHOULD flag any MR that reduces the number of collected tests or the coverage total, and a human reviewer MUST explain the reduction. ASSUMPTION: this is a custom job (`pytest --collect-only -q` compared with the target branch); the platform team owns it.

### Security and performance smoke tests
- **TST-046** [MUST] [test: tests/unit] Every endpoint and tool that enforces authorization MUST have a negative test proving that an unauthorized or wrong-tenant caller is denied ([02-security.md](./02-security.md) owns the security rules).
- **TST-047** [SHOULD] [ci] Critical endpoints SHOULD have a performance smoke test with a latency budget, run on a schedule, not in the MR pipeline ([18-reliability-and-operations.md](./18-reliability-and-operations.md) owns SLOs). VERIFY: choose a load tool with the platform team.

### CI gating
- **TST-048** [MUST] [ci: gitlab] The MR pipeline MUST run the unit and integration jobs with `allow_failure: false`, and the merge MUST be blocked when either fails.
- **TST-049** [MUST] [ci: gitlab] Test jobs MUST publish a JUnit report and a Cobertura coverage report as GitLab artifacts so results are visible on the MR.
- **TST-050** [MUST] [ci: gitlab] A scheduled pipeline MUST run mutation, `live_llm`, e2e and performance smoke jobs, and its failures MUST create a tracked issue.

## Service tiers and floors
ASSUMPTION: tier definitions and numbers below are proposals; confirm with Engineering Quality and AI governance (tiers should align with the risk tiering in [12-governance-and-compliance.md](./12-governance-and-compliance.md)).

| Tier | Typical service | Combined line+branch floor (`fail_under`) | `domain/` floor | Mutation score floor (domain logic) |
|---|---|---|---|---|
| A: affects money, coverage, claims, eligibility, or regulated records | pricing, claims decisioning, policy admin | 90 | 95 | 80 |
| B: customer-facing, no financial decision | portals, notifications, document services | 85 | 90 | optional |
| C: internal tooling, low impact | internal utilities, reports | 80 | n/a | not required |

Ratchet: each quarter, and whenever actual coverage is more than 5 points above the floor, raise `fail_under` to the current value rounded down to the nearest 5.

## Reference configuration
Tested with: Python 3.14 (mutmut also on 3.15.2), pytest 9.2, pytest-cov 7.1, coverage 7.17, Hypothesis 6.170, mutmut 3.8.1, pytest-socket 0.8.1, pytest-randomly 5.1, pytest-timeout 2.4, mypy 2.4, Ruff 0.17. These are a "tested with" record, not a pin; pins live in [00-tech-stack.md](./00-tech-stack.md). Lint and type config are owned by [11-clean-code.md](./11-clean-code.md) and [09-structure-and-format.md](./09-structure-and-format.md).

```toml
[tool.pytest]                       # native TOML table needs pytest >= 9.0
minversion = "9.0"
strict = true                       # VERIFY: exact option set covered by `strict`; unknown markers did fail in the test run
testpaths = ["tests"]
addopts = ["-ra", "--import-mode=importlib", "--disable-socket", "-m", "not live_llm and not e2e"]
timeout = "30"                      # native table expects a string for this option
filterwarnings = ["error"]
markers = [
  "integration: needs real dependencies (containers or emulators)",
  "contract: consumer or provider contract test",
  "e2e: end-to-end test against a deployed environment",
  "live_llm: calls a real model deployment; budgeted, never in make check",
  "slow: takes more than one second",
]

[tool.coverage.run]
source = ["svc"]                    # your package name
branch = true
relative_files = true
omit = ["mutants/*"]

[tool.coverage.report]
fail_under = 90                     # tier floor; one combined line+branch total
show_missing = true
exclude_also = ["if TYPE_CHECKING:", "raise NotImplementedError", "@overload"]

[tool.mutmut]
source_paths = ["src/svc/domain"]
pytest_add_cli_args_test_selection = ["tests/unit/domain"]
pytest_add_cli_args = ["--no-cov", "-p", "no:randomly"]
```

Notes from the test run:
- `--disable-socket` also blocks loopback. Integration tests opt in with `@pytest.mark.enable_socket` (verified). A blocked call surfaced as a `UserWarning` that `filterwarnings = error` turned into a failure; treat any socket error in a unit test as "this test touched the network".
- `-m "not live_llm and not e2e"` in `addopts` deselects live tests by default; a later `-m live_llm` on the command line replaces it and runs them (verified).
- Coverage is enforced only when `--cov` is passed, so `make test-unit` passes `--cov=<package> --cov-branch` and `make test-integration` does not (a subset run cannot meet a whole-service floor).
- A function with one uncovered branch and 100% line coverage reported 85.71% combined, so the single floor already accounts for branches (verified).
- Exclude `mutants/`, `.hypothesis/`, `.coverage` and `coverage.xml` from git ([07-ignore-files.md](./07-ignore-files.md)); `mutants/` is also excluded from Ruff and mypy in the reference config of [11-clean-code.md](./11-clean-code.md).

### Makefile targets
```make
test-unit:
	uv run pytest tests/unit --cov=$(PACKAGE) --cov-branch --cov-report=term-missing:skip-covered --cov-report=xml --junitxml=reports/unit.xml

test-integration:
	uv run pytest tests/integration tests/contract -m "integration or contract" --junitxml=reports/integration.xml

test: test-unit test-integration
```
VERIFY: `uv run` as the launcher depends on the uv decision (F10, see [00-tech-stack.md](./00-tech-stack.md)). Mutation, live-model and e2e runs have no standard `make` target; they are CI jobs that call the tools directly. Proposal for the platform team: add `make mutation`.

### Fake model client and schema validation
```python
class ChatClient(Protocol):
    def complete(self, prompt: str) -> str: ...


class FakeChatClient:
    """Scripted replies, records prompts, fails loudly when the script runs out."""

    def __init__(self, replies: list[str]) -> None:
        self._replies = list(replies)
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._replies.pop(0)


class Triage(BaseModel):
    category: str
    confidence: float


def triage(client: ChatClient, text: str) -> Triage:
    return Triage.model_validate_json(client.complete(f"classify: {text}"))


@pytest.mark.parametrize(
    "bad", ["not json", '{"category": "x"}', '{"category": 1, "confidence": "hi"}']
)
def test_malformed_reply_is_rejected(bad: str) -> None:
    with pytest.raises(ValidationError):
        triage(FakeChatClient([bad]), "synthetic text")
```

### Property test
```python
@given(st.integers(min_value=0, max_value=10**9))
def test_double_is_monotonic_and_even(cents: int) -> None:
    out = double(Premium(cents)).cents
    assert out >= cents
    assert out % 2 == 0
```
Register profiles in `tests/conftest.py`: `dev` (`max_examples=50`) and `gate` (`max_examples=200, derandomize=True, deadline=None`); load with `settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "dev"))` and set `HYPOTHESIS_PROFILE=gate` in CI. Do not name a profile `ci`: Hypothesis documents a built-in profile of that name.

### Mutation gate script
mutmut 3.8.1 (tested) has `run`, `results`, `show`, `export-cicd-stats` and other commands but no failure threshold. Gate on its stats file:
```python
import json
import sys
from pathlib import Path

floor = float(sys.argv[1])
stats = json.loads(Path("mutants/mutmut-cicd-stats.json").read_text())
scored = stats["total"] - stats["skipped"]
score = 100.0 * stats["killed"] / scored if scored else 0.0
print(f"mutation score {score:.1f}% (floor {floor}%), survived={stats['survived']}")
sys.exit(0 if score >= floor else 1)
```
Job: `mutmut run && mutmut export-cicd-stats && python3 -I scripts/mutation_gate.py 80`. mutmut is POSIX-only (fork); CI runners must be Linux. Mutmut 3 mutates only code inside functions. VERIFY: mutmut on Python 3.15 beyond the toy run (3 mutants killed on 3.15.2).

### GitLab CI jobs (illustrative)
```yaml
unit:
  stage: test
  script:
    - make test-unit
  coverage: '/^TOTAL.*\s(\d+(?:\.\d+)?)%$/'   # VERIFY: regex against the actual log format
  artifacts:
    when: always
    reports:
      junit: reports/unit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  allow_failure: false
```
`coverage_report` syntax is from the GitLab coverage visualization page; the `junit` key and the `coverage:` regex were not confirmed there. VERIFY both on docs.gitlab.com. Pipeline structure itself is owned by [16-cicd-and-deployment.md](./16-cicd-and-deployment.md).

## Checklist
- [ ] A failing test existed before the code and the MR description records it (TST-003).
- [ ] New tests sit under `tests/unit/` mirroring `src/`, with registered markers (TST-004, TST-005).
- [ ] No network, real clock, real env or randomness in unit tests (TST-008, TST-009, TST-013).
- [ ] `make check` passes locally; coverage meets the tier floor with branch coverage on (TST-001, TST-025).
- [ ] LLM-dependent code is tested with a fake client and schema validation, with failure cases (TST-029, TST-030).
- [ ] No live model call outside `live_llm` scheduled jobs (TST-032).
- [ ] Data is synthetic (TST-036).
- [ ] No test was deleted, skipped, loosened or regenerated to get green (TST-042).
- [ ] Domain logic has property tests, and Tier A logic meets the mutation floor (TST-020, TST-021).
- [ ] Authorization deny-paths and tool contract tests exist (TST-018, TST-046).
- [ ] Any skipped or quarantined test has a reason and ticket (TST-040, TST-041).

## Common AI failure modes
- Writes the implementation first and a test that mirrors it, so the test can never fail.
- Deletes, skips, or loosens a failing test, widens a tolerance, or regenerates a golden file to reach green.
- Mocks the unit under test, or asserts only that a mock was called.
- Asserts exact LLM wording, or calls a live model from a unit test.
- Tests only the happy path; no malformed output, timeout, 429 or refusal cases.
- Uses `time.sleep`, the wall clock, unseeded randomness or the network in unit tests.
- Pastes realistic-looking personal data into fixtures.
- Adds `# pragma: no cover` or lowers `fail_under` instead of writing tests.
- Treats a flaky test as acceptable and adds retries.
- Reports "all tests pass" without having run `make check`.

## Related docs
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md): evals for non-deterministic behavior (owner of quality thresholds).
- [03-architecture.md](./03-architecture.md): fitness tests that live in `tests/unit/architecture/`.
- [01-codebase-practices.md](./01-codebase-practices.md): definition of done and agent working rules.
- [17-api-and-contracts.md](./17-api-and-contracts.md), [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md): the contracts that contract tests check.
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md): synthetic data and test data limits.
- [16-cicd-and-deployment.md](./16-cicd-and-deployment.md), [00-tech-stack.md](./00-tech-stack.md), [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md).
