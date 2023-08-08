#!/bin/bash
container=$(docker run -p 9000:8080 --detach booker-scraper:latest)
docker exec -it "$container" bash

docker stop "$container" > /dev/null 2>&1
docker rm "$container" > /dev/null 2>&1

docker ps -a