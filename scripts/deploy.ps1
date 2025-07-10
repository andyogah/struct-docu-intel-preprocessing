# Define mandatory parameters for the deployment
param
(
    [Parameter(Mandatory = $true)][string]$DeploymentName,
    [Parameter(Mandatory = $true)]
    [string]$Location
)

# Login to Azure
Write-Host "Checking if logged in to Azure..."

# Check if the user is logged in to Azure
$loggedIn = az account show --query "name" -o tsv

# If logged in, display the account name, otherwise prompt for login
if ($loggedIn) {
    Write-Host "Already logged in as $loggedIn"
} else {
    Write-Host "Logging in..."
    az login
}

# Retrieve the default subscription ID
$subscriptionId = (
    (
        az account list -o json `
            --query "[?isDefault]"
    ) | ConvertFrom-Json
).id

# Set the subscription to the default subscription ID
az account set --subscription $subscriptionId
Write-Host "Subscription set to $subscriptionId"

Write-Host "Deploying infrastructure..."

# Change the working directory to the script's root directory
Write-Host "Changing the working directory to the script's root directory..."
Set-Location -Path $PSScriptRoot

# Change the working directory to the infras directory
Write-Host "Changing the working directory to the infras directory..."
$parentDir = Split-Path -Path $PSScriptRoot -Parent
Set-Location -Path (Join-Path -Path $parentDir -ChildPath 'infras')

# Display the Azure CLI version
az --version

# Deploy the infrastructure using a Bicep template and parameters file
$deploymentOutputs = (az deployment sub create --name $DeploymentName --location $Location --template-file './main.bicep' --parameters './parameter.json' --parameters workloadName=$DeploymentName --parameters location=$Location --query 'properties.outputs' -o json) | ConvertFrom-Json

# Save the deployment outputs to a JSON file
$deploymentOutputs | ConvertTo-Json | Out-File -FilePath './infraOutputs.json' -Encoding utf8

# Extract various outputs from the deployment
$resourceGroupName = $deploymentOutputs.resourceGroupInfo.value.name
$documentIntelligenceName = $deploymentOutputs.documentIntelligenceInfo.value.name
$documentIntelligenceEndpoint = $deploymentOutputs.documentIntelligenceInfo.value.endpoint
$documentIntelligencePrimaryKey = (az cognitiveservices account keys list --name $documentIntelligenceName --resource-group $resourceGroupName --query 'key1' -o tsv)
$openAIName = $deploymentOutputs.aiInfo.value.name
$openAIEndpoint = $deploymentOutputs.aiInfo.value.endpoint
$openAIModelDeploymentName = $deploymentOutputs.aiInfo.value.modelDeploymentName
$openAIKey = (az cognitiveservices account keys list --name $openAIName --resource-group $resourceGroupName --query key1 -o tsv)

# Save the deployment outputs to a config.env file
Write-Host "Saving the deployment outputs to a config.env file..."

# Function to update or add variables in a configuration file
function Set-ConfigurationFileVariable($configurationFile, $variableName, $variableValue) {
    if (Select-String -Path $configurationFile -Pattern $variableName) {
        (Get-Content $configurationFile) | Foreach-Object {
            $_ -replace "$variableName = .*", "$variableName = $variableValue"
        } | Set-Content $configurationFile
    }
    else {
        Add-Content -Path $configurationFile -value "$variableName = $variableValue"
    }
}

# Define the configuration file path
$configurationFile = "config.env"

# Create the configuration file if it doesn't exist
if (-not (Test-Path $configurationFile)) {
    New-Item -Path $configurationFile -ItemType "file" -Value ""
}

# Set variables in the configuration file
Set-ConfigurationFileVariable $configurationFile "AZURE_RESOURCE_GROUP_NAME" $resourceGroupName
Set-ConfigurationFileVariable $configurationFile "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" $documentIntelligenceEndpoint
Set-ConfigurationFileVariable $configurationFile "AZURE_DOCUMENT_INTELLIGENCE_KEY" $documentIntelligencePrimaryKey
Set-ConfigurationFileVariable $configurationFile "AZURE_OPENAI_ENDPOINT" $openAIEndpoint
Set-ConfigurationFileVariable $configurationFile "AZURE_OPENAI_API_KEY" $openAIKey
Set-ConfigurationFileVariable $configurationFile "AZURE_OPENAI_MODEL_DEPLOYMENT_NAME" $openAIModelDeploymentName

# Return the deployment outputs
return $deploymentOutputs

# Call the script with the required parameters to deploy the infrastructure
# .\deploy.ps1 -DeploymentName "myDeployment" -Location "eastus"
# The script will deploy the infrastructure using the Bicep template and parameters file