// Subscription-scoped azd entrypoint (per eps-demo-architecture): `azd up`
// brings up a brand-new environment from scratch, including the resource
// group itself. Deliberately minimal — compute (Static Web Apps + Functions,
// Container Apps, etc.) and any data services are an architect/demo decision
// made when the app is scaffolded, not something this template presupposes
// (see docs/adr/0004-stack-agnostic-template.md). This file only wires the
// guardrails every demo needs from day one: the resource group, tags, and a
// budget — extended in resources.bicep.
targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('azd environment name — also used to derive resource names.')
param environmentName string

@description('Azure region for all resources.')
param location string

@description('Monthly budget (USD) for the resource group; drives cost alerts (eps-demo-cost-security).')
param monthlyBudgetUsd int = 50

@description('Email for budget + cost alerts (set by infra/hooks/preprovision.*, defaults to the deployer).')
param budgetContactEmail string

@description('Partner short name, or "none". Never a full partner/customer name — this flows into resource tags only, never the public UI (eps-demo-compliance).')
param partnerName string = 'none'

@description('Object ID of the signed-in developer, derived by infra/hooks/preprovision.*. Granted the same Foundry role as the app so local runs behave identically (eps-demo-architecture).')
param principalId string = ''

@description('Set false for hardened or CI environments where no human should hold data-plane rights.')
param grantDeveloperAccess bool = true

@description('Name of the existing AI Foundry account holding the model roster (docs/adr/0008). Set with `azd env set AZURE_FOUNDRY_ACCOUNT`; not defaulted, because the account name is also the endpoint hostname and this repo keeps that out of source.')
@minLength(1)
param foundryAccountName string

@description('Resource group holding that Foundry account. It predates this deployment and is not managed here. Set with `azd env set AZURE_FOUNDRY_RESOURCE_GROUP`.')
@minLength(1)
param foundryResourceGroupName string

var ownerAlias = split(budgetContactEmail, '@')[0]

var tags = {
  'azd-env-name': environmentName
  demo: 'true'
  owner: ownerAlias
  partner: partnerName
  'cost-center': 'eps-ai-demos'
}

resource rg 'Microsoft.Resources/resourceGroups@2024-11-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

resource foundryRg 'Microsoft.Resources/resourceGroups@2024-11-01' existing = {
  name: foundryResourceGroupName
}

resource foundry 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  scope: foundryRg
  name: foundryAccountName
}

module resources 'resources.bicep' = {
  name: 'resources'
  scope: rg
  params: {
    location: location
    tags: tags
    monthlyBudgetUsd: monthlyBudgetUsd
    budgetContactEmail: budgetContactEmail
    foundryEndpoint: foundry.properties.endpoint
  }
}

// Cross-resource-group grant: the app lives in rg-${environmentName}, the models
// it calls do not. Deployed at the Foundry group's scope for that reason.
module foundryAccess 'modules/foundry-access.bicep' = {
  name: 'foundry-access'
  scope: foundryRg
  params: {
    foundryAccountName: foundryAccountName
    appPrincipalId: resources.outputs.webAppPrincipalId
    developerPrincipalId: principalId
    grantDeveloperAccess: grantDeveloperAccess
  }
}

output RESOURCE_GROUP_NAME string = rg.name
output AZURE_LOCATION string = location
output APPLICATIONINSIGHTS_CONNECTION_STRING string = resources.outputs.appInsightsConnectionString
output LOG_ANALYTICS_WORKSPACE_ID string = resources.outputs.logAnalyticsWorkspaceId
output AZURE_AI_ENDPOINT string = foundry.properties.endpoint
output WEB_APP_NAME string = resources.outputs.webAppName
output WEB_APP_URI string = resources.outputs.webAppUri
