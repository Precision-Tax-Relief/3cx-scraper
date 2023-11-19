#!/bin/bash
rm -rf segment
cp -r /Users/logan/rufsoft/analytics-python/segment segment

docker-compose down
docker-compose build
docker-compose up -d

sleep 1

echo "Starting task..."
# Invoke the function
curl "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{"task": "weekly"}'
echo ""

read -n 1 -s -r -p "Press any key to continue"

docker-compose down

docker ps -a