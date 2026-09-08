# ADR 0002: Azure Developer CLI (azd) as the deploy standard

- Status: accepted
- Date: 2026-08-05
- Context: `eps-demo-devx` requires a single command that brings up the whole
  environment from scratch, and the uniform CLI's `deploy` verb needs one
  real implementation shared by every demo. Architects are already expected
  to have the Azure CLI installed and signed in.
- Decision: `make deploy` runs `azd up`. `infra/main.bicep` and
  `infra/main.bicepparam` follow azd's conventions (subscription-scoped
  entrypoint, `AZURE_ENV_NAME`/`AZURE_LOCATION` read via
  `readEnvironmentVariable`). An `infra/hooks/preprovision.*` script derives
  `AZURE_PRINCIPAL_ID` and `AZURE_BUDGET_EMAIL` automatically so architects
  never hand-export them.
- Consequences:
  - Good: one command (`azd up`) provisions infra and (once `azure.yaml`
    lists services) deploys code — idempotent, re-runnable.
  - Good: CI/CD can reuse the identical flow with `azd auth login`
    (federated/OIDC, no client secret) — see `.github/workflows/deploy.yml`.
  - Bad: adds `azd` to the prerequisite list alongside `az`; mitigated by
    including it in `.devcontainer/devcontainer.json`.
