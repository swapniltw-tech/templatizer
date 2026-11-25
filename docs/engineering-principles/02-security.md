# Security

> **Owner:** Head of Application Security · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** OWASP Top 10 for LLM Applications 2025 (genai.owasp.org/llm-top-10); OWASP Top 10 for Agentic Applications 2026 (genai.owasp.org); OSFI B-13 and B-10 (osfi-bsif.gc.ca); Microsoft Learn (Entra ID authentication for Azure OpenAI in Microsoft Foundry)

## Purpose
Baseline application, pipeline and AI-specific security rules for every service and agent. Principle order: **least privilege first**, then automated scanning, then LLM and agent threat controls. Related homes, linked not restated: secrets handling in [06-secrets-and-env.md](./06-secrets-and-env.md), data handling and redaction in [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md), pipeline mechanics in [16-cicd-and-deployment.md](./16-cicd-and-deployment.md), dependency policy in [20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md), tool manifests in [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md). OSFI B-13 is the regulatory anchor for the FRFI's own technology and cyber controls; mapping is completed in [12-governance-and-compliance.md](./12-governance-and-compliance.md).

## Pinned threat lists
| List | Version we follow | Confirmed against primary source |
|---|---|---|
| OWASP Top 10 for LLM Applications | **2025 edition** (LLM01:2025 to LLM10:2025). A **2026 edition** page exists on genai.owasp.org (dated 2026-08-03) but its entries were not readable at write time | 2025 IDs confirmed on genai.owasp.org. VERIFY: 2026 IDs and mapping; Application Security MUST decide when to move (SEC-026) |
| OWASP Top 10 for Agentic Applications | **2026 list** (released 2025-12-09), IDs ASI01-ASI10 | ASI01 Agent Goal Hijack, ASI02 Tool Misuse, ASI03 Identity and Privilege Abuse, ASI04 Agentic Supply Chain, ASI05 Unexpected Code Execution, ASI06 Memory and Context Poisoning, ASI07 Insecure Inter-Agent Communication, ASI08 Cascading Failures, ASI09 Human-Agent Trust Exploitation, ASI10 Rogue Agents. VERIFY: exact titles against the OWASP document (the OWASP resource page links to a download; titles above come from OWASP search snippets and secondary lists) |

LLM 2025 IDs used here: LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM03 Supply Chain, LLM04 Data and Model Poisoning, LLM05 Improper Output Handling, LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM08 Vector and Embedding Weaknesses, LLM09 Misinformation, LLM10 Unbounded Consumption.

## Threat-to-control map
| Threat | Primary controls (rule IDs) |
|---|---|
| LLM01 / ASI01 prompt injection, goal hijack | SEC-016, SEC-017, SEC-018, SEC-021 |
| LLM02 / LLM07 information and prompt disclosure | SEC-019, SEC-020; data rules in [13](./13-data-classification-and-privacy.md) |
| LLM03 / ASI04 supply chain | SEC-009, SEC-010, SEC-023 |
| LLM05 improper output handling | SEC-017 |
| LLM06 / ASI02 / ASI03 excessive agency, tool misuse, privilege abuse | SEC-001 to SEC-004, SEC-014, SEC-018 |
| ASI05 unexpected code execution | SEC-022 |
| ASI06 / LLM04 / LLM08 poisoning | SEC-024; retrieval rules in [19-rag-and-retrieval.md](./19-rag-and-retrieval.md) |
| ASI07 inter-agent trust | SEC-025 |
| ASI10 rogue agents, ASI08 cascades | SEC-003, SEC-015; kill switch in [18-reliability-and-operations.md](./18-reliability-and-operations.md) |
| LLM10 unbounded consumption | SEC-027; quotas in [15-llm-and-model-governance.md](./15-llm-and-model-governance.md) |
| ASI09 human-agent trust | SEC-014 |

## Rules

### Identity and least privilege
- **SEC-001** [MUST] [ci: terraform policy] Workloads MUST authenticate to Azure with managed identity or workload identity federation; shared keys, connection strings and long-lived service principal secrets MUST NOT be used.
- **SEC-002** [MUST] [ci: terraform policy] Each deployed service and each agent MUST have its own identity with RBAC roles scoped to the specific resource (no subscription-wide roles, no `Owner`/`Contributor` for runtime identities).
- **SEC-003** [MUST] [review] Each agent MUST run under one dedicated managed identity; two agents MUST NOT share an identity, and an agent MUST NOT inherit end-user credentials beyond the user's own permissions.
- **SEC-004** [MUST] [ci: terraform policy] Azure OpenAI / Foundry resources MUST disable local (key) authentication and use Entra ID with the narrowest inference role (for example Cognitive Services OpenAI User). VERIFY: the exact Terraform azurerm argument for disabling local auth on the resource version in use.
- **SEC-005** [MUST] [review] Authorization MUST be deny-by-default and enforced server-side on every endpoint and tool; authentication-only checks are not sufficient.
- **SEC-006** [SHOULD] [review] Human and CI access to production SHOULD be time-bound and approved (just-in-time), with no standing admin roles.

### Network isolation
- **SEC-007** [MUST] [ci: terraform policy] Data stores, Key Vault, and Foundry/Azure OpenAI resources used by Confidential or Restricted workloads MUST disable public network access and be reachable only through private endpoints.
- **SEC-008** [SHOULD] [runtime] Services SHOULD restrict egress to an allow-list (firewall or NSG rules); agents with web or tool access MUST NOT have unrestricted internet egress.

### Pipeline scanning
`ASSUMPTION:` scanner choice (GitLab built-in vs standalone tools) is open pending F4 (self-managed vs GitLab.com and licence tier). Required **capabilities** are fixed below; tools are examples. VERIFY: which GitLab scanners are available in our tier.

| Capability | Candidate tools | Gate |
|---|---|---|
| SAST | GitLab SAST, Semgrep, Bandit | Block on high/critical findings |
| Secret detection | GitLab Secret Detection, gitleaks (also pre-commit) | Block on any verified secret |
| SCA | GitLab Dependency Scanning, pip-audit | Block on high/critical with fix available |
| Container scan | GitLab Container Scanning, Trivy | Block on high/critical in final image |
| IaC scan | Checkov, Trivy config | Block on high/critical |
| DAST | OWASP ZAP (or GitLab DAST) against a deployed non-production environment | Block on high; weekly full scan |

- **SEC-009** [MUST] [ci: SAST, SCA, secret detection] Every MR pipeline MUST run SAST, SCA and secret detection and MUST fail on high or critical findings; findings MUST NOT be silenced by editing scanner config in the same MR without CODEOWNERS approval from Security.
- **SEC-010** [MUST] [ci: package-check] CI MUST verify every new Python dependency exists on the approved registry, is not a near-name of a popular package, and has history (age and release count) above the thresholds in [20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md), to block hallucinated or typosquatted ("slopsquatted") packages.
- **SEC-011** [MUST] [ci: container scan] Container images MUST be scanned before publish, built from a pinned base-image digest, run as non-root, and MUST NOT contain secrets or build tools in the final stage.
- **SEC-012** [MUST] [ci: IaC scan] Terraform changes MUST pass IaC scanning and the policy checks in SEC-002, SEC-004 and SEC-007 in the MR pipeline before merge.
- **SEC-013** [RETIRED] [ci: SBOM] Superseded by DEP-024 in [20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md), which owns SBOM generation and retention.

### Human control and agent actions
- **SEC-014** [MUST] [runtime] Any tool with side effects classified as `write`, `destructive` or `external` in its manifest MUST require human approval, unless the manifest's `requires_human_approval.conditions` records an approved exception for a defined low-risk, reversible condition that the agent's autonomy rung permits (see PRN-020 and the rung table in [04-engineering-principles.md](./04-engineering-principles.md); `destructive`, `external`, financial and restricted-data-exposing actions never qualify); the approval request MUST show the exact action and parameters, not a model-written summary.
- **SEC-015** [MUST] [runtime] Every agent MUST enforce per-run limits (steps, tokens, wall-clock time, spend) and stop when one is reached. The kill switch is owned by REL-024 in [18-reliability-and-operations.md](./18-reliability-and-operations.md).
- **SEC-016** [MUST] [test] Text from users, documents, web pages, tool results, retrieved chunks and other agents MUST be treated as untrusted data: it MUST NOT be placed in the system prompt, and it MUST NOT be able to widen tool permissions.
- **SEC-017** [MUST] [test] Model output MUST be validated against a schema and encoded or parameterised before use in SQL, shell, HTML, file paths, URLs or tool arguments; model output MUST NOT be executed directly.
- **SEC-018** [MUST] [ci: registry-check] An agent MUST bind only tools listed in its manifest allow-list at the pinned version; tool descriptions and schemas are reviewed as code (they are a prompt-injection surface).
- **SEC-019** [MUST] [review] System prompts MUST NOT contain secrets, credentials, or access rules that are the sole enforcement of a boundary; authorization is enforced in code.
- **SEC-020** [MUST] [test] Model responses MUST NOT echo secrets or Restricted data; output filters and tests with synthetic canary strings MUST confirm this for each release.
- **SEC-021** [MUST] [test] Each Tier 1 and Tier 2 system MUST pass the prompt-injection and goal-hijack red-team suite defined in [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md) before release and on each model, prompt or tool change.
- **SEC-022** [MUST] [runtime] Code generated or supplied at runtime MUST execute only in an isolated sandbox (no secrets, no production network, CPU/memory/time limits, ephemeral filesystem) and MUST NOT run in the service process.
- **SEC-023** [MUST] [review] MCP servers and third-party tool servers MUST be vetted and approved (owner, source review, pinned version, tool list hash) before use, and MUST be listed in the registry; unvetted servers MUST NOT appear in `.mcp.json`. See [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md). VERIFY: the pinned MCP specification version (F13).
- **SEC-024** [MUST] [review] Agent memory and retrieval stores MUST be write-controlled (authenticated writers, provenance recorded) and scoped per user or tenant; memory content MUST be treated as untrusted on read.
- **SEC-025** [MUST] [runtime] Agent-to-agent calls MUST be authenticated, authorised against the registry and treated as untrusted input; one agent's output MUST NOT grant another agent more permissions. VERIFY: A2A agent-card guidance is unresearched (F13).
- **SEC-026** [MUST] [review] Application Security MUST review the pinned OWASP list editions at least every six months and record the decision (stay or move) in an ADR; threat models MUST cite the pinned edition's IDs.
- **SEC-027** [MUST] [runtime] Every LLM-facing endpoint MUST enforce per-caller rate limits, max input and output tokens, and budget alerts, to bound abuse and cost (LLM10).

### AI coding agents (supply chain of our own code)
- **SEC-028** [MUST] [review] AI coding agents MUST NOT hold production credentials, run `terraform apply`, approve their own MRs, or alter pipeline, scanner or permission configuration without a human CODEOWNER; permissions are defined in [01-codebase-practices.md](./01-codebase-practices.md).
- **SEC-029** [SHOULD] [review] Security-sensitive changes (authn/authz, crypto, IaC, pipeline files) SHOULD be reviewed by a human with security training even when an automated reviewer approves.

## Example: keyless Foundry client (placeholders only)
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential  # local dev; use an explicit managed/workload identity credential when deployed (FDY-004)

# VERIFY: constructor arguments and get_openai_client() against current Microsoft Learn for azure-ai-projects 2.x.
project = AIProjectClient(
    endpoint="https://<resource>.services.ai.azure.com/api/projects/<project>",
    credential=DefaultAzureCredential(),  # Entra token; no static API key
)
client = project.get_openai_client()
reply = client.chat.completions.create(
    model="<chat-deployment>",  # deployment name, not a model name
    messages=[{"role": "user", "content": "ping"}],
)
```
Call path and SDK choice are owned by [23-azure-foundry-standards.md](./23-azure-foundry-standards.md) (FDY-001). Microsoft Learn states that Entra authentication needs a custom subdomain, and that role assignments can take up to five minutes to apply (VERIFY).

## Example: GitLab CI security stage outline
```yaml
# .gitlab-ci.yml (outline; VERIFY template names against current GitLab docs and our tier)
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml
```

## Checklist
- [ ] Managed identity per service and per agent; no keys or connection strings
- [ ] Foundry local auth disabled; private endpoints; public access off
- [ ] SAST, SCA, secrets, container, IaC scans green; DAST scheduled
- [ ] New dependencies verified against hallucination/typosquat check
- [ ] SBOM generated and retained
- [ ] Side-effect tools require human approval; kill switch tested
- [ ] Untrusted-input handling and output validation have tests
- [ ] Red-team suite run on this change
- [ ] MCP servers and tools in registry, pinned
- [ ] Threat model cites pinned OWASP editions

## Common AI failure modes
- Using an account key or connection string "just to get it working".
- Granting `Contributor` to fix a 403 instead of the narrow role.
- Adding a package the model invented, or a near-name of a real one.
- Concatenating retrieved text or tool output into the system prompt.
- Passing model output to `eval`, `subprocess` or raw SQL.
- Having the agent summarise a destructive action for approval instead of showing the exact call.
- Disabling a failing scanner rule or test in the same MR.
- Putting authorization rules in the prompt rather than in code.
- Citing OWASP IDs from memory or mixing 2025 and 2026 editions.

## Related docs
- [12-governance-and-compliance.md](./12-governance-and-compliance.md)
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)
- [06-secrets-and-env.md](./06-secrets-and-env.md)
- [16-cicd-and-deployment.md](./16-cicd-and-deployment.md)
- [20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md)
- [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md)
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md)
- [23-azure-foundry-standards.md](./23-azure-foundry-standards.md)
- [01-codebase-practices.md](./01-codebase-practices.md)
