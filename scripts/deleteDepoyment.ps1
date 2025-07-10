# Define mandatory parameters for the deletion
param
(
    [Parameter(Mandatory = $true)][string]$ResourceGroupName
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

# Function to delete the deployment by removing the resource group
function Delete-Deployment {
    param (
        [string]$ResourceGroupName
    )
    Write-Host "Deleting resource group $ResourceGroupName..."
    az group delete --name $ResourceGroupName --yes --no-wait
    Write-Host "Resource group $ResourceGroupName deletion initiated."
}

# Call the function to delete the deployment
Delete-Deployment -ResourceGroupName $ResourceGroupName

# call the script with the required parameters to delete the deployment
# .\deleteDeployment.ps1 -ResourceGroupName "rg-testtest"
