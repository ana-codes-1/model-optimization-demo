using 'main.bicep'

// AZURE_ENV_NAME / AZURE_LOCATION are set automatically by azd. AZURE_BUDGET_EMAIL
// is derived by infra/hooks/preprovision.* if not already set in the azd
// environment — see that script before assuming it's unset. (That hook also
// derives AZURE_PRINCIPAL_ID in advance, ready for the day this file grows a
// `principalId` param — see resources.bicep's header comment.)
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME')
param location = readEnvironmentVariable('AZURE_LOCATION')
param budgetContactEmail = readEnvironmentVariable('AZURE_BUDGET_EMAIL')
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', '')

// The Foundry account and its twelve model deployments predate this repo and are
// not managed here (docs/adr/0008). Set both before the first deploy:
//   azd env set AZURE_FOUNDRY_ACCOUNT        <account-name>
//   azd env set AZURE_FOUNDRY_RESOURCE_GROUP <resource-group>
// They are deliberately not defaulted: the account name is the endpoint
// hostname, and this repo keeps the live endpoint out of source (config.json is
// gitignored for the same reason). infra/hooks/preprovision.* fails early with
// this message if either is missing.
param foundryAccountName = readEnvironmentVariable('AZURE_FOUNDRY_ACCOUNT', '')
param foundryResourceGroupName = readEnvironmentVariable('AZURE_FOUNDRY_RESOURCE_GROUP', '')
