#!/bin/bash
docker tag booker-scraper:latest 281172820522.dkr.ecr.us-east-1.amazonaws.com/booker-scraper:latest
docker push 281172820522.dkr.ecr.us-east-1.amazonaws.com/booker-scraper:latest
aws lambda update-function-code --function-name booker-scraper-lambda --image-uri 281172820522.dkr.ecr.us-east-1.amazonaws.com/booker-scraper:latest --profile shf > /dev/null 2>&1