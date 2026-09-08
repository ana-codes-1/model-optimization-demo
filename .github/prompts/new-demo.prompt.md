---
description: "Bootstrap a brand-new EPS AI partner demo from this template: interview the architect, then scaffold docs/infra/backend/frontend per the eps-demo-* skills."
name: "New EPS Demo"
argument-hint: "Partner name + one-line idea (optional — you'll be asked if omitted)"
agent: agent
---

# New EPS Demo — bootstrap

You are bootstrapping a brand-new partner demo from the `eps-demos-template`
baseline. Follow [AGENTS.md](../../AGENTS.md)'s "Starting a brand-new demo"
section and the skills it points to — read
[eps-demo-standards](../skills/eps-demo-standards/SKILL.md) first.

## 0. Check prerequisites before anything else

Run these in the same shell/context that will provision and deploy. Stop with
clear instructions if any required login fails — don't guess or work around it:

- `az account show` (Azure CLI signed in)
- `azd auth login --check-status` or `azd env list` (Azure Developer CLI context)
- `gh auth status` (GitHub CLI signed in)

If more than one GitHub account is configured, confirm the account that can read
and push the target organization, including SSO/EMU authorization. When WSL is
requested, verify the repo is under the native Linux filesystem and not `/mnt`.

## 1. Interview

If the user's request doesn't already answer these, ask (use the
ask-questions tool, don't just assume):

1. **Partner name** (internal use only — never on the public site), target
   audience, production concern, and the **idea/problem** being demoed.
2. The core "wow" moment, plain-language narrative, and user journey to optimize.
3. User/job roles and the document, field, tool, and file-access matrix. Ask
   separately about end-user identity and agent workload identity.
4. Likely **AI capability** (chat, agentic tool use, RAG, generation, none),
   required tools, evidence/citations, prompt overrides, and evaluation needs.
5. Models: fixed deployments, user choice, Model Router, token/cost visibility,
   and any residency/capacity constraints.
6. **Frontend/backend framework preference.** If none, default per
   [eps-demo-architecture](../skills/eps-demo-architecture/SKILL.md): React +
   TypeScript frontend; ask which backend language (no fixed template
   default — .NET minimal API, Python FastAPI, and Node/TypeScript are all
   fair game); compute defaults to Azure Static Web Apps + Azure Functions
   (Flex Consumption) unless Container Apps fits better.
7. **Data needs** — none, synthetic, or a bundled read-only catalog. Real
   partner/customer data is never acceptable
   ([eps-demo-compliance](../skills/eps-demo-compliance/SKILL.md)). Ask whether
   external systems require scoped API keys and whether files/PDFs need a
   separate authorization/download path.
8. State and delivery: conversation history, New/Clear chat, persistence,
   realtime streaming, mobile use, custom domain, and accessibility.
9. Operations: one supervised event or a globally shared/long-lived demo,
   health dependencies, telemetry destinations, alert recipients, retention,
   and expected support model.
10. Repository visibility, network/private-endpoint requirements, allowed
    operator IPs, and local execution environment (including native WSL).
11. **Timeline/urgency** — WAF priority defaults to Cost → Security →
   Performance → Operational Excellence → Reliability.

## 2. Restate the plan before writing code

Summarize what you're building and cite the skill behind each notable choice
(e.g., "per `eps-demo-identity`, using the alias+GUID pattern since there's no
real auth requirement"). Flag anywhere you're deferring a hard rule (most
often Private Link) and how it'll be documented.

## 3. Scaffold in this order

1. `docs/` — fill in the structure already stubbed under `docs/` (overview,
   narrative, architecture, security, code tour, cost, operations, ADRs,
   telemetry). Add ADRs for any material decision, including the compute choice
   below. For private repos or nontechnical audiences, plan served static HTML
   linked from the app.
2. `infra/` — `main.bicep`/`resources.bicep` currently only wire the resource
   group, tags, budget, and App Insights/Log Analytics (compute-agnostic on
   purpose — see `docs/adr/0004-stack-agnostic-template.md`). Add the compute
   this demo needs (Static Web Apps + Functions, Container Apps, etc.) and any
   data services to `resources.bicep`. The first time you add a resource with
   data-plane RBAC: add `principalId`/`principalType`/`grantDeveloperAccess`
   params (wire from `AZURE_PRINCIPAL_ID`, already derived by
   `infra/hooks/preprovision.*`) and a shared role-assignment module invoked
   once for the app's managed identity and once for the developer principal,
   so the two grants can never drift (`eps-demo-architecture`). Keep Private
   Link opt-in by default unless the demo needs it from day one
   (`docs/adr/0003`). If AI is involved, provision AI Foundry, flip on the
   matching config in `config/models.json`, and add its own RBAC pair the
   same way.
3. `backend/` — build the API. Dependency-inject every external call
   (`eps-demo-testing-solid`); route AI calls through a `FAKE_AI=1`-aware
   layer. Keep prompts/request templates in separate files. Treat search and
   file operations as first-class Agent Framework tools when using hosted agents.
4. Agent identities and authorization — deploy bootstrap identities when
   necessary, capture runtime principals, assign exact secret/container roles,
   and prove positive plus negative access before enabling production tools.
5. `frontend/` — build the UI per `eps-demo-ux` (narrative Home/About, live
   demo, health, designed states, safe streaming summaries/tool events,
   evidence, skeletons, mobile menu, colophon, footer, reset/new/clear controls).
6. Production-readiness surfaces — for shared/long-lived demos add cached
   no-model health, correlated content-safe telemetry, actionable sustained
   alerts, bounded history/files, realtime fallback, and retention.
7. `.vscode/tasks.json` + `launch.json` — replace the placeholder `dev` task
   with one dedicated task per service (distinct icon/color, per
   `eps-demo-devx`) plus a "Run All" compound and a "Debug All" launch
   compound.
8. `.github/workflows/ci.yml` — flesh out the guarded `frontend`/
   `backend-dotnet` (or equivalent) jobs; keep the coverage gates
   (BE ≥ 70%, FE ≥ 60%) and `FAKE_AI=1`.
9. `evals/` — add eval cases once there's an AI feature worth evaluating.
10. Update `CODEOWNERS` to the actual owning architect(s), and `docs/README.md`'s
   standards-compliance table to reflect reality (✅ / ⚠️ / ❌, honestly).

## 4. Release gate

Do not stop after scaffolding or local validation. For the intended environment:

1. run lint, build, tests/coverage, Bicep, generated-doc, and secret checks;
2. deploy and verify the public/default and custom domains;
3. run the critical journey, one allowed boundary, and one expected denial;
4. verify actual routed-model attribution and telemetry queries when applicable;
5. require health ready without scheduled model inference;
6. verify portrait mobile and served documentation;
7. remove temporary runners, identities, roles, packages, and artifacts; and
8. push the clean release commit.

Use `eps-demo-production-readiness` for the full contract.

## 5. Remember

- Never silently defer Managed Identity (no keys/passwords) or the no-PII /
  no-partner-name rules — everything else can be a documented gap, nothing is
  a silent shortcut.
- Keep changes surgical and cite skills in commit/PR messages.
