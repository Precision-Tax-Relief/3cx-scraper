#!/bin/bash

echo "Deleting container..."
az container delete --name 3cx-scraper-job --resource-group PTR03-RG -y
