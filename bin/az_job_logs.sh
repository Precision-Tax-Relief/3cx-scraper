#!/bin/bash

echo "Getting Logs..."
az container logs \
  --resource-group PTR03-RG \
  --name 3cx-scraper-job
