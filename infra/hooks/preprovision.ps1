# azd preprovision hook — derives values that must never be hardcoded per
# architect (eps-demo-architecture: grant the signed-in developer the same
# RBAC as the app identity; eps-demo-cost-security: budget alerts need a real
# contact). Run automatically by `azd up` / `azd provision`.
$ErrorActionPreference = "Stop"

az account show | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Not logged into Azure CLI. Run 'az login' first."
    exit 1
}

if (-not $env:AZURE_PRINCIPAL_ID) {
    $principalId = az ad signed-in-user show --query id -o tsv
    azd env set AZURE_PRINCIPAL_ID $principalId
}

if (-not $env:AZURE_BUDGET_EMAIL) {
    $budgetEmail = az account show --query user.name -o tsv
    azd env set AZURE_BUDGET_EMAIL $budgetEmail
}

# The Foundry account is referenced, not provisioned (docs/adr/0008). It is not
# defaulted in main.bicepparam because the account name is the endpoint hostname,
# which this repo keeps out of source — so fail here with a usable message rather
# than letting Bicep reject an empty string later.
if (-not $env:AZURE_FOUNDRY_ACCOUNT -or -not $env:AZURE_FOUNDRY_RESOURCE_GROUP) {
    Write-Error @"
This demo calls model deployments on an AI Foundry account that already exists.
Point the deployment at it before running 'azd up':

  azd env set AZURE_FOUNDRY_ACCOUNT        <account-name>
  azd env set AZURE_FOUNDRY_RESOURCE_GROUP <resource-group>

See docs/adr/0008-existing-foundry-account.md.
"@
    exit 1
}
