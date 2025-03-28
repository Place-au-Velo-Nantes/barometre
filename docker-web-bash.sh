#!/bin/bash

cd docker
CONTAINER_ID=$(docker ps -qf "name=docker-barometre_web")
if [ ! -z "$CONTAINER_ID" ]; then
  echo "Container is already running.  Attaching shell..."
  docker exec -ti "$CONTAINER_ID" /bin/bash
else
  echo "Container is not running.  Starting the container in shell mode..."
  docker compose run --rm barometre_web /bin/bash
fi
