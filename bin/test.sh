#!/bin/bash
container=$(docker run -p 9000:8080 --detach booker-scraper:latest)

# Invoke the function
curl "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{}'
echo ""

docker stop "$container" > /dev/null 2>&1
docker rm "$container" > /dev/null 2>&1

docker ps -a