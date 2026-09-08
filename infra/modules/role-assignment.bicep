// Shared role-assignment module (eps-demo-architecture). Every data-plane grant
// in this repo goes through this file, invoked once for the app's managed
// identity and once for the signed-in developer, so the two can never drift.
targetScope = 'resourceGroup'

@description('Resource the role is granted on. Used only to make the assignment name deterministic; the actual scope comes from the module declaration.')
param scopeResourceId string

@description('Object ID of the principal receiving the role.')
param principalId string

@description('ServicePrincipal for a managed identity, User for a signed-in developer. Getting this wrong makes the assignment fail against a freshly created identity.')
@allowed(['ServicePrincipal', 'User'])
param principalType string

@description('Role definition GUID, not the full resource ID.')
param roleDefinitionId string

resource assignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  // Deterministic name keeps redeploys idempotent instead of conflicting.
  name: guid(scopeResourceId, principalId, roleDefinitionId)
  properties: {
    principalId: principalId
    principalType: principalType
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionId)
  }
}
