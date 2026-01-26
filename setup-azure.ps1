# Setup Azure and GitHub for deployment
# This script creates Azure resources and configures GitHub secrets for OIDC authentication
#
# Prerequisites:
#   - Azure CLI (az) - logged in with `az login`
#   - GitHub CLI (gh) - logged in with `gh auth login`
#
# Usage: .\setup-azure.ps1 -GitHubRepo "org/repo" [-ResourceGroup "rg-name"] [-Location "eastus"]

param(
  [Parameter(Mandatory = $true)]
  [string]$GitHubRepo,

  [string]$ResourceGroup = "fastapi-react-aspire-rg",

  [string]$Location = "eastus",

  [string]$AppName = "fastapi-react-aspire-deploy"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up Azure and GitHub for deployment..." -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
function Test-CommandExists {
  param($Command, $InstallHint)
  if (!(Get-Command $Command -ErrorAction SilentlyContinue)) {
    Write-Host "❌ $Command is not installed. $InstallHint" -ForegroundColor Red
    exit 1
  }
}

Test-CommandExists "az" "Install from: https://docs.microsoft.com/cli/azure/install-azure-cli"
Test-CommandExists "gh" "Install from: https://cli.github.com/"

# Verify Azure login
Write-Host "Checking Azure login..." -ForegroundColor Cyan
$account = az account show 2>$null | ConvertFrom-Json
if (!$account) {
  Write-Host "Please log in to Azure:" -ForegroundColor Yellow
  az login
  $account = az account show | ConvertFrom-Json
}
$SubscriptionId = $account.id
$TenantId = $account.tenantId
Write-Host "✅ Logged in to Azure (Subscription: $SubscriptionId)" -ForegroundColor Green

# Verify GitHub login
Write-Host "Checking GitHub login..." -ForegroundColor Cyan
$null = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Host "Please log in to GitHub:" -ForegroundColor Yellow
  gh auth login
}
Write-Host "✅ Logged in to GitHub" -ForegroundColor Green

# Create resource group if it doesn't exist
Write-Host ""
Write-Host "Creating resource group '$ResourceGroup' in '$Location'..." -ForegroundColor Cyan
az group create --name $ResourceGroup --location $Location --output none 2>$null
Write-Host "✅ Resource group ready" -ForegroundColor Green

# Create Azure AD application
Write-Host ""
Write-Host "Creating Azure AD application '$AppName'..." -ForegroundColor Cyan
$existingApp = az ad app list --display-name $AppName --query "[0].appId" -o tsv 2>$null

if ([string]::IsNullOrEmpty($existingApp) -or $existingApp -eq "null") {
  $AppId = az ad app create --display-name $AppName --query appId -o tsv
  Write-Host "✅ Created new Azure AD application" -ForegroundColor Green
}
else {
  $AppId = $existingApp
  Write-Host "ℹ️  Using existing Azure AD application" -ForegroundColor Yellow
}

# Create service principal if it doesn't exist
Write-Host ""
Write-Host "Creating service principal..." -ForegroundColor Cyan
$existingSp = az ad sp list --filter "appId eq '$AppId'" --query "[0].id" -o tsv 2>$null

if ([string]::IsNullOrEmpty($existingSp) -or $existingSp -eq "null") {
  $null = az ad sp create --id $AppId --query id -o tsv
  Write-Host "✅ Created service principal" -ForegroundColor Green
}
else {
  Write-Host "ℹ️  Using existing service principal" -ForegroundColor Yellow
}

# Create federated credential for GitHub Actions
Write-Host ""
Write-Host "Creating federated credential for GitHub Actions..." -ForegroundColor Cyan
$CredentialName = "github-actions-main"

$existingCred = az ad app federated-credential list --id $AppId --query "[?name=='$CredentialName'].name" -o tsv 2>$null

if ([string]::IsNullOrEmpty($existingCred)) {
  $credParams = @{
    name      = $CredentialName
    issuer    = "https://token.actions.githubusercontent.com"
    subject   = "repo:${GitHubRepo}:ref:refs/heads/main"
    audiences = @("api://AzureADTokenExchange")
  } | ConvertTo-Json -Compress

  az ad app federated-credential create --id $AppId --parameters $credParams --output none
  Write-Host "✅ Created federated credential for main branch" -ForegroundColor Green
}
else {
  Write-Host "ℹ️  Federated credential already exists" -ForegroundColor Yellow
}

# Assign Contributor role to the service principal
Write-Host ""
Write-Host "Assigning Contributor role to service principal..." -ForegroundColor Cyan
az role assignment create `
  --assignee $AppId `
  --role "Contributor" `
  --scope "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup" `
  --output none 2>$null
Write-Host "✅ Role assignment ready" -ForegroundColor Green

# Configure GitHub secrets
Write-Host ""
Write-Host "Configuring GitHub repository secrets..." -ForegroundColor Cyan

gh secret set AZURE_CLIENT_ID --repo $GitHubRepo --body $AppId
Write-Host "✅ Set AZURE_CLIENT_ID" -ForegroundColor Green

gh secret set AZURE_TENANT_ID --repo $GitHubRepo --body $TenantId
Write-Host "✅ Set AZURE_TENANT_ID" -ForegroundColor Green

gh secret set AZURE_SUBSCRIPTION_ID --repo $GitHubRepo --body $SubscriptionId
Write-Host "✅ Set AZURE_SUBSCRIPTION_ID" -ForegroundColor Green

gh secret set AZURE_RESOURCE_GROUP --repo $GitHubRepo --body $ResourceGroup
Write-Host "✅ Set AZURE_RESOURCE_GROUP" -ForegroundColor Green

gh secret set AZURE_LOCATION --repo $GitHubRepo --body $Location
Write-Host "✅ Set AZURE_LOCATION" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Azure Resources:"
Write-Host "  • Subscription:     $SubscriptionId"
Write-Host "  • Tenant:           $TenantId"
Write-Host "  • Resource Group:   $ResourceGroup"
Write-Host "  • App Registration: $AppName (ID: $AppId)"
Write-Host ""
Write-Host "GitHub Secrets configured in " -NoNewline
Write-Host "$GitHubRepo" -ForegroundColor Cyan -NoNewline
Write-Host ":"
Write-Host "  • AZURE_CLIENT_ID"
Write-Host "  • AZURE_TENANT_ID"
Write-Host "  • AZURE_SUBSCRIPTION_ID"
Write-Host "  • AZURE_RESOURCE_GROUP"
Write-Host "  • AZURE_LOCATION"
Write-Host ""
Write-Host "To deploy, push to main branch or manually trigger the deploy workflow." -ForegroundColor Yellow
