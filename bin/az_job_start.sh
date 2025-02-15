#!/bin/bash

echo "Starting container..."
az container start \
  --resource-group PTR03-RG \
  --name 3cx-scraper-job
  
echo "Getting status..."
az container show \
  --resource-group PTR03-RG \
  --name 3cx-scraper-job