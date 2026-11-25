# Dependencies and Licensing

> **Owner:** Platform Engineering lead with Security and Legal · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** docs.astral.sh/uv (project sync and lock concepts); pypi.org pip-audit page (2.10.1 at read time); docs.renovatebot.com GitLab platform page. Licence policy: none yet (F7). Everything not read there is `VERIFY:`.

## Purpose
Every dependency is code we run with our privileges and a legal obligation we accept. AI coding agents add packages quickly and sometimes add packages that do not exist or are malicious lookalikes ("slopsquatting"). This doc owns registries, pinning and lockfiles, update cadence, licence policy, hallucinated-package checks, SBOM, internal packages and vendor SDK approval. Vulnerability scanning and supply-chain threat model are in [02-security.md](./02-security.md); the CI job layout is in [16-cicd-and-deployment.md](./16-cicd-and-deployment.md); the tool choice (`uv`) is in [00-tech-stack.md](./00-tech-stack.md).

## Open items and assumptions
| Item | Status |
|---|---|
| Licence allow/deny list | `ASSUMPTION:` the table below is a **starting proposal only**; Legal owns the final list (F7) |
| `uv` as package and lock manager | `ASSUMPTION:` approved (F10); fallback is pip-tools with hashes |
| Approved package registries and internal index | `ASSUMPTION:` an internal proxy or mirror exists or will; product choice (for example GitLab package registry or another) is an ADR; `VERIFY:` |
| Renovate vs another update bot | `ASSUMPTION:` Renovate; Renovate supports `platform=gitlab` and creates merge requests; hosted vs self-run depends on GitLab hosting (F4) |

## Proposed licence policy (pending Legal, F7)
| Category | Examples | Default |
|---|---|---|
| Permissive | MIT, BSD-2/3-Clause, Apache-2.0, ISC, PSF | Allowed |
| Weak copyleft | MPL-2.0, LGPL (dynamic use) | Review: allowed only for unmodified, dynamically linked use |
| Strong or network copyleft | GPL, AGPL, SSPL | Denied unless Legal approves in writing |
| Non-commercial, source-available, or custom terms | CC BY-NC, BSL, "free for research" | Denied |
| Unknown or missing licence | no declared licence | Denied until resolved |
| Model weights, datasets, prompts from third parties | any | Separate review: licence and data provenance, see [12-governance-and-compliance.md](./12-governance-and-compliance.md) |

## Rules

### Registries and sources
- **DEP-001** [MUST] [ci] Python packages MUST be installed only from the approved registry or internal mirror configured in the project (`pyproject.toml` / uv index settings). Ad hoc `--index-url`, `--extra-index-url`, direct URLs and VCS dependencies MUST NOT be used without a waiver ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)). `VERIFY:` uv index configuration keys.
- **DEP-002** [MUST] [ci] Where more than one index is configured, each package MUST be pinned to a single named index so a public package cannot shadow an internal name (dependency confusion).
- **DEP-003** [MUST] [ci] Base images and tool images MUST come from the approved container registry and be pinned by digest; see CIC-007 in [16-cicd-and-deployment.md](./16-cicd-and-deployment.md).

### Pinning and lockfiles
- **DEP-004** [MUST] [ci: lockfile check] Every service MUST commit a lockfile (`uv.lock`) generated from `pyproject.toml`; CI MUST fail if the lockfile is stale (`uv lock --check`, documented as not updating the lockfile).
- **DEP-005** [MUST] [ci] CI and container builds MUST install from the lockfile without re-resolving. `VERIFY:` the exact `uv sync` flag (`--locked` / `--frozen`); the uv page read shows them with `uv run` and defines `--frozen` as skipping the up-to-date check.
- **DEP-006** [SHOULD] [ci] The lockfile SHOULD include artifact hashes; installs SHOULD verify them. `VERIFY:` uv hash behaviour; with pip-tools use `--generate-hashes`.
- **DEP-007** [MUST] [review] Direct dependencies in `pyproject.toml` MUST have a lower bound and a justified upper bound policy (compatible-release for stable libraries, exact for fast-moving or pre-1.0 libraries).
- **DEP-008** [MUST] [review] `opentelemetry-*` packages MUST be upgraded as one set (see [10-logging-observability.md](./10-logging-observability.md)); Foundry and vendor AI SDKs MUST be pinned exactly (see [23-azure-foundry-standards.md](./23-azure-foundry-standards.md)).
- **DEP-009** [MUST] [lint: ruff] Dev, test and docs dependencies MUST live in separate dependency groups and MUST NOT be installed in production images.

### Update cadence
- **DEP-010** [SHOULD] [ci: renovate] A bot SHOULD open grouped, scheduled update merge requests (`ASSUMPTION:` weekly for minor and patch; major versions individually). Bot merge requests MUST pass the same pipeline and review as human ones.
- **DEP-011** [MUST] [ci] Known-vulnerable dependencies MUST be remediated within the SLA by severity (`ASSUMPTION:` critical 7 days, high 30 days, medium 90 days) or carry a waiver with compensating controls.
- **DEP-012** [MUST] [review] Bot or agent merge requests MUST NOT auto-merge major upgrades, new transitive licences in a denied category, or any change to a lockfile entry for an AI or security library without human review.
- **DEP-013** [SHOULD] [review] Dependencies with no release in 24 months, a single maintainer, or an archived repository SHOULD be flagged for replacement in the next review.
- **DEP-014** [MUST] [manual] Python minor version upgrades follow the policy in doc 00; dependencies that block the supported minor MUST be replaced or upgraded.

### Licences
- **DEP-015** [MUST] [ci: licence scanner] CI MUST generate a licence report for direct and transitive dependencies and fail on denied or unknown licences. `VERIFY:` tool (for example a CycloneDX-based or licence-checker tool) and GitLab licence features by tier.
- **DEP-016** [MUST] [review] A new direct dependency in the review category MUST have recorded Legal approval before merge.
- **DEP-017** [MUST] [review] The licence allow/deny list MUST live in one machine-readable file in the platform repository, owned by Legal, and be consumed by CI. Services MUST NOT keep their own copies.
- **DEP-018** [MUST] [review] Code, data and model assets copied from outside the org MUST have their licence recorded; AI-generated code MUST NOT copy verbatim from licensed sources (see [01-codebase-practices.md](./01-codebase-practices.md)).

### Hallucinated and typosquatted packages
- **DEP-019** [MUST] [ci] CI MUST fail when a new dependency is not on the approved registry, or when the package name is not already in a platform-maintained allowlist and has not passed the new-package check (DEP-020).
- **DEP-020** [MUST] [review] A new-package check MUST confirm: the exact name exists on the approved index, is not one edit away from a popular package, has a real source repository matching the publisher, has release history, and is not newly created. Record the result in the MR description.
- **DEP-021** [MUST] [review] AI agents MUST NOT run installs of packages they have not verified exist; they MUST propose the addition and run the check. Packages suggested by a model MUST be treated as untrusted until verified.
- **DEP-022** [SHOULD] [ci] CI SHOULD run `pip-audit` against the lockfile or project (`--locked` audits lock files; `--strict` fails on collection errors). pip-audit does not defend against malicious packages, so it complements DEP-020 and does not replace it.
- **DEP-023** [SHOULD] [ci] Install steps SHOULD disable running arbitrary build scripts from unknown sdists where supported (prefer wheels). `VERIFY:` the uv/pip option names.

### SBOM
- **DEP-024** [MUST] [ci] Each release MUST produce a CycloneDX SBOM (for example `uv export` with a CycloneDX format, or `pip-audit -f cyclonedx-json`; `VERIFY:` current flags) covering application and image layers, attached to the release.
- **DEP-025** [MUST] [ci] SBOMs MUST be retained per doc 12 and be queryable by package name so a new advisory can be mapped to affected services within one business day (`ASSUMPTION:`).

### Internal packages and vendor SDKs
- **DEP-026** [SHOULD] [review] Shared internal code SHOULD be published as versioned packages (semver, changelog, owner) to the internal index, not copied between repositories or consumed from branches.
- **DEP-027** [MUST] [review] Internal packages MUST pass the same gates as services (tests, type check, scans, SBOM) and MUST NOT contain secrets, customer data or environment-specific values.
- **DEP-028** [MUST] [review] A new vendor SDK or client library for an external service MUST be approved by Security and, where it touches data or models, by the owners of docs 12 and 15 before adoption. Preview or beta SDK features in production require a waiver.
- **DEP-029** [MUST] [review] The approved-dependency exceptions list MUST name an owner and expiry for each entry; expired entries fail CI.
- **DEP-030** [SHOULD] [review] Prefer the standard library or an existing approved dependency over adding a new one for trivial functionality.

## Checklist
- [ ] Lockfile committed, current and used in CI and builds (DEP-004, DEP-005).
- [ ] Only approved indexes; packages pinned to an index (DEP-001, DEP-002).
- [ ] Licence report passes; Legal sign-off for review-category additions (DEP-015, DEP-016).
- [ ] New-package check recorded for each added dependency (DEP-020).
- [ ] pip-audit and vulnerability SLA met (DEP-011, DEP-022).
- [ ] SBOM produced and retained (DEP-024, DEP-025).
- [ ] Vendor SDK approved; AI SDK versions pinned exactly (DEP-008, DEP-028).
- [ ] Update bot configured and its MRs reviewed (DEP-010, DEP-012).

## Common AI failure modes
- Adding a package that does not exist, or a near-miss name of a real one.
- Running `pip install` ad hoc and committing only `pyproject.toml` without the lockfile.
- Adding `--extra-index-url` to "fix" a resolution error.
- Choosing a convenient library with a GPL/AGPL or non-commercial licence without checking.
- Upgrading all dependencies at once, including OpenTelemetry and AI SDKs separately.
- Putting dev tools in production dependencies, bloating the image and attack surface.
- Assuming pip-audit catches malicious packages.
- Copy-pasting a "latest" install line from a blog instead of the pinned, approved version.
- Treating a bot's green merge request as pre-approved.

## Related docs
- [00-tech-stack.md](./00-tech-stack.md): `uv`, Python version policy.
- [02-security.md](./02-security.md): supply-chain and vulnerability scanning.
- [16-cicd-and-deployment.md](./16-cicd-and-deployment.md): CI jobs, image pinning.
- [12-governance-and-compliance.md](./12-governance-and-compliance.md): third-party approval, evidence retention.
- [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md): dependency waivers.
- [10-logging-observability.md](./10-logging-observability.md): OTel version pinning.
- [23-azure-foundry-standards.md](./23-azure-foundry-standards.md): Foundry SDK pinning.
- [01-codebase-practices.md](./01-codebase-practices.md): AI-generated code provenance.
