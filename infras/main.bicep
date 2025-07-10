targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the workload which is used to generate a short unique hash used in all resources.')
param workloadName string

@minLength(1)
@description('Primary location for all resources.')
param location string

@description('Name of the resource group. If empty, a unique name will be generated.')
param resourceGroupName string = ''

@description('Tags for all resources.')
param tags object = {
  WorkloadName: workloadName
  Environment: 'Dev'
}

var abbrs = loadJsonContent('./abbrs.json')
var roles = loadJsonContent('./roles.json')
var resourceToken = toLower(uniqueString(subscription().id, workloadName, location))

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.managementGovernance.resourceGroup}${workloadName}'
  location: location
  tags: union(tags, {})
}

module documentIntelligence './core/docuIntel.bicep' = {
  name: '${abbrs.ai.documentIntelligence}${resourceToken}'
  scope: resourceGroup
  params: {
    name: '${abbrs.ai.documentIntelligence}${resourceToken}'
    location: location
    tags: union(tags, {})
  }
}

var modelDeploymentName = 'gpt-4o'

var aiServiceName = '${abbrs.ai.aiServices}${resourceToken}'
module aiServices './core/aiServices.bicep' = {
  //name: !empty(openAIServiceName) ? openAIServiceName : '${abbrs.openAIService}${resourceToken}'
  name: aiServiceName
  scope: resourceGroup
  params: {
    name: aiServiceName
    location: location
    tags: union(tags, {})
    deployments: [
      {
        name: modelDeploymentName
        model: {
          format: 'OpenAI'
          name: 'gpt-4o'
          version: '2024-11-20'                   
        }
        sku: {
          name: 'GlobalStandard'
          capacity: 10
        }        
      }
    ]
  }
}

module docuIntelRoleAssignments './roleAssignment.bicep' = {
  name: 'docuIntelRoleAssignments'
  scope: resourceGroup
  params: {
    principalId: documentIntelligence.outputs.principalId
    //roleDefinitionId: roles.ai.cognitiveServicesContributor  // Role definition for accessing OpenAI
    roleDefinitionId: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/${roles.ai.cognitiveServicesContributor}'  // Role definition for accessing OpenAI
    scope: aiServices.outputs.id
  }
}

module aiServicesRoleAssignments './roleAssignment.bicep' = {
  name: 'aiServicesRoleAssignments'
  scope: resourceGroup
  params: {
    principalId: aiServices.outputs.principalId
    //roleDefinitionId: roles.ai.cognitiveServicesContributor  // Role definition for accessing Document Intelligence
    roleDefinitionId: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/${roles.ai.cognitiveServicesContributor}'  // Role definition for accessing Document Intelligence
    scope: documentIntelligence.outputs.id
  }
}

output resourceGroupInfo object = {
  id: resourceGroup.id
  name: resourceGroup.name
  location: resourceGroup.location
}

output aiInfo object = {
  id: aiServices.outputs.id
  name: aiServices.outputs.name
  endpoint: aiServices.outputs.endpoint
  modelDeploymentName: modelDeploymentName
}

output documentIntelligenceInfo object = {
  id: documentIntelligence.outputs.id
  name: documentIntelligence.outputs.name
  endpoint: documentIntelligence.outputs.endpoint
  host: documentIntelligence.outputs.host
}
