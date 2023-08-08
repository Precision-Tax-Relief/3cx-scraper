#!/bin/bash
docker tag booker-scraper:latest 515970055937.dkr.ecr.us-west-2.amazonaws.com/booker-scraper:latest
docker push 515970055937.dkr.ecr.us-west-2.amazonaws.com/booker-scraper:latest
aws lambda update-function-code --function-name booker-scraper --image-uri 515970055937.dkr.ecr.us-west-2.amazonaws.com/booker-scraper:latest  > /dev/null 2>&1