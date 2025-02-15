#!/bin/bash

# Get ACR credentials and save them to environment variables
ACR_NAME="PTR033cxCR"
ACR_REGION="westus2"

echo "Registering Microsoft.ContainerInstance provider..."
az provider register --namespace Microsoft.ContainerInstance

# Get the credentials from Azure
echo "Getting ACR credentials..."
CREDS=$(az acr credential show --name $ACR_NAME)

# Extract username and password
export ACR_USERNAME=$(echo $CREDS | jq -r '.username')
export ACR_PASSWORD=$(echo $CREDS | jq -r '.passwords[0].value')

# Load environment variables from .env file and format them for az container create
ENV_VARS=""
while IFS='=' read -r key value; do
    # Skip empty lines and comments
    if [[ -z "$key" ]] || [[ "$key" == \#* ]]; then
        continue
    fi
    # Remove any surrounding quotes from the value
    value=$(echo "$value" | tr -d '"'"'")
    ENV_VARS="$ENV_VARS $key=$value"
done < .env

# Create the container instance
az container create \
  --resource-group PTR03-RG \
  --name 3cx-scraper-job \
  --image ptr033cxcr.azurecr.io/3cx-scraper:latest \
  --cpu 1 \
  --memory 1 \
  --location $ACR_REGION \
  --registry-login-server ptr033cxcr.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --restart-policy Never \
  --os-type Linux \
  --environment-variables $ENV_VARS
