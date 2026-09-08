// Grants model-inference access on an AI Foundry account that already exists,
// in whatever resource group holds it (see docs/adr/0008). Deployed at the
// scope of that resource group, so it is a separate module from resources.bicep.
targetScope = 'resourceGroup'

@description('Name of the existing AI Foundry / Cognitive Services account.')
param foundryAccountName string

@description('Object ID of the web app managed identity.')
param appPrincipalId string

@description('Object ID of the signed-in developer, so local runs use the same rights as the deployed app.')
param developerPrincipalId string

@description('Set false for hardened or CI environments where no human should hold data-plane rights.')
param grantDeveloperAccess bool

// Cognitive Services User: enough to call model deployments, not to manage them.
var cognitiveServicesUser = 'a97b65f3-24c7-4388-baec-2e87135dc908'

resource foundry 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: foundryAccountName
}

module appGrant 'role-assignment.bicep' = {
  name: 'foundry-grant-app'
  params: {
    scopeResourceId: foundry.id
    principalId: appPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: cognitiveServicesUser
  }
}

// Same module, same role, different principal — the developer running `make dev`
// locally authenticates with `az login` and must reach exactly what the app reaches.
module developerGrant 'role-assignment.bicep' = if (grantDeveloperAccess && !empty(developerPrincipalId)) {
  name: 'foundry-grant-developer'
  params: {
    scopeResourceId: foundry.id
    principalId: developerPrincipalId
    principalType: 'User'
    roleDefinitionId: cognitiveServicesUser
  }
}

output foundryEndpoint string = foundry.properties.endpoint
