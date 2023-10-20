#!/bin/bash
rm -rf segment
cp -r /Users/logan/rufsoft/analytics-python/segment segment

docker-compose down
docker-compose build
docker-compose up -d

sleep 1

# Invoke the function
curl "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{"task": "daily"}'
echo ""

docker-compose logs -f

docker-compose down

docker ps -a