---
name: eps-demo-architecture
description: Azure architecture and IaC standards for EPS AI vibe demos. Use when scaffolding infrastructure, writing Bicep, choosing compute, or wiring Azure dependencies.
---

# EPS Demo — Architecture & Hosting

## Hosting

- Always hosted in **Azure**.
- Static front end + API back end preferred.
- Compute options:
  - **Azure Static Web Apps** with BYO **Azure Function (Flex Consumption)** — default.
  - **Azure Container Apps** when the workload doesn't fit SWA + Functions.
- Frontend frameworks recommended (not mandated): React + TypeScript.
- Backend frameworks recommended (not mandated): Python FastAPI or .NET minimal API.

## Infrastructure as Code

- **Bicep is the standard.** No Terraform, no ARM JSON unless absolutely necessary.
- Modules live under `infra/` at the repo root.
- A single `azd` (Azure Developer CLI) or equivalent script must bring up the entire environment from scratch.

## Production-grade defaults

These apply to every demo, even ones with tiny scope:

- **Private Link** to every Azure dependency (Storage, SQL, Cosmos, Foundry, Key Vault).
- **Managed Identity always.** No connection strings with keys, no SAS in source, no passwords.
- **Key Vault** for any secret that cannot be eliminated (e.g., a partner-service credential).
- Outbound network: connect only to Azure services and the named partner service.
- All resources tagged: `demo=true`, `owner=<alias>`, `partner=<short-name-or-none>`, `cost-center=eps-ai-demos`.

For multi-agent demos, an agent with a distinct data boundary gets a distinct
workload identity. Do not reuse a project/host identity merely because the agents
share compute or a model. Capture platform-created hosted-agent principals after
deployment and reconcile their exact downstream RBAC.

External SaaS services that cannot use Managed Identity are an explicit trust
boundary:

- store each least-privilege credential in a secret-scoped Key Vault entry;
- pin outbound requests to one HTTPS origin and disable redirects before adding
  authorization;
- document public versus private egress and downstream DLS/FLS/role enforcement;
  and
- never centralize per-agent retrieval credentials in a shared health/API service.

## Network and deployment details

- Realtime services use exact HTTPS CORS origins for both the Azure default
  hostname and configured custom domain. Never use wildcard credentialed CORS.
- When private Function/package Storage blocks normal deployment, use an
  ephemeral VNet-connected runner with a temporary identity and minimum roles.
  Remove the runner, identity, role assignments, package container, and local
  bundle after verification.
- Temporary selected-IP access for operators is a parameterized, documented gap
  with default-deny firewalls and Private Link retained. Do not broaden to all
  networks.
- Long-lived demos include the monitoring, health, retention, and alert resources
  required by `eps-demo-production-readiness`.

## Model configuration

- **No hardcoded model names.** All model identifiers, endpoints, and deployments come from configuration.
- A single `models.json` (or equivalent) at the repo root drives which deployments the app uses; swapping a deprecated model is a config change.
- See `eps-demo-ai-models` for content-filter and cost-surfacing requirements.

## Local development against Azure

- **No local emulators** (Azurite has been buggy). Local dev hits a shared dev Azure Storage account (and Cosmos / SQL / Foundry resources) via Managed Identity or short-lived credentials.
- **Grant the current signed-in user the same RBAC roles as the app's Managed Identity.** Whenever IaC assigns a data-plane role to the workload identity (e.g., `Cognitive Services OpenAI User` / `Azure AI User`, `Storage Blob Data Contributor`, `Cosmos DB Built-in Data Contributor`, `Key Vault Secrets User`), it must also assign the **identical** role to the developer principal so they can run the app locally against the real cloud dependencies via `DefaultAzureCredential` / `az login`.
  - Pass the developer's object ID into Bicep as a parameter (e.g., `principalId`), defaulting from `az ad signed-in-user show --query id -o tsv` in the `azd`/deploy script.
  - Use the **same role-assignment module** for both the Managed Identity and the developer principal so the two never drift.
  - Gate these developer-principal assignments behind a flag (e.g., `grantDeveloperAccess`, default `true` for dev/demo, `false` for hardened/CI environments) so they aren't created where they shouldn't be.
- CI uses `FAKE_AI=1` plus per-PR ephemeral resources where useful.

## Architecture diagram

Every repo must include `docs/architecture/` with at least one C4-style diagram (or equivalent) showing components, trust boundaries, and Azure services in use.
