// Resource-group-scoped guardrails: budget + observability, plus the App Service
// that hosts this demo (docs/adr/0007 explains why App Service rather than the
// Static Web Apps + Functions default in eps-demo-architecture).
//
// Data-plane RBAC for AI Foundry lives in modules/foundry-access.bicep, because
// the Foundry account sits in a different resource group (docs/adr/0008). Both
// the app identity and the developer principal are granted through the single
// shared modules/role-assignment.bicep, so the two can never drift.
// Private Link stays opt-in per docs/adr/0003 — see the gap table in docs/README.md.
targetScope = 'resourceGroup'

@description('Location for all resources.')
param location string

@description('Tags applied to every resource (demo/owner/partner/cost-center + azd-env-name).')
param tags object

@description('Monthly budget (USD) for this resource group.')
param monthlyBudgetUsd int

@description('Email for budget + cost alerts.')
param budgetContactEmail string

@description('AI Foundry endpoint the app calls for every model in the roster.')
param foundryEndpoint string

@description('azd environment name. Used verbatim as the web app name, so the public hostname is <environmentName>.azurewebsites.net — a name you can say out loud on stage (docs/adr/0007). Must be globally unique.')
param environmentName string

@description('App Service plan SKU. B1 is the smallest tier that stays warm between demos; a cold start is a bad look on stage.')
param appServiceSku string = 'B1'

@description('Start date for the budget period (first of month). Left as a param so it is computed once at first deploy, not recomputed (and invalidated) on every redeploy.')
param budgetStartDate string = utcNow('yyyy-MM-01')

var resourceToken = uniqueString(resourceGroup().id)
var appInsightsName = 'appi-${resourceToken}'
var logAnalyticsName = 'log-${resourceToken}'

// ------------------------------------------------------------------ Budget
// Cost guardrail per eps-demo-cost-security — wired up regardless of what
// else this demo needs.
resource budget 'Microsoft.Consumption/budgets@2023-05-01' = {
  name: 'budget-${resourceGroup().name}'
  properties: {
    category: 'Cost'
    amount: monthlyBudgetUsd
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: budgetStartDate
    }
    notifications: {
      actual_80pct: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 80
        thresholdType: 'Actual'
        contactEmails: [budgetContactEmail]
      }
      forecasted_100pct: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 100
        thresholdType: 'Forecasted'
        contactEmails: [budgetContactEmail]
      }
    }
  }
}

// ------------------------------------------------------------ Observability
// App Insights + Log Analytics are compute-agnostic — point whatever compute
// gets added (Functions, Container Apps, App Service, ...) at these
// (eps-demo-repo-hygiene: "App Insights with PII scrubbed").
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

output appInsightsConnectionString string = appInsights.properties.ConnectionString
output logAnalyticsWorkspaceId string = logAnalytics.id

// ------------------------------------------------------------------ Compute
// Linux App Service running the stdlib Python server directly — no container
// registry, no build step. See docs/adr/0007.
resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'plan-${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: appServiceSku
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource web 'Microsoft.Web/sites@2023-12-01' = {
  // Named from the azd environment rather than a hash: this URL gets read out
  // to partners, and "app-h4k2mn7q3.azurewebsites.net" is not a URL you can say.
  name: environmentName
  location: location
  // azd matches this tag to the service in azure.yaml to know where to deploy.
  tags: union(tags, { 'azd-service-name': 'web' })
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      // The app is standard library only, so there is nothing to build on deploy.
      appCommandLine: 'python server.py'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      http20Enabled: true
      alwaysOn: true
      appSettings: [
        {
          name: 'AZURE_AI_ENDPOINT'
          value: foundryEndpoint
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'false'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
      ]
    }
  }
}

output webAppName string = web.name
output webAppUri string = 'https://${web.properties.defaultHostName}'
output webAppPrincipalId string = web.identity.principalId
