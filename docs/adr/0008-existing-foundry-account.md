# ADR 0008: Reference the existing AI Foundry account rather than provisioning one

- Status: accepted
- Date: 2026-09-08
- Context: The `/new-demo` scaffold order says that when AI is involved, `infra/`
  should provision AI Foundry alongside the app. This demo's entire subject is a
  head-to-head comparison of twelve *specific* model configurations — six models,
  each at its cheapest and most expensive thinking setting. Those deployments
  already exist on a Foundry account that predates this repo, including two
  Anthropic models that arrive through the Foundry marketplace flow rather than a
  plain `Microsoft.CognitiveServices/deployments` resource, and which have their
  own quota and regional availability constraints.

  Provisioning a fresh Foundry account per `azd` environment would mean every
  `azd up` re-creating six deployments, hitting per-subscription model quota, and
  risking a demo where a row fails because capacity wasn't granted in the new
  region — a failure mode indistinguishable, on the chart, from a model getting
  the answer wrong.

- Decision: Treat the Foundry account as **pre-existing infrastructure**,
  referenced by name and resource group through `foundryAccountName` /
  `foundryResourceGroupName`. Both are supplied from the `azd` environment
  (`azd env set AZURE_FOUNDRY_ACCOUNT` / `AZURE_FOUNDRY_RESOURCE_GROUP`) and are
  deliberately **not defaulted in `main.bicepparam`** — the account name is also
  the endpoint hostname, and this repo keeps the live endpoint out of source for
  the same reason `config.json` is gitignored. `infra/hooks/preprovision.*` fails
  early with that instruction if either is unset. `infra/` provisions the app,
  the budget, and observability, and grants data-plane access on that account via
  `modules/foundry-access.bicep`. It never manages the models themselves.
- Consequences:
  - Good: `azd up` is fast, repeatable, and cannot disturb the roster the demo
    depends on. Model changes stay a `config.json` edit, per
    `eps-demo-ai-models`.
  - Good: the role grant is still infrastructure-as-code, and goes through the
    same shared `role-assignment.bicep` module for both the app identity and the
    signed-in developer, so local and deployed rights cannot drift.
  - Bad: `azd up` is not fully self-contained — it assumes that account exists
    and that the deployer can write role assignments on its resource group. A
    genuinely fresh environment needs the models deployed first;
    `deploy-claude.json` covers the Anthropic half.
  - Neutral: the Foundry account lives in `eastus2` while the app runs in
    `westus2` (see ADR 0007), so the role assignment is a deliberate
    cross-resource-group, cross-region module.
