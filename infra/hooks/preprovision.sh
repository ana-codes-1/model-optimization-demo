#!/usr/bin/env bash
# azd preprovision hook — derives values that must never be hardcoded per
# architect (eps-demo-architecture: grant the signed-in developer the same
# RBAC as the app identity; eps-demo-cost-security: budget alerts need a real
# contact). Run automatically by `azd up` / `azd provision`.
set -euo pipefail

if ! az account show >/dev/null 2>&1; then
  echo "Not logged into Azure CLI. Run 'az login' first." >&2
  exit 1
fi

if [ -z "${AZURE_PRINCIPAL_ID:-}" ]; then
  principal_id="$(az ad signed-in-user show --query id -o tsv)"
  azd env set AZURE_PRINCIPAL_ID "$principal_id"
fi

if [ -z "${AZURE_BUDGET_EMAIL:-}" ]; then
  budget_email="$(az account show --query user.name -o tsv)"
  azd env set AZURE_BUDGET_EMAIL "$budget_email"
fi

# The Foundry account is referenced, not provisioned (docs/adr/0008). It is not
# defaulted in main.bicepparam because the account name is the endpoint hostname,
# which this repo keeps out of source — so fail here with a usable message rather
# than letting Bicep reject an empty string later.
if [ -z "${AZURE_FOUNDRY_ACCOUNT:-}" ] || [ -z "${AZURE_FOUNDRY_RESOURCE_GROUP:-}" ]; then
  cat >&2 <<'EOF'
This demo calls model deployments on an AI Foundry account that already exists.
Point the deployment at it before running 'azd up':

  azd env set AZURE_FOUNDRY_ACCOUNT        <account-name>
  azd env set AZURE_FOUNDRY_RESOURCE_GROUP <resource-group>

See docs/adr/0008-existing-foundry-account.md.
EOF
  exit 1
fi
