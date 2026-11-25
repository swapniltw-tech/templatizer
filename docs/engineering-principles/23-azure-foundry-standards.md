# Microsoft Foundry Standards

> **Owner:** Platform Engineering lead with AI governance · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview), [Guardrails overview](https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview), [Deployment types](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types), [Model versions](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/model-versions), [Model lifecycle and retirements](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements), [Quotas and limits](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/quotas-limits), [Agent identity](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity), [Agent tracing](https://learn.microsoft.com/en-us/azure/foundry/observability/concepts/trace-agent-concept), [azure-ai-projects on PyPI](https://pypi.org/project/azure-ai-projects/)

## Purpose
Microsoft Foundry (formerly Azure AI Foundry; the portal and some pages still show old names) is the only approved LLM platform. This doc owns **platform mechanics**: SDK, agent types, identity, networking, guardrails, deployment types and residency, version and retirement handling, quota, tracing. Policy on which models are approved, prompts, fallback and budgets lives in [15-llm-and-model-governance.md](./15-llm-and-model-governance.md). Tool and agent manifests live in [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md).

Foundry changes quickly. Learn pages read for this revision were dated between July and November 2026. Anything marked `VERIFY:` was not confirmed on a primary page. Open item F11 (feature status and preview policy) and F2 (approved models) apply throughout; code uses placeholder names such as `<chat-deployment>`.

## Rules

### SDK and access
- **FDY-001** [MUST] [review] LLM calls MUST go through the Foundry project endpoint (`https://<resource>.services.ai.azure.com/api/projects/<project>`) using the `azure-ai-projects` Python SDK. Any other LLM provider or SDK path needs a waiver ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)) and vendor approval ([12-governance-and-compliance.md](./12-governance-and-compliance.md)).
- **FDY-002** [MUST] [ci: lockfile check] `azure-ai-projects` MUST be pinned to an exact version in the lockfile. Learn requires `>=2.3.0` (a floor, not a recommendation); PyPI listed 2.11.0 released 2026-11-13 (VERIFY: re-check at each bump). 2.x is incompatible with 1.x. VERIFY: whether the separate `azure-ai-agents` Python package is fully unnecessary; the 2.x Python quickstart installs only `azure-ai-projects`.
- **FDY-003** [MUST] [review] Preview features MUST NOT be used in production without a waiver. In the SDK, preview surfaces are reached with `allow_preview=True` or `.beta` sub-clients; REST preview opt-ins use a `Foundry-Features` header. Code review MUST reject these unless a waiver id is cited.
- **FDY-004** [MUST] [ci: gitleaks] Authentication MUST use Microsoft Entra (managed identity or workload identity in deployed environments, `az login` locally); API keys MUST NOT be used or stored ([06-secrets-and-env.md](./06-secrets-and-env.md)). Deployed code SHOULD use an explicit credential rather than the default credential chain.
- **FDY-005** [MUST] [lint] Deployment and agent names MUST come from configuration (placeholders such as `<chat-deployment>` in docs and examples), never hard-coded model names in code.
- **FDY-006** [SHOULD] [review] All model calls SHOULD go through one adapter module that applies timeouts, retries, redaction, telemetry and output validation ([09-structure-and-format.md](./09-structure-and-format.md)).
- **FDY-007** [MUST] [review] Clients MUST set explicit timeouts below the documented ceilings (streaming non-reasoning calls up to 60 seconds; reasoning and non-streaming up to 29 minutes) and MUST retry HTTP 429 with exponential backoff honoring `Retry-After` ([18-reliability-and-operations.md](./18-reliability-and-operations.md)).

### Agent types, identity and tools
- **FDY-008** [SHOULD] [review] Agent type SHOULD follow [05-decision-playbook.md](./05-decision-playbook.md): a prompt agent when no custom runtime code is needed; a hosted agent when the agent calls custom code or needs custom orchestration; the Responses API directly (ephemeral agent) when the definition ships with the application. Voice-based prompt agents are for real-time voice only.
- **FDY-009** [MUST] [ci] Production agent definitions MUST live in Git and be published by CI (`create_version`), never authored by hand in the portal. Each published version MUST map to a manifest ([25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md)).
- **FDY-010** [MUST] [review] Each agent MUST use its own Entra agent identity. New agents get their own blueprint and identity with no permissions; grants MUST be explicit, least privilege and scoped to the narrowest resource. The legacy shared project identity MUST NOT be used for new agents.
- **FDY-011** [MUST] [review] On-behalf-of-user access for agent tools is documented as preview; using it in production MUST have a waiver and a compensating control (for example the tool re-checks the user's entitlement).
- **FDY-012** [MUST] [review] Built-in Foundry roles (Foundry User, Foundry Owner, Foundry Account Owner, Foundry Project Manager; formerly Azure AI User and so on, role ids unchanged) MUST be assigned at the narrowest scope; humans MUST NOT hold Owner roles on production projects day to day.
- **FDY-013** [SHOULD] [review] Tools SHOULD be provided through a Foundry Toolbox when the platform decision (F12) is made, with toolbox versions promoted to default only through a merge request. Toolbox Skills are preview and fall under FDY-003.
- **FDY-014** [MUST] [review] Orchestration frameworks are not the default. If one is adopted (for example Microsoft Agent Framework, LangGraph), versions MUST be pinned and the choice recorded in an ADR. VERIFY: Agent Framework class renames reported for 2026 (`ChatAgent` to `Agent`, `@ai_function` to `@tool`) before writing code from memory.
- **FDY-015** [MUST] [review] Agent-to-agent endpoints MUST use A2A v1.0 (generally available); A2A v0.3 is preview and falls under FDY-003.

### Networking
- **FDY-016** [MUST] [review] Regulated workloads MUST use private networking: prompt agents with private networking, hosted agents with bring-your-own virtual network, and public network access to the Foundry resource disabled. VERIFY: exact resource settings and Terraform attributes before writing IaC.
- **FDY-017** [MUST] [review] The networking decision for a hosted agent MUST be made at creation time. VERIFY: a third-party guide says network injection cannot be added afterwards; Learn pages read did not confirm this.
- **FDY-018** [MUST] [review] Hosted agents MUST have network egress controls configured with an allow-list. Egress controls are generally available except Transform rules, which are preview; Azure Policy governance for egress guardrails applies to hosted agents only.

### Guardrails
- **FDY-019** [MUST] [ci: terraform plan check] Every agent MUST have an explicit, named guardrail assigned; because agent guardrails are preview, FDY-021 and FDY-003 apply (waiver plus compensating controls). An agent's guardrail fully overrides its model's guardrail; an agent with none inherits the model deployment's guardrail, which is `Microsoft.DefaultV2` by default. VERIFY: Terraform and SDK attribute for assigning a guardrail to an agent.
- **FDY-020** [MUST] [review] Guardrails MUST be treated as defense in depth, not the sole control. Input validation, output schema validation, tool allow-lists and human approval remain required ([02-security.md](./02-security.md)).
- **FDY-021** [MUST] [review] Agent guardrails are documented as preview, including the tool-call and tool-response intervention points. Their use is a preview feature under FDY-003: it MUST be recorded in the agent manifest with compensating controls AND a waiver ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)). Spotlighting and groundedness controls do not apply to agents.
- **FDY-022** [SHOULD] [review] Blocking levels SHOULD be chosen by risk tier. Content-risk output filtering MUST NOT be turned off; that option exists only for customers approved by Microsoft and requires governance approval.
- **FDY-023** [SHOULD] [review] Groundedness detection (preview) is documented as retiring on 2027-04-30, so grounding checks SHOULD be owned by evals ([14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md)) and not by this feature.

### Deployments, residency and versions
- **FDY-024** [MUST] [ci: azure policy] For workloads that process personal or restricted data, deployments MUST use the `Standard` or `ProvisionedManaged` deployment types only. `GlobalStandard`, `GlobalProvisionedManaged`, `GlobalBatch`, `DataZone*` and `DeveloperTier` MUST be denied by Azure Policy on `sku.name` for those subscriptions. Learn states Global types may process in any Azure region; Data Zones exist only for US, EU and APAC, so there is no Canadian data zone; `DeveloperTier` has no residency guarantee.
- **FDY-025** [MUST] [review] The PIA MUST address processing location and foreign-access risk for the chosen deployment type ([13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)). ASSUMPTION: Canada Central is the primary region; VERIFY: which approved models are offered as `Standard` in a Canadian region, since geography-based types launch last and have no guaranteed availability date.
- **FDY-026** [MUST] [review] Batch processing exists only as `GlobalBatch` and `DataZoneBatch`, so batch pipelines MUST NOT send personal information to it; use synchronous `Standard` calls or non-personal data ([26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md) case 24).
- **FDY-027** [MUST] [review] Instant model access (documented as preview, calls a model without a deployment) MUST NOT be used in production because it bypasses deployment, version and policy controls.
- **FDY-028** [MUST] [ci: terraform plan check] Deployments MUST be created by Terraform, one per environment and purpose, with the model version pinned and `versionUpgradeOption` set explicitly. `OnceNewDefaultVersionAvailable` MUST NOT be used in production. Workloads in the medium and high risk tiers MUST use `NoAutoUpgrade` and migrate on schedule; `OnceCurrentVersionExpired` is allowed only for low risk with passing evals. VERIFY: Terraform attribute name for the upgrade option.
- **FDY-029** [MUST] [ci: scheduled job] A scheduled job MUST read each deployed model's `lifecycleStatus` and `deprecation` dates from the Models API and alert the owner at 120 days before retirement. Migration MUST start at least 90 days before retirement because dates are not extendable, `NoAutoUpgrade` deployments stop at retirement (inference returns `410 Gone`), and provisioned deployments are never auto-upgraded. Process is owned by [15-llm-and-model-governance.md](./15-llm-and-model-governance.md).

### Quota and cost
- **FDY-030** [MUST] [review] Quota MUST NOT be used as the cost control. Budgets and anomaly alerts are required ([15-llm-and-model-governance.md](./15-llm-and-model-governance.md), [18-reliability-and-operations.md](./18-reliability-and-operations.md)).
- **FDY-031** [SHOULD] [manual] Teams SHOULD check the quota scope per model in the Foundry portal (subscription-level pools for onboarded models; per-region otherwise) and request increases before launch. Subscription quota tiers can upgrade automatically; opting out is preview.

### Tracing and evaluation
- **FDY-032** [MUST] [runtime] Tracing MUST be enabled to the project's Application Insights resource. Tracing is documented as generally available for prompt, hosted and external agents; workflow agents are preview. GenAI semantic conventions are Development status, so attribute names MAY change ([10-logging-observability.md](./10-logging-observability.md)).
- **FDY-033** [MUST] [runtime] Prompt, response and tool-argument content in traces MUST be redacted per [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md); content that cannot be redacted MUST go to the restricted table with limited access. Avoid duplicate instrumentation of the same call. VERIFY: content-capture setting names for the Python SDK.
- **FDY-034** [SHOULD] [ci: make eval] CI evals SHOULD run in the team harness; Foundry evaluations SHOULD be used for production monitoring on sampled traffic, with results retained as audit evidence ([14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md)). VERIFY: Foundry evaluations GA status.

### Governance of features
- **FDY-035** [MUST] [review] Each service MUST list the Foundry preview features it uses in its ADR with the waiver id; the platform team MUST review the list at each SDK bump.
- **FDY-036** [MUST] [review] Models from non-OpenAI publishers in the Foundry catalog MUST NOT be used until the approved list in [15-llm-and-model-governance.md](./15-llm-and-model-governance.md) names them. ASSUMPTION: unresolved item F2.

## SDK reference example
Placeholders only; confirm names against the pinned SDK version.
```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import ManagedIdentityCredential  # deployed; locally use an Azure CLI credential

project = AIProjectClient(
    endpoint="https://<resource>.services.ai.azure.com/api/projects/<project>",
    credential=ManagedIdentityCredential(),
)

agent = project.agents.create_version(
    agent_name="<agent-name>",
    definition=PromptAgentDefinition(
        model="<chat-deployment>",          # deployment name from config, not a model name
        instructions=load_prompt("system"),  # versioned prompt file, hash-checked
    ),
)

openai = project.get_openai_client(agent_name="<agent-name>")
conversation = openai.conversations.create()
response = openai.responses.create(conversation=conversation.id, input="<user-input>")
```
Calls above (`create_version`, `PromptAgentDefinition`, `get_openai_client`, `conversations.create`, `responses.create`) appear in the Learn prompt-agent quickstart. VERIFY: constructor arguments for credential classes in your pinned version.

## Deployment types
| SKU | Processing location | Allowed for personal data |
|---|---|---|
| `Standard` | Within the customer-specified Azure geography | Yes, subject to PIA |
| `ProvisionedManaged` | Within the customer-specified Azure geography | Yes, subject to PIA |
| `DataZoneStandard`, `DataZoneProvisionedManaged`, `DataZoneBatch` | Within a US, EU or APAC data zone | No |
| `GlobalStandard`, `GlobalProvisionedManaged`, `GlobalBatch` | Any Azure region | No |
| `DeveloperTier` | Any Azure region; 24-hour lifetime; no SLA | No |

Learn recommends starting with Global Standard for general workloads; that advice does not apply here because of residency. Standard types may also route between regions within the geography "for operational purposes".

Azure Policy sketch to deny a SKU (Learn shows the `if` block; the `then` effect is added here). VERIFY: test in a non-production subscription before assigning.
```json
{
  "mode": "All",
  "policyRule": {
    "if": {
      "allOf": [
        {"field": "type", "equals": "Microsoft.CognitiveServices/accounts/deployments"},
        {"field": "Microsoft.CognitiveServices/accounts/deployments/sku.name",
         "in": ["GlobalStandard", "GlobalProvisionedManaged", "GlobalBatch",
                "DataZoneStandard", "DataZoneProvisionedManaged", "DataZoneBatch", "DeveloperTier"]}
      ]
    },
    "then": {"effect": "deny"}
  }
}
```

## Model lifecycle facts used by the rules
| Fact | Source page |
|---|---|
| Stages: Preview, GA, Legacy (optional), Deprecated (existing customers only), Retired (`410 Gone`) | Model lifecycle and support policy |
| GA models: 18-month lifecycle; Anthropic, DeepSeek, Fireworks and Mistral GA models: 12 months | same |
| Retirement notice: at least 60 days (GA), at least 30 days (preview); retirement dates are not extendable | same |
| Official replacement named about 90 to 120 days before retirement | same |
| Auto-upgrade applies to Global Standard, Data Zone Standard and Standard; provisioned deployments are not auto-upgraded | same |
| Upgrade option values: `OnceNewDefaultVersionAvailable`, `OnceCurrentVersionExpired`, `NoAutoUpgrade` | same (FAQ) |
| Preview models are force-upgraded or retired; no option to stay | same |
| Azure notifies subscription owners by email and Service Health; select the `Azure OpenAI Service` name in alerts | same |

## Feature status register
Status as read from Learn on the verification date. Re-check at each SDK bump (F11).
| Feature | Status stated on Learn | Rule |
|---|---|---|
| Prompt agents, voice-based prompt agents | Voice agents GA, with some features preview | FDY-003 |
| Hosted agents | VERIFY: GA status not stated on the overview page | FDY-003 until confirmed |
| Agent guardrails (content safety on agents) | Preview | FDY-021 |
| Guardrail tool-call and tool-response intervention points | Preview | FDY-021 |
| Toolbox | VERIFY: GA status not stated; Skills in Toolbox preview | FDY-013 |
| Tracing | GA for prompt, hosted and external agents; workflow agents preview | FDY-032 |
| Hosted-agent egress controls | GA except Transform rules (preview) | FDY-018 |
| Instant model access | Preview | FDY-027 |
| Portal quota-increase requests; quota tier opt-out | Preview | FDY-031 |
| Agent identity acting on behalf of user | Preview | FDY-011 |
| Copilot harness for prompt agents | Preview | FDY-003 |
| Old hosted-agent preview backend, end of support 2026-08-20 | VERIFY: date not found on pages read; confirm nothing relies on it | FDY-035 |

## Checklist
- [ ] `azure-ai-projects` pinned exactly; no key-based auth; names come from config.
- [ ] No preview feature in production without a waiver id in the ADR.
- [ ] Each agent has its own identity with explicit least-privilege grants.
- [ ] Each agent has an explicit named guardrail; compensating controls recorded for preview parts.
- [ ] Deployment SKUs are `Standard` or `ProvisionedManaged` for personal data; Azure Policy deny is assigned.
- [ ] `versionUpgradeOption` set explicitly; retirement alert job exists with a named owner.
- [ ] Private networking and egress allow-list configured; hosted agent networking decided at creation.
- [ ] Tracing on, content redacted; evals wired in CI and production sampling.
- [ ] Budget alerts exist; quota is not the only control.

## Common AI failure modes
- Copying Learn samples that hard-code a real model name and an API key or default credential chain.
- Choosing Global Standard because the docs say "start with Global Standard", breaking residency.
- Assuming the agent inherits the model's guardrail and then assigning a weaker agent guardrail that overrides it.
- Writing 1.x-era code (`create_agent`, separate agents package) against the 2.x SDK, or mixing the two. VERIFY: `create_agent` removal in your pinned version.
- Leaving `versionUpgradeOption` at its default so a new default model version arrives without evals.
- Setting `allow_preview=True` to make an example work and shipping it.
- Treating quota as a spending limit.
- Granting the shared project identity broad roles because new agent identities start with none.
- Inventing Terraform attribute names for Foundry resources.

## Related docs
- [15-llm-and-model-governance.md](./15-llm-and-model-governance.md): approved models, pinning policy, prompts, fallback, budgets.
- [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md): manifests, Toolbox as runtime catalog.
- [02-security.md](./02-security.md): agent and LLM threats.
- [06-secrets-and-env.md](./06-secrets-and-env.md): identity and secrets.
- [10-logging-observability.md](./10-logging-observability.md): tracing and redaction.
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md): PIA, residency.
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md): evals.
- [16-cicd-and-deployment.md](./16-cicd-and-deployment.md): Terraform and pipeline.
- [18-reliability-and-operations.md](./18-reliability-and-operations.md): retries, quota handling, kill switch.
- [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md): preview-feature waivers.

## Sources
- Foundry Agent Service overview: https://learn.microsoft.com/en-us/azure/foundry/agents/overview
- Guardrails overview: https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview
- Deployment types: https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types
- Model versioning: https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/model-versions
- Model lifecycle and support policy: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
- Quotas and limits: https://learn.microsoft.com/en-us/azure/foundry/foundry-models/quotas-limits
- Prompt agent quickstart: https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent
- Agent identity: https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity
- Agent tracing: https://learn.microsoft.com/en-us/azure/foundry/observability/concepts/trace-agent-concept
