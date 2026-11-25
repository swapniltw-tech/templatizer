# AI Tool and Agent Registry

> **Owner:** Platform Engineering lead with AI governance · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** [MCP specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28), [MCP tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools), [MCP key changes](https://modelcontextprotocol.io/specification/2026-07-28/changelog), [Foundry Toolbox](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/toolbox-overview), [Foundry agent identity](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity), [A2A specification](https://a2a-protocol.org/latest/specification/), [JSON Schema 2020-12](https://json-schema.org/draft/2020-12)

## Purpose
Every AI tool (an action a model can invoke) and every agent is a **registered, versioned, spec'd artifact** with an owner and an approval state. This doc owns the manifest schemas, the lifecycle, and the rules for how agents discover and bind tools. **Discovery is not permission:** a tool being listed does not make it callable by every agent.

Scope split: policy on models and prompts is in [15-llm-and-model-governance.md](./15-llm-and-model-governance.md); Foundry platform mechanics (Toolbox, identity, guardrails) are in [23-azure-foundry-standards.md](./23-azure-foundry-standards.md); eval content is in [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md); threat model is in [02-security.md](./02-security.md). This doc defines the artifacts those docs refer to.

Registry files live in the repo (`registry/schemas/`, `registry/tools/`, `registry/agents/`; see [09-structure-and-format.md](./09-structure-and-format.md)). The schemas below are the contract; `make registry-check` enforces them.

## Rules

### Registration and binding
- **REG-001** [MUST] [ci: make registry-check] Every tool an agent can call (MCP, OpenAPI, function, or Foundry built-in) MUST have a manifest in `registry/tools/`; a tool without a manifest MUST fail CI.
- **REG-002** [MUST] [ci: make registry-check] Every agent MUST have a manifest in `registry/agents/`; an agent without a manifest MUST NOT be deployed.
- **REG-003** [MUST] [review] The Git manifests are the source of truth. Runtime catalogs (Foundry Toolbox, tool catalog, Entra Agent Registry) MUST be populated from them by CI and MUST NOT be edited by hand. ASSUMPTION: this registry-platform choice is open item F12.
- **REG-004** [MUST] [ci: make registry-check] Manifests MUST validate against the JSON Schemas in this doc using a validator with format checking enabled, and the embedded `input_schema`, `output_schema` and `error_schema` MUST themselves be valid JSON Schema 2020-12.
- **REG-005** [MUST] [runtime] An agent MUST bind only the tools in its manifest `allowed_tools`, resolved by tool `id` and version range, and only tools whose status is `approved`. Everything else MUST be refused at tool dispatch, not by prompt wording.
- **REG-006** [MUST] [ci: make registry-check] Every `allowed_tools` entry MUST resolve to an existing manifest whose version satisfies the range; unresolved or non-approved references MUST fail CI.
- **REG-007** [MUST] [runtime] Tools that appear on a server after approval MUST NOT be bound until they have a manifest. Agents MUST ignore unregistered tools returned by a tool listing.

### Lifecycle and change control
- **REG-008** [MUST] [review] Tools and agents MUST move through `draft -> evaluated -> approved -> deprecated -> retired`. Approval MUST be recorded by a reviewer other than the author; an AI agent MUST NOT approve its own manifest.
- **REG-009** [MUST] [ci: make registry-check] Any change to a tool's `description`, `input_schema`, `output_schema`, `error_schema`, `auth`, `limits` or `side_effects` MUST bump `version` (semantic versioning; breaking schema changes bump major) and MUST re-run the tool's evals before `status` returns to `approved`.
- **REG-010** [MUST] [review] `registry/` MUST be covered by CODEOWNERS with the tool owner and a security reviewer for `high` risk tools.
- **REG-011** [MUST] [ci: make registry-check] A `deprecated` manifest MUST carry a deprecation date and, where one exists, a replacement id; CI MUST fail when an `approved` agent still references a `retired` tool. ASSUMPTION: notice period between deprecated and retired is set by AI governance (F1).
- **REG-012** [MUST] [manual] The registry MUST be exported to the model and agent inventory defined in [12-governance-and-compliance.md](./12-governance-and-compliance.md); every manifest MUST carry an `inventory_id` and the export MUST be retained as audit evidence.

### Tool manifests and descriptions
- **REG-013** [MUST] [review] Tool descriptions are model-visible text and a prompt-injection surface. They MUST be reviewed like code, MUST describe only what the tool does and its inputs, and MUST NOT contain instructions to the model about other tools or about ignoring rules.
- **REG-014** [MUST] [review] `side_effects` and `risk_tier` MUST be assigned by the tool owner and reviewer. They MUST NOT be derived from server-reported MCP annotations, which the MCP specification says clients must treat as untrusted unless the server is trusted.
- **REG-015** [MUST] [ci: make registry-check] Tools with `side_effects` of `destructive`, or `risk_tier` of `high`, MUST set `requires_human_approval.required` to true with no exception conditions. Tools with `write` side effects follow SEC-014 (approval unless a documented low-risk condition applies). Approval MUST be enforced in code at dispatch ([04-engineering-principles.md](./04-engineering-principles.md) owns the principle).
- **REG-016** [MUST] [ci: make registry-check] Tools with `side_effects` of `write`, `destructive` or `external` MUST declare `idempotent` and, when true, MUST accept an idempotency key (see [17-api-and-contracts.md](./17-api-and-contracts.md)).
- **REG-017** [MUST] [review] Each tool MUST define `limits` (rate, timeout, payload size) and the runtime MUST enforce them; cost limits SHOULD be set where the tool incurs per-call cost.
- **REG-018** [MUST] [review] Tool `auth` MUST use the calling agent's own identity (or on-behalf-of-user where the user's permissions must apply), with the least-privilege role and scopes listed. Tools MUST NOT use shared service credentials ([06-secrets-and-env.md](./06-secrets-and-env.md)).
- **REG-019** [MUST] [ci: make registry-check] An agent's `data_classes` MUST NOT include a class higher than the `data_classification_max` of any tool it can call (classes: [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)).
- **REG-020** [MUST] [review] Each tool MUST ship `docs` with usage, failure modes, at least one example and a runbook link before reaching `evaluated`.

### MCP pinning and drift
- **REG-021** [MUST] [ci: make registry-check] MCP-backed tools MUST record the MCP server `pinned_version`, the protocol `spec_version` (currently 2026-07-28; VERIFY: re-check on modelcontextprotocol.io before each pin change) and `tool_definition_sha256`; the MCP client SDK version MUST be pinned in the lockfile ([20-dependencies-and-licensing.md](./20-dependencies-and-licensing.md)).
- **REG-022** [MUST] [ci: make registry-check] `tool_definition_sha256` MUST be the SHA-256 of the canonical JSON (sorted keys, no whitespace, UTF-8) of the `tools/list` entry as returned to the agent's own identity, because the MCP list MAY vary by the authorization presented. CI MUST fail when the live server's hash differs from the manifest.
- **REG-023** [MUST] [runtime] The runtime MUST re-check the hash when it binds a tool and when a cached tool list expires (`ttlMs`) or a list-changed notification arrives, and MUST refuse to bind on mismatch.
- **REG-024** [SHOULD] [ci: scheduled job] A scheduled pipeline SHOULD run the drift check daily against each registered MCP server and open an issue for the tool owner on mismatch.
- **REG-025** [MUST] [review] New registrations MUST NOT depend on MCP features the specification lists as deprecated (Roots, Sampling, Logging, HTTP+SSE transport, Dynamic Client Registration) without a waiver ([21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md)).

### Evals
- **REG-026** [MUST] [ci: make eval] Each tool and each agent MUST reference an eval dataset and thresholds ([14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md)); `approved` status MUST require `last_run` and `result_link`, and evals MUST re-run on any schema, prompt or model change.

### Agent manifests
- **REG-027** [MUST] [ci: make registry-check] Agent manifests MUST declare purpose and non-goals, autonomy rung, allowed tools, model deployment and model version, data classes, eval suite and thresholds, guardrail policy, human-approval points, kill switch, runbook and inventory id.
- **REG-028** [MUST] [ci: make registry-check] `model.model_version` MUST be an explicit version, never a floating alias, and CI MUST compare it with the version actually deployed by Terraform ([15-llm-and-model-governance.md](./15-llm-and-model-governance.md)).
- **REG-029** [MUST] [ci: make registry-check] Prompts MUST be listed by path and SHA-256 of the file bytes. The prompt loader MUST verify the hash at startup and fail closed on mismatch.
- **REG-030** [MUST] [ci: make registry-check] `high` risk agents MUST NOT exceed the `propose` autonomy rung without a waiver. The `autonomy_rung` enum uses the canonical identifiers defined in [04-engineering-principles.md](./04-engineering-principles.md).
- **REG-031** [MUST] [test] The kill switch MUST be exercised in a pre-production test before an agent reaches `approved`, and the owner role MUST be on call ([18-reliability-and-operations.md](./18-reliability-and-operations.md)).

### Inter-agent calls
- **REG-032** [MUST] [runtime] Calls between agents (A2A, agent-as-tool, or Foundry A2A tool) MUST go through the registry like any tool, and the remote agent's output MUST be treated as untrusted input.
- **REG-033** [SHOULD] [review] External agents SHOULD be consumed only when their Agent Card is verified (signature check where the card is signed; the A2A specification makes signing optional) and the endpoint is allow-listed in the agent manifest.

### Observability
- **REG-034** [MUST] [review] Tool calls MUST emit the span and metrics named in the manifest `observability` block, with arguments and results redacted per [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md) and [10-logging-observability.md](./10-logging-observability.md).
- **REG-035** [MUST] [ci: make registry-check] A fixed workflow that calls an LLM MUST also have an agent manifest (state `workflow` in `purpose`, list its fixed tool set, and declare the rung that matches its side effects); "it is not an agent" is not an exemption from registration, evals or the kill switch.

## Discovery versus permission
| Layer | What it is | Who can see it | What it grants |
|---|---|---|---|
| Git `registry/` | Manifests, schemas, evals refs; source of truth | Engineers, reviewers | Nothing at runtime |
| Foundry tool catalog / Toolbox | Runtime bundle of tools behind one MCP-compatible endpoint with central auth, guardrails on tool input and output, versioning | Projects with access | Tool availability for agents pointed at the toolbox |
| Entra agent identity + RBAC | Per-agent identity; starts with no permissions | Entra admins | The actual downstream access |
| Agent manifest `allowed_tools` | Per-agent allow-list by id and version range | Reviewers | Which approved tools the agent may bind |

Rules of thumb: listing a tool tells an agent it exists; the allow-list decides if it may bind; RBAC decides if the call succeeds; human approval decides if a risky call proceeds. All four must agree.

### Findings from primary sources (corrections to earlier planning notes)
| Topic | Finding | Status |
|---|---|---|
| MCP revision | Latest revision is **2026-07-28**; previous is 2025-11-25. It is stateless: no `initialize` handshake, no `Mcp-Session-Id`; every request carries protocol version and capabilities in `_meta`; servers implement `server/discover`. | Confirmed on modelcontextprotocol.io |
| Deprecated | Roots, Sampling, Logging, HTTP+SSE transport and Dynamic Client Registration (in favour of Client ID Metadata Documents) are Deprecated; minimum 12-month window. | Confirmed |
| Tool list | `tools/list` MAY vary by authorization but not per connection; SHOULD be deterministic order; results carry `ttlMs` and `cacheScope`. | Confirmed |
| Schema dialect | `inputSchema` and `outputSchema` default to JSON Schema 2020-12 when `$schema` is absent; `inputSchema` MUST be an object schema. | Confirmed |
| Annotations | Spec says clients MUST treat tool annotations as untrusted unless from a trusted server. Exact `ToolAnnotations` field names and defaults for this revision. | VERIFY: field list not confirmed for 2026-07-28 |
| Tasks | Long-running tasks moved to an official extension (`io.modelcontextprotocol/tasks`). | Confirmed; Foundry's "MCP tasks" preview status: VERIFY |
| Toolbox | Single MCP-compatible endpoint, versioning with promote-to-default, central auth, guardrails on tool inputs and outputs, tool search. Skills in Toolbox are labelled preview. | Skills preview confirmed; Toolbox GA status: VERIFY |
| Entra Agent Registry | Published Foundry agents can be shared through it. | Confirmed on Learn; registry API details: VERIFY |
| Azure API Center private MCP registry | Not checked against a primary source. | VERIFY: only a secondary claim |
| A2A | Agent Card at `/.well-known/agent-card.json`; spec 1.0.0 is latest; Foundry states A2A v1.0 is generally available and v0.3 remains preview. | Confirmed (see A2A section) |

## Lifecycle
| State | Meaning | Allowed next | Gate to enter |
|---|---|---|---|
| `draft` | Being written; may be called only in dev | `evaluated` | Schema valid, owner set |
| `evaluated` | Evals pass thresholds, docs complete | `approved` | Eval result link; reviewer sign-off |
| `approved` | Bindable by agents that list it | `deprecated` | Reviewer approval; governance sign-off for `high` risk |
| `deprecated` | Still callable; new bindings discouraged | `retired` | Deprecation date, replacement id |
| `retired` | Not callable; removed from catalogs | none | No approved agent references it |

## Tool manifest
One file per tool in `registry/tools/<id>.json`. Field notes:

| Field | Notes |
|---|---|
| `id`, `name` | `id` is the registry key (kebab-case); `name` is the MCP/function name (1-128 chars; letters, digits, `_`, `-`, `.`) |
| `risk_tier` | `low`, `medium`, `high` map to Tier 3, Tier 2, Tier 1 in [12-governance-and-compliance.md](./12-governance-and-compliance.md) |
| `side_effects` | `none`, `read`, `write`, `destructive`, `external` (data leaves the org) |
| `requires_human_approval` | Boolean plus free-text conditions; enforced at dispatch |
| `auth` | `agent-identity`, `managed-identity`, `on-behalf-of-user`, `none`; plus scopes and the named role |
| `mcp` | Only for MCP-backed tools; hash definition is in REG-022 |
| `evals` | Dataset ref (synthetic only), thresholds, last run, result link |

### Tool schema
`registry/schemas/tool.schema.json` (validated; see "Validation evidence").
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://registry.example.internal/schemas/tool.schema.json",
  "title": "AI tool manifest",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "name", "version", "owner", "description", "status", "risk_tier", "side_effects", "requires_human_approval", "input_schema", "output_schema", "error_schema", "auth", "data_classification_max", "limits", "idempotent", "evals", "docs", "observability", "regulatory"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9-]{2,63}$"
    },
    "name": {
      "type": "string",
      "pattern": "^[A-Za-z0-9_.-]{1,128}$"
    },
    "version": {
      "type": "string",
      "pattern": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(-[0-9A-Za-z.-]+)?$"
    },
    "owner": {
      "type": "object",
      "additionalProperties": false,
      "required": ["team", "role"],
      "properties": {"team": {"type": "string", "minLength": 1}, "role": {"type": "string", "minLength": 1}}
    },
    "description": {
      "type": "string",
      "minLength": 20,
      "maxLength": 1024
    },
    "status": {
      "enum": ["draft", "evaluated", "approved", "deprecated", "retired"]
    },
    "risk_tier": {
      "enum": ["low", "medium", "high"]
    },
    "side_effects": {
      "enum": ["none", "read", "write", "destructive", "external"]
    },
    "requires_human_approval": {
      "type": "object",
      "additionalProperties": false,
      "required": ["required"],
      "properties": {"required": {"type": "boolean"}, "conditions": {"type": "string"}}
    },
    "input_schema": {
      "$ref": "#/$defs/json_schema_input"
    },
    "output_schema": {
      "$ref": "#/$defs/json_schema_object"
    },
    "error_schema": {
      "$ref": "#/$defs/json_schema_object"
    },
    "auth": {
      "type": "object",
      "additionalProperties": false,
      "required": ["identity", "scopes", "role"],
      "properties": {"identity": {"enum": ["agent-identity", "managed-identity", "on-behalf-of-user", "none"]}, "scopes": {"type": "array", "items": {"type": "string"}, "uniqueItems": true}, "role": {"type": "string", "minLength": 1}}
    },
    "data_classification_max": {
      "enum": ["public", "internal", "confidential", "restricted"]
    },
    "limits": {
      "type": "object",
      "additionalProperties": false,
      "required": ["rate_per_minute", "timeout_seconds", "max_payload_bytes"],
      "properties": {"rate_per_minute": {"type": "integer", "minimum": 1}, "timeout_seconds": {"type": "number", "exclusiveMinimum": 0, "maximum": 300}, "max_cost_per_call_usd": {"type": "number", "minimum": 0}, "max_payload_bytes": {"type": "integer", "minimum": 1}}
    },
    "idempotent": {
      "type": "boolean"
    },
    "evals": {
      "type": "object",
      "additionalProperties": false,
      "required": ["dataset_ref", "thresholds"],
      "properties": {"dataset_ref": {"type": "string", "minLength": 1}, "thresholds": {"type": "object", "minProperties": 1, "additionalProperties": {"type": "number"}}, "last_run": {"type": "string", "format": "date"}, "result_link": {"type": "string", "minLength": 1}}
    },
    "docs": {
      "type": "object",
      "additionalProperties": false,
      "required": ["usage", "failure_modes", "runbook"],
      "properties": {"usage": {"type": "string"}, "failure_modes": {"type": "string"}, "examples": {"type": "array", "items": {"type": "string"}}, "runbook": {"type": "string"}}
    },
    "mcp": {
      "type": "object",
      "additionalProperties": false,
      "required": ["server", "pinned_version", "spec_version", "tool_definition_sha256"],
      "properties": {"server": {"type": "string", "minLength": 1}, "pinned_version": {"type": "string", "minLength": 1}, "spec_version": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"}, "tool_definition_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"}}
    },
    "observability": {
      "type": "object",
      "additionalProperties": false,
      "required": ["span_name"],
      "properties": {"span_name": {"type": "string"}, "metrics": {"type": "array", "items": {"type": "string"}}}
    },
    "regulatory": {
      "type": "object",
      "additionalProperties": false,
      "required": ["inventory_id"],
      "properties": {"inventory_id": {"type": "string", "minLength": 1}, "notes": {"type": "string"}}
    },
    "deprecation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["date"],
      "properties": {"date": {"type": "string", "format": "date"}, "replacement": {"type": "string"}}
    }
  },
  "allOf": [{"if": {"properties": {"status": {"enum": ["approved", "deprecated"]}}, "required": ["status"]}, "then": {"properties": {"evals": {"required": ["last_run", "result_link"]}}}}, {"if": {"properties": {"status": {"const": "deprecated"}}, "required": ["status"]}, "then": {"required": ["deprecation"]}}, {"if": {"properties": {"side_effects": {"const": "destructive"}}, "required": ["side_effects"]}, "then": {"properties": {"requires_human_approval": {"properties": {"required": {"const": true}}}}}}, {"if": {"properties": {"side_effects": {"enum": ["write", "destructive", "external"]}}, "required": ["side_effects"]}, "then": {"properties": {"idempotent": true}, "required": ["idempotent"]}}, {"if": {"properties": {"risk_tier": {"const": "high"}}, "required": ["risk_tier"]}, "then": {"properties": {"requires_human_approval": {"properties": {"required": {"const": true}}}}}}],
  "$defs": {
    "json_schema_object": {
      "type": "object",
      "required": ["type"],
      "properties": {"$schema": {"const": "https://json-schema.org/draft/2020-12/schema"}, "type": {"enum": ["object", "array"]}}
    },
    "json_schema_input": {
      "type": "object",
      "required": ["type"],
      "properties": {"$schema": {"const": "https://json-schema.org/draft/2020-12/schema"}, "type": {"const": "object"}}
    }
  }
}
```

### Example tool manifest
Validated against the schema above. `tool_definition_sha256` was computed with the function in the registry check below.
```json
{
  "id": "policy-document-lookup",
  "name": "policy_document_lookup",
  "version": "1.2.0",
  "owner": {
    "team": "claims-platform",
    "role": "Tech Lead"
  },
  "description": "Returns metadata and a short extract for one policy document by document identifier. Read-only. Does not return policyholder personal information.",
  "status": "approved",
  "risk_tier": "low",
  "side_effects": "read",
  "requires_human_approval": {
    "required": false
  },
  "input_schema": {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": false,
    "required": ["document_id"],
    "properties": {"document_id": {"type": "string", "pattern": "^DOC-[0-9]{8}$"}}
  },
  "output_schema": {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["document_id", "title", "extract"],
    "properties": {"document_id": {"type": "string"}, "title": {"type": "string"}, "extract": {"type": "string", "maxLength": 2000}}
  },
  "error_schema": {
    "type": "object",
    "required": ["code", "message"],
    "properties": {"code": {"enum": ["not_found", "forbidden", "timeout"]}, "message": {"type": "string"}}
  },
  "auth": {
    "identity": "agent-identity",
    "scopes": ["documents.read"],
    "role": "Document Reader (custom, scoped to the documents store)"
  },
  "data_classification_max": "restricted",
  "limits": {
    "rate_per_minute": 60,
    "timeout_seconds": 10,
    "max_cost_per_call_usd": 0.001,
    "max_payload_bytes": 65536
  },
  "idempotent": true,
  "evals": {
    "dataset_ref": "evals/datasets/policy-document-lookup.jsonl",
    "thresholds": {"schema_valid_rate": 1.0, "correct_document_rate": 0.98},
    "last_run": "2026-11-20",
    "result_link": "https://gitlab.example.internal/group/project/-/jobs/12345"
  },
  "docs": {
    "usage": "docs/tools/policy-document-lookup.md",
    "failure_modes": "docs/tools/policy-document-lookup.md#failure-modes",
    "examples": ["docs/tools/policy-document-lookup.md#examples"],
    "runbook": "docs/runbooks/policy-document-lookup.md"
  },
  "mcp": {
    "server": "documents-mcp",
    "pinned_version": "3.4.1",
    "spec_version": "2026-07-28",
    "tool_definition_sha256": "f12bd12eeed4358696b1931607c9105117b8cdbfc3e9e7031677ed74d004d9a7"
  },
  "observability": {
    "span_name": "execute_tool policy_document_lookup",
    "metrics": ["tool.calls", "tool.errors", "tool.latency_ms"]
  },
  "regulatory": {
    "inventory_id": "INV-0000-EXAMPLE"
  }
}
```

## Agent manifest
One file per agent in `registry/agents/<id>.json`. The model deployment is a placeholder because the approved model list is unresolved (F2).

### Agent schema
`registry/schemas/agent.schema.json`.
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://registry.example.internal/schemas/agent.schema.json",
  "title": "AI agent manifest",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "version", "owner", "status", "risk_tier", "purpose", "non_goals", "autonomy_rung", "allowed_tools", "model", "data_classes", "evals", "guardrails", "human_approval_points", "kill_switch", "runbook", "inventory_id", "prompts"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9-]{2,63}$"
    },
    "version": {
      "type": "string",
      "pattern": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(-[0-9A-Za-z.-]+)?$"
    },
    "owner": {
      "type": "object",
      "additionalProperties": false,
      "required": ["team", "role"],
      "properties": {"team": {"type": "string", "minLength": 1}, "role": {"type": "string", "minLength": 1}}
    },
    "status": {
      "enum": ["draft", "evaluated", "approved", "deprecated", "retired"]
    },
    "risk_tier": {
      "enum": ["low", "medium", "high"]
    },
    "purpose": {
      "type": "string",
      "minLength": 20
    },
    "non_goals": {
      "type": "array",
      "minItems": 1,
      "items": {"type": "string", "minLength": 1}
    },
    "autonomy_rung": {
      "enum": ["suggest", "assist-read", "propose", "act-low-risk", "act-bounded", "autonomous"]
    },
    "allowed_tools": {
      "type": "array",
      "items": {"type": "object", "additionalProperties": false, "required": ["id", "version_range"], "properties": {"id": {"type": "string", "pattern": "^[a-z][a-z0-9-]{2,63}$"}, "version_range": {"type": "string", "pattern": "^[~^]?\\d+\\.\\d+\\.\\d+$|^>=\\d+\\.\\d+\\.\\d+,<\\d+\\.\\d+\\.\\d+$"}}}
    },
    "model": {
      "type": "object",
      "additionalProperties": false,
      "required": ["deployment", "model_version", "fallback"],
      "properties": {"deployment": {"type": "string", "pattern": "^<[a-z-]+-deployment>$|^[A-Za-z0-9._-]+$"}, "model_version": {"type": "string", "minLength": 1, "not": {"pattern": "(?i)^(latest|default|auto|stable|current)$"}}, "fallback": {"type": "string"}}
    },
    "data_classes": {
      "type": "array",
      "minItems": 1,
      "uniqueItems": true,
      "items": {"enum": ["public", "internal", "confidential", "restricted"]}
    },
    "evals": {
      "type": "object",
      "additionalProperties": false,
      "required": ["suite_path", "thresholds_ref"],
      "properties": {"suite_path": {"type": "string"}, "thresholds_ref": {"type": "string"}, "last_run": {"type": "string", "format": "date"}, "result_link": {"type": "string"}}
    },
    "guardrails": {
      "type": "object",
      "additionalProperties": false,
      "required": ["policy_name", "prompt_injection_checks"],
      "properties": {"policy_name": {"type": "string", "minLength": 1}, "prompt_injection_checks": {"type": "boolean"}, "output_validation": {"type": "string"}}
    },
    "human_approval_points": {
      "type": "array",
      "items": {"type": "string", "minLength": 1}
    },
    "kill_switch": {
      "type": "object",
      "additionalProperties": false,
      "required": ["mechanism", "owner_role"],
      "properties": {"mechanism": {"type": "string", "minLength": 1}, "owner_role": {"type": "string", "minLength": 1}}
    },
    "runbook": {
      "type": "string",
      "minLength": 1
    },
    "inventory_id": {
      "type": "string",
      "minLength": 1
    },
    "prompts": {
      "type": "array",
      "minItems": 1,
      "items": {"type": "object", "additionalProperties": false, "required": ["path", "sha256"], "properties": {"path": {"type": "string"}, "sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"}}}
    }
  },
  "allOf": [{"if": {"properties": {"status": {"enum": ["approved"]}}, "required": ["status"]}, "then": {"properties": {"evals": {"required": ["last_run", "result_link"]}}}}, {"if": {"properties": {"risk_tier": {"const": "high"}}, "required": ["risk_tier"]}, "then": {"properties": {"autonomy_rung": {"enum": ["suggest", "assist-read", "propose"]}, "human_approval_points": {"minItems": 1}}}}]
}
```

### Example agent manifest
```json
{
  "id": "claims-intake-triage",
  "version": "0.3.0",
  "owner": {
    "team": "claims-platform",
    "role": "Product Owner"
  },
  "status": "approved",
  "risk_tier": "high",
  "purpose": "Classifies incoming claim submissions and routes them to the correct queue. Never decides coverage.",
  "non_goals": ["Deciding or recommending coverage or payment", "Contacting claimants"],
  "autonomy_rung": "propose",
  "allowed_tools": [{"id": "policy-document-lookup", "version_range": "^1.2.0"}],
  "model": {
    "deployment": "<chat-deployment>",
    "model_version": "<pinned-model-version>",
    "fallback": "route-to-human-queue"
  },
  "data_classes": ["confidential", "restricted"],
  "evals": {
    "suite_path": "evals/claims-intake-triage/",
    "thresholds_ref": "evals/claims-intake-triage/thresholds.yaml",
    "last_run": "2026-11-20",
    "result_link": "https://gitlab.example.internal/group/project/-/jobs/12399"
  },
  "guardrails": {
    "policy_name": "<guardrail-policy>",
    "prompt_injection_checks": true,
    "output_validation": "pydantic schema, reject on failure"
  },
  "human_approval_points": ["Every routing decision, before it takes effect (autonomy rung propose)"],
  "kill_switch": {
    "mechanism": "feature flag claims-intake-triage-enabled",
    "owner_role": "On-call engineer"
  },
  "runbook": "docs/runbooks/claims-intake-triage.md",
  "inventory_id": "INV-0001-EXAMPLE",
  "prompts": [{"path": "prompts/claims-intake-triage/system.md", "sha256": "d1f197558e345fd1f2db4c90e9da2d110b7020d8e52fac0777e6284f843a5f32"}]
}
```

## Registry check
`make registry-check` runs schema validation (with format checking), validates embedded schemas, resolves agent-to-tool references, checks tool status, and compares hashes. This sketch is the tested baseline. It implements schema validation, embedded-schema validity, agent-to-tool resolution, tool status, REG-019 data-class ceilings and hash checks. It does NOT implement version-range matching (REG-006), REG-011, the rung-versus-tool-side-effects check (PRN-012, PRN-029), the live-server hash comparison (REG-022) or the deployed-model-version comparison (REG-028); the last two need network and Terraform state access. Extend it before relying on `make registry-check` as the gate for those rules.
```python
"""Registry check sketch: schema validation plus cross-file checks."""
import hashlib, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

CLASS_ORDER = ["public", "internal", "confidential", "restricted"]

def tool_definition_sha256(manifest: dict) -> str:
    """Hash the canonical JSON of the tools/list entry the agent would see."""
    entry = {
        "name": manifest["name"],
        "description": manifest["description"],
        "inputSchema": manifest["input_schema"],
        "outputSchema": manifest["output_schema"],
    }
    canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def validate(schema: dict, instance: dict) -> list[str]:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [f"{'/'.join(map(str, e.path))}: {e.message}" for e in validator.iter_errors(instance)]

def main(root: Path) -> int:
    tool_schema = load(root / "schemas/tool.schema.json")
    agent_schema = load(root / "schemas/agent.schema.json")
    errors: list[str] = []
    tools = {}
    for p in sorted((root / "tools").glob("*.json")):
        m = load(p)
        errors += [f"{p.name}: {e}" for e in validate(tool_schema, m)]
        for key in ("input_schema", "output_schema", "error_schema"):
            Draft202012Validator.check_schema(m[key])  # embedded schemas must be valid too
        if "mcp" in m and m["mcp"]["tool_definition_sha256"] != tool_definition_sha256(m):
            errors.append(f"{p.name}: tool_definition_sha256 does not match manifest")
        tools[m["id"]] = m
    for p in sorted((root / "agents").glob("*.json")):
        a = load(p)
        errors += [f"{p.name}: {e}" for e in validate(agent_schema, a)]
        for ref in a["allowed_tools"]:
            tool = tools.get(ref["id"])
            if tool is None:
                errors.append(f"{p.name}: unknown tool {ref['id']}")
            elif tool["status"] != "approved":
                errors.append(f"{p.name}: tool {ref['id']} is {tool['status']}, not approved")
            if tool is not None:  # REG-019
                top = CLASS_ORDER.index(tool["data_classification_max"])
                errors += [
                    f"{p.name}: data class {c} exceeds max of tool {ref['id']} (REG-019)"
                    for c in a["data_classes"] if CLASS_ORDER.index(c) > top
                ]
        for pr in a["prompts"]:
            if file_sha256(root / pr["path"]) != pr["sha256"]:
                errors.append(f"{p.name}: prompt hash mismatch for {pr['path']}")
    print("\n".join(errors) or "registry ok")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
```

## Validation evidence
The two schemas, the example tool manifest and the example agent manifest above were validated with `jsonschema` (Draft 2020-12 validator, format checker enabled) in a fresh virtual environment, running Python with `-I`; the registry check printed `registry ok`. Negative cases were also exercised and failed as intended: a floating model alias (`latest`), an unknown tool reference, a `high` risk agent above `propose`, a `destructive` tool without human approval, a draft-07 `$schema` in an input schema, a `deprecated` tool without a deprecation block and an unknown top-level property. Re-run these in your own repository before relying on the schemas: the schemas are an internal standard, not an MCP or Foundry format.

## MCP notes
- Pin the spec revision in each tool manifest; do not rely on blog summaries of the protocol. MCP carries trace context in `_meta` (`traceparent`, `tracestate`, `baggage`); use it so tool spans join the agent trace ([10-logging-observability.md](./10-logging-observability.md)).
- Because the revision is stateless, tools needing state use explicit handles returned by a creation tool; treat a handle as a name, not a capability, and check authorization on every call.
- Clients SHOULD validate structured results against `outputSchema`; this registry makes that mandatory for registered tools by storing the schema in the manifest.
- Servers MUST validate inputs, rate-limit and sanitize outputs per the MCP security considerations; the registry records the limits, the tool owner implements them.

## A2A agent cards
- The A2A specification (latest 1.0.0) says servers MUST make an Agent Card available and clients can fetch it from `/.well-known/agent-card.json`. Agent Card required fields reported: `name`, `description`, `supportedInterfaces`, `version`, `capabilities`, `defaultInputModes`, `defaultOutputModes`, `skills`. VERIFY: confirm the exact required list against section 4.4.1 of the specification before building a schema.
- Cards MAY be signed with JWS over a JCS-canonicalized card; clients SHOULD verify at least one signature before trusting a signed card.
- An Agent Card is self-description by the remote party. It is not a registry entry and grants no permission. Treat it as untrusted until the agent is registered here.

## Checklist
- [ ] Every tool and agent in the repo has a manifest and `make registry-check` passes.
- [ ] Manifest `status` matches reality; `approved` items have eval `last_run` and `result_link`.
- [ ] `side_effects`, `risk_tier` and approval flags were set by a human reviewer, not copied from MCP annotations.
- [ ] Tool descriptions were reviewed as security-relevant text.
- [ ] MCP server version, spec revision and definition hash are pinned; the drift job is scheduled.
- [ ] Agent `allowed_tools` is minimal; each tool has a version range.
- [ ] Model version is explicit and matches the deployed version; prompts are hash-pinned.
- [ ] Kill switch tested; runbook linked; inventory id set.
- [ ] Data classes of the agent do not exceed any tool's maximum.

## Common AI failure modes
- Registering a tool by copying the MCP server's own annotations into `side_effects`, so a mislabelled write tool shows as read-only.
- Writing a verbose, instruction-laden tool description that doubles as a prompt injection ("always call this tool first").
- Binding every tool the server returns instead of the approved allow-list, so new server tools become callable silently.
- Setting `model_version` to `latest` or a floating alias to "keep up".
- Bumping a tool schema without bumping the version or re-running evals.
- Hashing the tool list from an admin identity, so the hash does not match what the agent actually sees.
- Treating an A2A Agent Card or a Toolbox listing as approval.
- Marking a manifest `approved` to unblock a merge request; the eval link is a placeholder.
- Inventing manifest fields or MCP features not in the schema or specification.

## Related docs
- [02-security.md](./02-security.md): agent threats, MCP server vetting.
- [04-engineering-principles.md](./04-engineering-principles.md): autonomy ladder and human-in-the-loop principle.
- [12-governance-and-compliance.md](./12-governance-and-compliance.md): inventory and approvals.
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md): data classes.
- [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md): eval datasets and thresholds.
- [15-llm-and-model-governance.md](./15-llm-and-model-governance.md): models, prompts, versioning.
- [17-api-and-contracts.md](./17-api-and-contracts.md): tool schemas as contracts.
- [23-azure-foundry-standards.md](./23-azure-foundry-standards.md): Toolbox, identity, guardrails.
- [26-ai-use-case-catalog.md](./26-ai-use-case-catalog.md): which autonomy rung and risk tier a use case implies.
- [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md): waivers.

## Sources
- MCP specification 2026-07-28 (overview, tools, key changes): https://modelcontextprotocol.io/specification/2026-07-28
- Foundry Agent Service overview: https://learn.microsoft.com/en-us/azure/foundry/agents/overview
- What is Toolbox in Microsoft Foundry: https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/toolbox-overview
- Agent identity concepts in Microsoft Foundry: https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity
- A2A Protocol specification: https://a2a-protocol.org/latest/specification/
