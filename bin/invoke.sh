#!/bin/bash
aws lambda invoke --function-name booker-scraper response.json --log-type Tail --query 'LogResult' --output text |  base64 -d