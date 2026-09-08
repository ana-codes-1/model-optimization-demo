// Shared role-assignment module (eps-demo-architecture). Every data-plane grant
// in this repo goes through this file, invoked once for the app's managed
// identity and once for the signed-in developer, so the two can never drift.
//
// The assignment is scoped to the Foundry *account*, not to its resource group.
// A role assignment without an explicit `scope` inherits the deployment scope,
// which would silently widen every grant to the whole group and to any other
// Cognitive Services account that happens to live in it.
targetScope = 'resourceGroup'

@description('Name of the existing AI Foundry account the role is granted on. Must live in this module\'s target resource group.')
@minLength(2)
param foundryAccountName string

@description('Object ID of the principal receiving the role.')
param principalId string

@description('ServicePrincipal for a managed identity, User for a signed-in developer. Getting this wrong makes the assignment fail against a freshly created identity.')
@allowed(['ServicePrincipal', 'User'])
param principalType string

@description('Role definition GUID, not the full resource ID.')
param roleDefinitionId string

resource foundry 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: foundryAccountName
}

resource assignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: foundry
  // Deterministic name keeps redeploys idempotent instead of conflicting.
  name: guid(foundry.id, principalId, roleDefinitionId)
  properties: {
    principalId: principalId
    principalType: principalType
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionId)
  }
}

output scopeResourceId string = foundry.id
