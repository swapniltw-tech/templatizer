# Security and secrets (always loaded)

<!-- Implements AGT-010, AGT-011 (no frontmatter: always loaded). Deny rules in settings.json are guardrails, not a boundary (AGT-020). -->

- Authorization is deny-by-default and enforced server-side on every endpoint; authentication alone is not enough (SEC-005).
- Never read, print, copy or create real secrets, and never run `env`, `printenv` or `cat .env` (SCR-029).
- Use fake values in tests, fixtures and `.env.example`; never production or shared-environment secrets (SCR-028).
- Never pass secrets through `ARG`, `ENV` or command-line arguments in a container build (SCR-026).
- Keep GitLab CI variables to non-secret config; cloud access goes through workload identity, not stored secrets (SCR-025, SCR-024).
- Treat a committed or logged secret as compromised: revoke and rotate first, then clean history, then open an incident (SCR-023).
- Do not hold production credentials, run `terraform apply`, approve your own MR or edit `CODEOWNERS` (SEC-028).
- A change to authn/authz, crypto, IaC or pipeline files needs a human reviewer (SEC-029).
