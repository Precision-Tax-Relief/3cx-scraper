#!/bin/bash
PAYLOAD=$(echo -n '{"task": "test"}' | base64)
aws lambda invoke --function-name booker-scraper-lambda --payload "$PAYLOAD" response.json --log-type Tail --query 'LogResult' --output text |  base64 -d