# CI/CD and Deployment

> **Owner:** Platform Engineering lead (delivery) · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** docs.gitlab.com (ID token authentication; Azure OIDC; protected environments; IaC scanning; GitLab-managed Terraform/OpenTofu state; CI/CD YAML reference, partially read); developer.hashicorp.com Terraform `azurerm` backend. Anything not read in those pages is `VERIFY:`.

## Purpose
Define the delivery pipeline: required stages and gates, environment promotion, Terraform infrastructure delivery, GitLab protections, and deploy credentials with no long-lived secrets. GitLab is **confirmed** for code hosting and CI/CD. Terraform is `ASSUMPTION:` until the platform team records it in an ADR (F3). Whether GitLab is self-managed or GitLab.com is **unresolved** (F4), so runner, data-residency and scanner-tier specifics are marked. The standard `make` targets are defined in [00-tech-stack.md](./00-tech-stack.md); CI calls them rather than re-implementing commands.

## What depends on the unresolved items
| Topic | Self-managed | GitLab.com | Status |
|---|---|---|---|
| Runners | Platform team operates and patches | Shared or self-hosted runners | `ASSUMPTION:` self-hosted, isolated runners for anything touching cloud credentials; `VERIFY:` (F4) |
| Data residency of source/CI logs | Controlled by org | Hosted by vendor; check region options | `VERIFY:` with security and privacy (F4, F5) |
| Protected environments and deployment approvals | Premium or Ultimate | Premium or Ultimate | Confirmed by GitLab docs; licence tier `ASSUMPTION:` |
| IaC scanning (KICS-based) | Free, Premium, Ultimate; MR display, approvals and vulnerability report need Ultimate | same | Confirmed by GitLab docs |
| SAST, secret detection, dependency and container scanning, DAST | Tier-dependent; richer MR and report features usually need Ultimate | same | `VERIFY:` per-scanner tier on docs.gitlab.com (page for the scanner overview did not list them) |
| ID token `sub` claim extras (`ref_protected`, `environment_protected`, `deployment_tier`) | Needs GitLab 18.7 or later | Available when on that version | Confirmed for 18.7 by GitLab docs; `VERIFY:` instance version |
| Custom roles restricting Terraform state access | Ultimate only | Ultimate only | Confirmed by GitLab docs (only if using GitLab-managed state) |

If a built-in scanner is unavailable at the licensed tier, run an open-source equivalent (Semgrep, gitleaks, Trivy, pip-audit) as a plain job that fails the pipeline and uploads its report as an artifact. The gate matters, not the vendor. Scanner selection rationale is owned by [02-security.md](./02-security.md).

## Required pipeline stages
| Stage | Jobs | Gate |
|---|---|---|
| validate | `make fmt-check`, `make lint`, `make typecheck` | Blocks MR |
| test | `make test-unit`, `make test-integration` with coverage report | Blocks MR |
| eval | `make eval` (own harness, synthetic data) | Blocks MR when AI code, prompts or schemas change; see [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md) |
| security | SAST, secret detection, dependency scan, `make security` | Blocks MR on policy severity |
| build | Container build, SBOM, image scan, sign | Blocks merge to default branch |
| infra | `terraform fmt -check`, `validate`, IaC scan, policy-as-code, `plan` | Plan is posted to the MR |
| deploy | Per environment, protected, with OIDC credentials | Manual approval for production |

## Rules

### Pipeline gates
- **CIC-001** [MUST] [ci: gitlab] Every repository MUST have a root `.gitlab-ci.yml` that runs the `make` targets for format, lint, type check, tests and `make security`, and the pipeline MUST pass before an MR can merge.
- **CIC-002** [MUST] [ci: gitlab] Pipelines MUST run on merge request events and on the default branch; production deploys MUST run only from the protected default branch or protected tags.
- **CIC-003** [MUST] [ci] The `eval` job MUST run when prompts, tool schemas, agent code or model deployment settings change, and MUST fail below the thresholds defined in doc 14.
- **CIC-004** [MUST] [ci] SAST, secret detection, dependency scanning and container image scanning MUST run on every MR. Findings above the agreed severity MUST fail the job; `allow_failure: true` on a security job requires a waiver ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)).
- **CIC-005** [RETIRED] [ci] Superseded by DEP-024 and DEP-025 in [20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md); the pipeline job that runs them is defined in this doc's pipeline section.
- **CIC-006** [SHOULD] [ci] Common jobs SHOULD come from a central, versioned include (`include: project` pinned to a tag, or a CI/CD component pinned to a version), not copy-pasted per repository. Includes MUST NOT track a moving branch.
- **CIC-007** [MUST] [review] Job images MUST be pinned by digest or immutable tag and come from an approved registry ([20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md)); `latest` MUST NOT be used. (The GitLab Azure example uses `azure-cli:latest`; do not copy that.)
- **CIC-008** [SHOULD] [ci] Jobs SHOULD set `timeout`, `interruptible: true` (for non-deploy jobs) and `retry` only for infrastructure failures, not for failing tests.

### Protections and review
- **CIC-009** [MUST] [manual: GitLab settings] The default branch MUST be protected: no direct pushes, no force pushes, merge only via MR with a passing pipeline and at least one approval from someone other than the author.
- **CIC-010** [MUST] [review] A `CODEOWNERS` file MUST cover `infra/`, `.gitlab-ci.yml`, `registry/`, `prompts/`, `evals/` and security-relevant paths, with required approval from those owners. `VERIFY:` the tier needed for enforced CODEOWNERS approvals.
- **CIC-011** [MUST] [review] AI coding agents MUST NOT approve or merge their own MRs and MUST NOT have credentials with Maintainer rights or deploy rights (see [01-codebase-practices.md](./01-codebase-practices.md)).
- **CIC-012** [MUST] [manual: GitLab settings] Production and pre-production environments MUST be protected environments with an allowed-deployers list; production MUST require a deployment approval. Needs Premium or Ultimate; `ASSUMPTION:` licensed.
- **CIC-013** [MUST] [review] Changes to `.gitlab-ci.yml`, included templates and runner configuration MUST be reviewed by the platform team via CODEOWNERS; pipeline definitions MUST NOT be editable by a deploy-job author unreviewed.
- **CIC-014** [MUST] [manual] Protected CI/CD variables MUST NOT be used for cloud credentials; use OIDC (CIC-016). Any remaining variables MUST be masked and protected and scoped to environments.

### Deploy credentials (OIDC, no long-lived secrets)
- **CIC-015** [MUST] [ci] Deploy and Terraform jobs MUST NOT use stored client secrets, service principal passwords or personal access tokens for Azure.
- **CIC-016** [MUST] [ci] Jobs that need Azure MUST obtain a short-lived GitLab ID token via `id_tokens:` with an explicit `aud` and exchange it through a Microsoft Entra federated identity credential (workload identity federation).
- **CIC-017** [MUST] [review] Federated credentials MUST be scoped narrowly: one app registration or user-assigned managed identity per environment and purpose (plan vs apply), with a subject that pins project, ref and, where available, environment. Wildcard subjects MUST NOT be used for production.
- **CIC-018** [MUST] [review] Plan identities MUST have read-only roles; apply identities MUST be usable only from protected refs or protected environments. `VERIFY:` use `ref_protected` / `environment_protected` custom claims (GitLab 18.7 or later) in the subject or a claims-matching expression.
- **CIC-019** [SHOULD] [review] Prefer GitLab project and namespace IDs over path-based claims in trust policies, because paths change on rename (GitLab docs recommendation).
- **CIC-020** [MUST] [review] Azure role assignments for pipeline identities MUST be least privilege per [02-security.md](./02-security.md); no subscription-wide Owner.

### Terraform ASSUMPTION: final choice pending (F3)
- **CIC-021** [MUST] [ci: terraform] Infrastructure MUST be defined in Terraform under `infra/`, with `terraform fmt -check` and `terraform validate` in CI. Provider versions MUST be pinned and `.terraform.lock.hcl` committed.
- **CIC-022** [MUST] [review] State MUST be remote in an Azure Storage container using the `azurerm` backend with Microsoft Entra authentication (`use_azuread_auth`, `use_oidc`), one state key per environment and component. The backend supports locking natively; do not disable it.
- **CIC-023** [MUST] [review] The state storage account MUST have no public network access (private endpoint), soft delete and versioning enabled, and data-plane RBAC limited to pipeline identities and a break-glass group. `VERIFY:` exact Azure settings and region policy. State contains sensitive values; treat it as restricted data.
- **CIC-024** [MUST] [ci] Merge requests MUST run `terraform plan` and publish the plan summary; `apply` MUST run only after merge, on the protected branch, using the saved plan file from a protected environment job. Plan files MUST be restricted artifacts (they may contain secrets) with short expiry.
- **CIC-025** [MUST] [ci: checkov or trivy config or GitLab IaC scanning] IaC MUST be scanned in every MR. GitLab IaC scanning (KICS-based; `Jobs/SAST-IaC.gitlab-ci.yml`) is allowed; Checkov or Trivy config are alternatives. `VERIFY:` current tool choice with security (F4).
- **CIC-026** [SHOULD] [ci: conftest or OPA] Policy-as-code SHOULD evaluate the plan JSON for rules such as: private endpoints required, Canada Central/East only, no public storage, required tags, no wildcard role assignments. `VERIFY:` tool and policy repo.
- **CIC-027** [SHOULD] [ci] A scheduled pipeline SHOULD run `terraform plan -detailed-exitcode` per environment to detect drift and open an issue on non-empty diffs.
- **CIC-028** [MUST] [review] Modules MUST be versioned, have an owner and a README with inputs and outputs, and be consumed by pinned version. No secrets in variables files or state outputs marked non-sensitive.
- **CIC-029** [MUST] [review] AI agents MUST NOT run `terraform apply` or `destroy` against shared environments; they may run `fmt`, `validate` and local `plan` without credentials.

### Environments, release and rollback
- **CIC-030** [MUST] [review] Promotion MUST follow dev -> test -> production with the same immutable image digest, built once. Environment differences come from configuration only.
- **CIC-031** [MUST] [ci] Production images MUST be signed and provenance recorded, and the deploy job MUST verify the signature. `VERIFY:` signing tool (for example cosign) and where signatures are stored.
- **CIC-032** [MUST] [review] Every deploy MUST have a tested rollback (redeploy previous digest) and use `resource_group` or equivalent so two deploys to one environment never run concurrently.
- **CIC-033** [SHOULD] [review] Risky changes SHOULD ship behind feature flags with progressive rollout; flags double as kill switches per [18-reliability-and-operations.md](./18-reliability-and-operations.md).
- **CIC-034** [MUST] [review] Database or schema migrations MUST be backward compatible with the previous release (expand then contract).
- **CIC-035** [MUST] [ci] Deployments MUST record version, digest, approver and pipeline link as deployment evidence retained per doc 12.

## Worked `.gitlab-ci.yml` skeleton
Illustrative. Names in angle brackets are placeholders. Items marked `VERIFY:` are not confirmed against current GitLab docs.

```yaml
# .gitlab-ci.yml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG

default:
  image: <approved-registry>/python@sha256:<digest>     # pinned (CIC-007)
  interruptible: true
  timeout: 20 minutes

stages: [validate, test, eval, security, build, infra, deploy]

include:
  # VERIFY: template paths and tier; replace with approved central include
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Jobs/SAST-IaC.gitlab-ci.yml               # confirmed in IaC scanning docs
  # - project: <platform-group>/ci-templates           # preferred, pinned
  #   ref: <tag>
  #   file: /python-service.yml

variables:
  UV_FROZEN: "1"          # VERIFY: uv env var; or call `uv sync --frozen` in make install

.make: &make
  before_script: [make install]

lint:
  stage: validate
  <<: *make
  script: [make fmt-check, make lint, make typecheck]

unit-tests:
  stage: test
  <<: *make
  script: [make test-unit]
  coverage: '/TOTAL.*\s+(\d+%)$/'                        # VERIFY: matches your coverage output
  artifacts:
    when: always
    reports:
      junit: reports/junit.xml

integration-tests:
  stage: test
  <<: *make
  script: [make test-integration]

evals:
  stage: eval
  <<: *make
  script: [make eval]                                    # synthetic datasets only
  rules:
    - changes: [prompts/**/*, registry/**/*, evals/**/*, src/**/ai/**/*]

dependency-audit:
  stage: security
  <<: *make
  script: [make security]                                # pip-audit, gitleaks, bandit etc.
  # GitLab dependency scanning / container scanning templates: VERIFY: tier and names

build-image:
  stage: build
  script:
    - make build                                         # builder choice (kaniko, buildah...) VERIFY:
    # - generate SBOM, scan image, sign image (VERIFY: tools)
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

tf-validate:
  stage: infra
  image: <approved-registry>/terraform@sha256:<digest>
  script:
    - cd infra/envs/${TF_ENV:-dev}
    - terraform fmt -check -recursive
    - terraform init -backend=false
    - terraform validate

tf-plan:
  stage: infra
  image: <approved-registry>/terraform@sha256:<digest>
  id_tokens:
    ARM_OIDC_TOKEN:                                      # name read by azurerm; VERIFY: in provider docs
      aud: <audience-matching-federated-credential>
  variables:
    ARM_USE_OIDC: "true"
    ARM_USE_AZUREAD: "true"
    ARM_CLIENT_ID: "<plan-identity-client-id>"           # non-secret identifier
    ARM_TENANT_ID: "<tenant-id>"
    ARM_SUBSCRIPTION_ID: "<subscription-id>"
  script:
    - cd infra/envs/<env>
    - terraform init
    - terraform plan -out=plan.tfplan
    - terraform show -json plan.tfplan > plan.json       # feed to policy-as-code
  artifacts:
    paths: [infra/envs/<env>/plan.tfplan, infra/envs/<env>/plan.json]
    expire_in: 1 day
    access: developer                                    # VERIFY: key and value; plan files may hold secrets
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

deploy-prod:
  stage: deploy
  image: <approved-registry>/azure-cli@sha256:<digest>
  environment:
    name: production                                     # protected environment (CIC-012)
  resource_group: production
  id_tokens:
    AZURE_OIDC_TOKEN:
      aud: <audience-matching-federated-credential>
  script:
    - az login --service-principal -u "$AZURE_CLIENT_ID" -t "$AZURE_TENANT_ID" --federated-token "$AZURE_OIDC_TOKEN"
    - ./scripts/deploy.sh "$IMAGE_DIGEST"                # verify signature first (CIC-031)
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

Notes on the skeleton:
- The `az login --federated-token` shape and `id_tokens` syntax follow GitLab's Azure OIDC page. That page nests `script` oddly under a job named `auth`; use normal job structure as above.
- For `terraform apply`, add a `tf-apply` job in the `deploy` stage with `environment`, the apply identity's `ARM_CLIENT_ID`, `needs` on `tf-plan` artifacts from the same commit, and `terraform apply plan.tfplan`. `VERIFY:` that a plan from an MR pipeline is reusable after merge, otherwise re-plan on the default branch and require approval of the new plan.
- The Entra federated credential uses issuer = your GitLab URL, subject like `project_path:<group>/<project>:ref_type:branch:ref:<default-branch>`, and audience equal to the job's `aud`. GitLab docs note default `sub` format can be changed and extended; `VERIFY:` current format on your GitLab version.
- Troubleshooting codes in GitLab docs: `AADSTS70021` (no matching federated identity record, check issuer, subject, audience) and `AADSTS700212` (no matching audience): audience mismatch is the usual cause. `VERIFY:` exact code spelling in Microsoft docs.

## Terraform remote state and OIDC notes
```hcl
terraform {
  required_version = ">= <min>"            # pin; VERIFY: current Terraform release
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> <x.y>" }  # VERIFY: current major
  }
  backend "azurerm" {
    use_azuread_auth     = true
    use_oidc             = true
    tenant_id            = "<tenant-id>"
    client_id            = "<identity-client-id>"
    storage_account_name = "<state-account>"
    container_name       = "tfstate"
    key                  = "<env>/<component>.tfstate"
  }
}
```
- Per the Terraform `azurerm` backend docs, the Entra OIDC path requires `use_azuread_auth`, `tenant_id`, `storage_account_name`, `container_name`, `key`, `use_oidc` and `client_id`. `resource_group_name` and `subscription_id` are only needed for management-plane lookups.
- `ARM_USE_OIDC`, `ARM_USE_AZUREAD`, `ARM_CLIENT_ID`, `ARM_TENANT_ID` and `ARM_OIDC_TOKEN` are the documented environment variables. The `oidc_token` and `oidc_token_file_path` settings are described as for third-party integrations; `VERIFY:` that passing GitLab's token through `ARM_OIDC_TOKEN` works for your provider version (the backend page shows a GitHub example only).
- The identity running `init` needs data-plane RBAC on the state container (for example a Storage Blob Data role). `VERIFY:` the minimum role.
- GitLab-managed Terraform/OpenTofu state exists (GitLab docs, 18.3 and later) but this standard uses Azure Storage state per the recorded decision; do not mix backends.
- Terraform vs OpenTofu: GitLab's current docs lead with OpenTofu. Terraform is the planned tool, so `VERIFY:` licence acceptability and ADR (F3) before depending on either vendor component.

## Checklist
- [ ] `.gitlab-ci.yml` runs all `make` gates and passes on the MR (CIC-001).
- [ ] Default branch and production environment protected; CODEOWNERS covers infra and pipeline files (CIC-009, CIC-010, CIC-012).
- [ ] No long-lived Azure secrets; ID token with explicit `aud`; narrow federated credentials (CIC-015 to CIC-018).
- [ ] Job images pinned; includes pinned (CIC-006, CIC-007).
- [ ] Terraform: pinned providers, remote Entra-authenticated state, plan in MR, apply after merge (CIC-021 to CIC-024).
- [ ] IaC scan and policy-as-code run (CIC-025, CIC-026).
- [ ] SBOM, image signature and deployment evidence kept (DEP-024, CIC-031, CIC-035).
- [ ] Rollback tested; flags and kill switch available (CIC-032, CIC-033).
- [ ] Open items F3 and F4 recorded in the ADR.

## Common AI failure modes
- Generating another vendor's workflow files, or using the wrong term for a merge request, instead of `.gitlab-ci.yml` and merge requests.
- Storing `ARM_CLIENT_SECRET` or a service principal password as a CI variable instead of OIDC.
- Wildcard subjects in federated credentials, or one identity shared by plan and apply, dev and prod.
- Pinning nothing: `latest` images, floating includes, unpinned providers.
- Running `terraform apply` from the MR pipeline, or applying a freshly generated plan nobody reviewed.
- Disabling a failing security job with `allow_failure: true` to get green.
- Assuming Ultimate-only features (MR security widgets, advanced scanners) exist at the licensed tier.
- Copying the GitLab docs example's `latest` image or the odd `auth:` job nesting literally.
- Caching or storing plan files and state as publicly readable artifacts.
- Granting the deploy identity Owner so the pipeline "just works".

## Related docs
- [00-tech-stack.md](./00-tech-stack.md): `make` targets and tool choices.
- [02-security.md](./02-security.md): scanner selection, least privilege.
- [06-secrets-and-env.md](./06-secrets-and-env.md): secrets handling.
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md): eval gates.
- [18-reliability-and-operations.md](./18-reliability-and-operations.md): rollback, kill switch.
- [20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md): registries, SBOM.
- [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md): waivers for gate bypass.
- [01-codebase-practices.md](./01-codebase-practices.md): agent rules, MR practice.
- [12-governance-and-compliance.md](./12-governance-and-compliance.md): evidence retention.
