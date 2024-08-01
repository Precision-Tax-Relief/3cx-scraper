#!/bin/bash
PAYLOAD=$(echo -n '{"task": "appointment_map"}' | base64)
aws lambda invoke --function-name booker-scraper --payload "$PAYLOAD" response.json --log-type Tail --query 'LogResult' --output text |  base64 -d