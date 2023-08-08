#!/bin/bash
container=$(docker run -p 9000:8080 --detach --cpus=1 --memory=2048m booker-scraper:latest)

# Invoke the function
curl "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{}'
echo ""

docker logs "$container"
docker stop "$container" > /dev/null 2>&1
docker rm "$container" > /dev/null 2>&1

docker ps -a