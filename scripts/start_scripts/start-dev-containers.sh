#!/bin/bash

CONTAINERS_DIR="containers"
DOCKER_CMD="docker compose -f containers/db-messaging.docker-compose.yml --env-file containers/.env up -d"

echo "Running docker command: $DOCKER_CMD"
eval "$DOCKER_CMD"
