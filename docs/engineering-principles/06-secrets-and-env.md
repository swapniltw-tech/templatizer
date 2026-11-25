# Secrets and Environment Configuration

> **Owner:** Security lead with Platform Engineering lead · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** learn.microsoft.com (Key Vault Azure RBAC guide; Key Vault rotation tutorial; Azure Identity for Python and credential chains; Entra workload identity federation); docs.gitlab.com (CI/CD variables; ID token authentication); pydantic-settings documentation (verified by running the example below)

## Purpose
Define how services receive configuration and secrets: Azure Key Vault as the store, managed or workload identity as the way in, `.env` files as a local-only convenience, and `pydantic-settings` as the only reader of the environment. The goal is that no secret ever exists in Git, an image, a log or an agent's context, and that the few secrets that remain can be rotated without a deploy.

Ignore-file entries for `.env*` are in [07-ignore-files.md](./07-ignore-files.md). Redaction of secrets and personal data in logs is owned by [10-logging-observability.md](./10-logging-observability.md) and [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md). Pipeline authentication design is owned by [16-cicd-and-deployment.md](./16-cicd-and-deployment.md). Agent permission settings that keep agents away from secrets are in [08-claude-md.md](./08-claude-md.md).

## Rules

### Storage and access
- **SCR-001** [MUST] [ci: gitleaks] Secrets MUST NOT appear in source code, Git history, container images, build arguments, logs, traces, prompts, test fixtures or documentation examples. Secret scanning runs in pre-commit and in CI.
- **SCR-002** [MUST] [review] Azure Key Vault MUST be the only secret store for deployed environments (dev, test, prod). Secrets MUST NOT live in repo files, GitLab variables used as a vault, wiki pages or chat.
- **SCR-003** [MUST] [ci: terraform-scan] Vaults MUST use the Azure RBAC permission model. New vaults MUST NOT use legacy access policies. Microsoft states RBAC is the default for newly created vaults from API version 2026-02-01; VERIFY: confirm the model on each existing vault.
- **SCR-004** [MUST] [review] There MUST be one vault per application per environment, with roles assigned at the vault scope. Per-secret role assignments MUST NOT be used except for the two exceptions Microsoft documents (a secret needed by one individual, or a secret shared by several applications).
- **SCR-005** [MUST] [review] Workloads MUST authenticate to Azure with a managed identity or workload identity. Client secrets, storage account keys and connection strings with embedded keys MUST NOT be used where Microsoft Entra authentication is supported.
- **SCR-006** [MUST] [review] Each service MUST have its own identity with the least privilege role: `Key Vault Secrets User` (read secret contents) for applications. `Key Vault Secrets Officer` is reserved for rotation automation and deployment pipelines. Agent-specific identity rules are in [02-security.md](./02-security.md).
- **SCR-007** [MUST] [test: unit] Deployed code MUST construct an explicit credential (`ManagedIdentityCredential`, or `WorkloadIdentityCredential` on Kubernetes). `DefaultAzureCredential` MUST be used only when `environment == "local"`. Microsoft's guidance is to replace `DefaultAzureCredential` with a specific credential once an app is deployed (debuggability, latency, and unpredictable behavior from environment variables).
- **SCR-008** [MUST] [review] Developers MUST NOT have standing read access to production vaults. Access is by approved, time-bound elevation recorded for audit (mechanism: ASSUMPTION: privileged identity management or equivalent, F5).
- **SCR-009** [MUST] [review] Key Vault MUST have soft delete and purge protection enabled, network access restricted to private endpoints, and diagnostic logs sent to the central log workspace. VERIFY: confirm exact settings and Azure Policy definitions with the platform team (F5).

### Configuration in code
- **SCR-010** [MUST] [test: architecture] `config.py` MUST be the only module that reads `os.environ`, `.env` files or other process-level configuration. Other modules receive typed settings through dependency injection (composition root in `main.py`).
- **SCR-011** [MUST] [lint: mypy] Configuration MUST be a `pydantic-settings` `BaseSettings` subclass with typed fields, `extra="forbid"`, and `SecretStr` for any secret value. Invalid configuration MUST stop the process at startup.
- **SCR-012** [MUST] [test: unit] Secrets MUST NOT have a non-empty default value in code (`None` is allowed so the validator can reject its absence or presence by environment), and outside `local` they MUST NOT be accepted from plain environment variables. The settings class MUST enforce this with a validator. Platform-injected Key Vault references are the one alternative; VERIFY: check what the chosen hosting platform supports before allowing it, and record it in an ADR.
- **SCR-013** [MUST] [test: unit] Secret values MUST be fetched through one Key Vault adapter (`adapters/keyvault/`) that returns `SecretStr`, never logs values, and takes the credential as a parameter so tests can inject a fake.
- **SCR-014** [MUST] [test: unit] Services MUST tolerate rotation: cache secrets with a short time-to-live or re-fetch once on an authentication failure, and MUST NOT require a restart to pick up a new secret version.

### `.env` files
- **SCR-015** [MUST] [ci: gitleaks] `.env` MUST be used for local development only. It MUST never be copied into an image, never deployed, and never contain production values.
- **SCR-016** [MUST] [test: unit] The repo MUST commit `.env.example` listing every variable the settings class reads (commented out where the default applies), with obviously fake values. A unit test (below) MUST fail when `.env.example` and the settings class disagree.
- **SCR-017** [MUST] [ci: image-scan] Images and deployment artifacts MUST NOT contain `.env` files (enforced by the `.dockerignore` allow-list in [07-ignore-files.md](./07-ignore-files.md)).
- **SCR-018** [SHOULD] [review] Local development SHOULD authenticate with the developer's own sign-in (`az login`) against a development vault, not with shared secrets in `.env`.

### Rotation and lifecycle
- **SCR-019** [MUST] [review] Every secret MUST have an owner, a purpose, an expiry date and a rotation period recorded in the vault (tags) and the inventory. Rotation period: ASSUMPTION: set by the Security team (F5); until then 90 days for secrets that cannot be eliminated.
- **SCR-020** [SHOULD] [review] Teams SHOULD eliminate secrets before rotating them (managed identity, federated credentials, Entra authentication, disabling shared key authorization). Microsoft's rotation tutorial itself says to prefer Entra authorization over shared account keys.
- **SCR-021** [SHOULD] [review] Where a secret remains, rotation SHOULD be automated using the Key Vault near-expiry event (`SecretNearExpiry`, published 30 days before expiry per the Microsoft tutorial) and a function that updates the dependent service and writes a new secret version.
- **SCR-022** [MUST] [review] Secrets MUST be rotated on suspected exposure, on departure of anyone with access, and on any change in who may read them.
- **SCR-023** [MUST] [manual] A committed or logged secret MUST be treated as compromised: revoke and rotate first, then remove it from history, then open an incident per [18-reliability-and-operations.md](./18-reliability-and-operations.md). Deleting the commit alone is not remediation.

### CI/CD
- **SCR-024** [MUST] [review] Pipelines MUST authenticate to Azure by workload identity federation using GitLab ID tokens (`id_tokens:`), not long-lived client secrets stored in CI/CD variables. VERIFY: federation setup and subject format against current GitLab and Microsoft docs before use; design is owned by [16-cicd-and-deployment.md](./16-cicd-and-deployment.md).
- **SCR-025** [MUST] [review] GitLab CI/CD variables MUST hold only non-secret configuration, or bootstrap values that cannot come from federation. Any such secret variable MUST be Protected, Masked (or Masked and hidden where available), environment-scoped, and never defined in `.gitlab-ci.yml`.
- **SCR-026** [MUST] [review] Container builds MUST NOT receive secrets through `ARG`, `ENV` or command-line arguments. Image content rules are in [07-ignore-files.md](./07-ignore-files.md).

### Logging, tests and agents
- **SCR-027** [MUST] [test: unit] Code MUST NOT log secret values, tokens or full connection strings. Log the secret name, never the value. `SecretStr` MUST be kept as `SecretStr` until the last call that needs the plain value.
- **SCR-028** [MUST] [review] Tests and CI MUST use fake values and local fakes. Production or shared-environment secrets MUST NOT be used in tests.
- **SCR-029** [MUST] [review] AI coding agents MUST NOT read, print, copy or create real secrets. They MUST NOT run `env`, `printenv` or `cat .env`, and MUST NOT write real values into any file, including `.env`. The repo's agent settings deny the obvious paths; see [08-claude-md.md](./08-claude-md.md) for why those denies are not a security boundary on their own.
- **SCR-030** [MAY] [review] Teams MAY use platform-native Key Vault integration (for example, Key Vault references or a secrets store driver) instead of the SDK adapter, subject to SCR-012.

## Reference pattern

### Access model
| Item | Standard |
|---|---|
| Store | One Azure Key Vault per app per environment, RBAC model |
| Runtime identity | Managed identity (Azure-hosted) or workload identity (Kubernetes), one per service |
| Runtime role | `Key Vault Secrets User` at the vault scope |
| Pipeline role | `Key Vault Secrets Officer` only for jobs that write secrets; reached through federation |
| Local development | Developer sign-in with `az login`, development vault only |
| Secret names | Lowercase with hyphens, e.g. `database-password`; stored as names in config, never as values |

Illustrative role assignment (from the Microsoft RBAC guide; infrastructure is normally Terraform, see [16-cicd-and-deployment.md](./16-cicd-and-deployment.md)). VERIFY: not executed here (no Azure subscription in the authoring environment):

```bash
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee <principal-id-of-service-identity> \
  --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.KeyVault/vaults/<vault-name>
```

### `config.py` (pydantic-settings)
Checked on 2026-11-25 with pydantic 2.14 and pydantic-settings 2.16 on Python 3.14: ruff and `mypy --strict` clean, and exercised with the cases below. The behavior notes are results, not assumptions.

```python
"""Application configuration. The only module that reads the environment."""

from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, HttpUrl, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings loaded from environment variables (prefix APP_)."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",  # local development only; the file is absent when deployed
        env_file_encoding="utf-8",
        extra="forbid",  # unknown keys in the .env file fail fast (real env vars are not checked)
        frozen=True,
    )

    environment: Literal["local", "dev", "test", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    request_timeout_s: float = Field(default=10.0, gt=0, le=120)

    # Non-secret pointers: where secrets live and what they are called.
    key_vault_url: HttpUrl | None = None
    database_password_secret_name: str = "database-password"

    # Local development only. Outside "local" this field must stay unset and the
    # value is read from Key Vault by the adapter. SecretStr masks repr and logs.
    database_password: SecretStr | None = None

    @model_validator(mode="after")
    def _check_environment_rules(self) -> Self:
        if self.environment != "local":
            if self.key_vault_url is None:
                msg = "APP_KEY_VAULT_URL is required outside the local environment"
                raise ValueError(msg)
            if self.database_password is not None:
                msg = "secrets must not be passed as plain env vars outside local"
                raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings (validated once, fails fast at startup)."""
    return Settings()
```

Observed behavior:

| Input | Result |
|---|---|
| No variables | Valid, `environment="local"`, `database_password` is `None` |
| `APP_ENVIRONMENT=prod` alone | Fails: `APP_KEY_VAULT_URL` required |
| `prod` with `APP_KEY_VAULT_URL` | Valid |
| `prod` plus `APP_DATABASE_PASSWORD` | Fails: secrets not accepted as plain env outside local |
| `APP_LOG_LEVEL=LOUD` | Fails with the allowed values |
| `repr(settings)` with a password set | Shows `SecretStr('**********')` |
| `.env` containing an unprefixed key such as `AZURE_CLIENT_ID=...` | **Fails** (`extra="forbid"` applies to the file): keep only `APP_*` keys in `.env` |
| An unknown `APP_NOPE=1` in the real environment | **Not** rejected (only file entries are checked) |

### Key Vault adapter (`adapters/keyvault/`)
Checked with ruff and `mypy --strict` (imports `azure-identity` and `azure-keyvault-secrets`); not run against a real vault. VERIFY: first run against a development vault.

```python
"""Key Vault adapter: fetches secrets using the workload's own identity."""

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from pydantic import SecretStr


def build_credential(environment: str) -> TokenCredential:
    """Local: developer sign-in chain. Deployed: one explicit credential, no chain."""
    if environment == "local":
        return DefaultAzureCredential()
    return ManagedIdentityCredential()


def get_secret(vault_url: str, name: str, credential: TokenCredential) -> SecretStr:
    """Read one secret by name; never log the value."""
    client = SecretClient(vault_url=vault_url, credential=credential)
    return SecretStr(client.get_secret(name).value or "")
```

Notes:
- With a user-assigned identity, pass `client_id=` to `ManagedIdentityCredential`. On Kubernetes, use `WorkloadIdentityCredential` instead (the Azure Identity library documents it for Microsoft Entra Workload ID).
- Wrap `get_secret` with a short-lived cache and one retry on an authentication failure to satisfy SCR-014.
- Hand the `TokenCredential` in from `main.py` so tests pass a fake credential.

### `.env.example`
Committed; fake values only; only `APP_*` keys (see the behavior table above). Every settings field appears, commented out when its default applies.

```dotenv
# Local development only. Copy to .env (git-ignored). Never put real secrets here.
# Every APP_* variable the settings class reads is listed; commented lines use the default.
APP_ENVIRONMENT=local
APP_LOG_LEVEL=DEBUG
# APP_REQUEST_TIMEOUT_S=10
# APP_KEY_VAULT_URL=https://<vault-name>.vault.azure.net
# APP_DATABASE_PASSWORD_SECRET_NAME=database-password
# Local-only stand-in for the Key Vault secret; use a throwaway value.
APP_DATABASE_PASSWORD=change-me-local-only
```

Sync test (checked on 2026-11-25: passes with the example above, fails when a line is removed). Place it next to the settings module or adjust the paths:

```python
"""Keep .env.example and the settings class in sync."""

import re
from pathlib import Path

from config import Settings

LINE = re.compile(r"^#?\s*(APP_[A-Z0-9_]+)=", re.MULTILINE)


def test_env_example_lists_every_setting() -> None:
    text = (Path(__file__).parent / ".env.example").read_text(encoding="utf-8")
    documented = set(LINE.findall(text))
    expected = {f"APP_{name.upper()}" for name in Settings.model_fields}
    assert documented == expected
```

### GitLab CI/CD variables versus Key Vault
Checked against docs.gitlab.com/ci/variables on 2026-11-25. Tier and version availability of individual options was not confirmed (F4): VERIFY: for the chosen GitLab tier and version.

| Question | GitLab CI/CD variable | Azure Key Vault |
|---|---|---|
| Intended use | Pipeline configuration and bootstrap values | Application and deployment secrets |
| Visible to anyone with project maintainer rights | Yes, in the settings UI unless the variable is hidden at creation (hiding cannot be added later) | No, RBAC-controlled and audited |
| Log masking | `Masked` replaces the value with `[MASKED]`, needs 8+ characters on one line, and GitLab states it is not a guaranteed protection | n/a (values are not printed by design) |
| Scope control | `Protected` limits to protected branches and tags; environment scope is a Premium or Ultimate feature for group variables | Per-vault RBAC, per-environment vaults |
| Rotation | Manual edit in the UI | Versions, expiry dates, near-expiry events |
| Standard | Non-secret config; secret only as a Protected and Masked bootstrap exception | **Default home of every secret** |

GitLab's own page says sensitive values belong in the UI rather than `.gitlab-ci.yml` and suggests connecting an external secrets manager. A job that needs Azure access should obtain a short-lived token through the ID-token federation described in [16-cicd-and-deployment.md](./16-cicd-and-deployment.md): the `id_tokens:` keyword gives the job a signed JWT in a variable, with a configurable `aud`, and its expiry follows the job timeout (five minutes if none is set). The Azure side needs a federated identity credential with issuer, subject and audience (Microsoft recommends `api://AzureADTokenExchange`; wildcards are not supported and up to 20 credentials fit on one app or managed identity). VERIFY: GitLab issuer and subject claim format for the chosen GitLab deployment, and the exact job commands; none were executed here.

### Rotation checklist per secret
1. Owner, purpose, expiry and period are set (tags) in the vault.
2. Two credentials overlap during rotation so consumers can switch (the Microsoft storage-key tutorial alternates primary and secondary keys across secret versions).
3. Consumers re-read within the cache time-to-live; no restart needed.
4. Old credential is revoked after the overlap window.
5. The rotation is recorded as evidence (who, when, which version, no value).

## Checklist
- [ ] No secret in code, history, image layers, build args or logs (gitleaks clean in pre-commit and CI).
- [ ] One vault per app per environment, RBAC model, soft delete and purge protection, private endpoint.
- [ ] Service has its own identity with `Key Vault Secrets User` only.
- [ ] Deployed code builds an explicit credential; `DefaultAzureCredential` appears only on the local path.
- [ ] `config.py` is the only reader of the environment; secrets are `SecretStr`; validator blocks plain-env secrets outside local.
- [ ] `.env.example` is committed, fake, contains only `APP_*` keys and matches the settings class.
- [ ] Every secret has an owner, expiry and rotation period; rotation tested.
- [ ] Pipelines use federation, not stored cloud credentials; any CI secret variable is Protected and Masked.
- [ ] Agent settings deny `.env*` reads; no real values in agent context.

## Common AI failure modes
| Failure | What to do instead |
|---|---|
| Hardcodes `api_key = "sk-..."` or a connection string in the example "just to make it run" | Read from settings; fake values only in `.env.example` |
| Uses `os.getenv` scattered across modules | One `config.py`, injected settings |
| Gives a secret field a default such as `"changeme"` | No default; validator enforces presence rules |
| Uses `DefaultAzureCredential()` everywhere, including production | Explicit managed or workload identity when deployed |
| Stores a service principal client secret in a GitLab variable | Federation with ID tokens |
| Passes secrets with `docker build --build-arg` or `ENV` | Runtime injection through the identity and vault |
| Logs `settings` or the request headers at debug level | Log secret names only; keep `SecretStr` |
| Puts a real-looking key in `.env.example` or a test | Obviously fake placeholders |
| Writes real values into `.env` on request | Refuse; use the vault and developer sign-in |
| "Fixes" a leaked secret by deleting the file in a new commit | Revoke and rotate, then clean history, then open an incident |

## Related docs
- [07-ignore-files.md](./07-ignore-files.md): `.env*` ignore rules, build-context rules
- [00-tech-stack.md](./00-tech-stack.md): pydantic-settings, Dockerfile, gitleaks
- [08-claude-md.md](./08-claude-md.md): agent permissions that protect secrets
- [02-security.md](./02-security.md): identity per agent, scanners
- [16-cicd-and-deployment.md](./16-cicd-and-deployment.md): GitLab ID tokens, Terraform, protected environments
- [10-logging-observability.md](./10-logging-observability.md): log redaction
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md): data classes and tests
- [18-reliability-and-operations.md](./18-reliability-and-operations.md): incident response
