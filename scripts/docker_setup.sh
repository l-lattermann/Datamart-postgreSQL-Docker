#!/bin/zsh
# ============================================================
# SETUP: COLIMA + DOCKER + DB CONNECTIVITY CHECK
# Purpose:
# - install colima/docker/docker-compose (if missing)
# - start or create Colima VM with given profile
# - start Docker container from compose file
# - clean orphaned pg volumes (optional)
# - run Python DB connection test
# ============================================================

# ------------------------------------------------------------
# unified logging to logs/app.log
# ------------------------------------------------------------
exec > >(tee -a logs/app.log) 2>&1

# ============================================================
# 1) INSTALLATION
# ============================================================
# Install required components if missing
brew install colima
brew install docker
brew install docker-compose

# ============================================================
# 2) CONFIGURATION
# ============================================================
# import environment from .env (fails fast on error)
set -e
set -a
source .env
set +a

# Colima
COLIMA_PROFILE=$COLIMA_PROFILE
CPU=$CPU
MEM=$MEM
DISK=$DISK

# Docker
YML_FILE=$YML_FILE
DOCKER_PROFILE=$DOCKER_PROFILE

# ============================================================
# 3) COLIMA LIFECYCLE
# ============================================================
echo ""
echo "=== Checking Colima VM status for profile: $COLIMA_PROFILE ==="

# VM not running
if colima status "$COLIMA_PROFILE" 2>&1 | grep -qi "not running"; then
    echo "-> Colima $COLIMA_PROFILE is not running."

    # VM exists → restart
    if colima list 2>&1 | grep -qi "$COLIMA_PROFILE"; then
        echo "-> Colima $COLIMA_PROFILE exists. Restarting..."
        colima restart "$COLIMA_PROFILE"
    # VM does not exist → create
    else
        echo "-> Colima $COLIMA_PROFILE not found. Creating..."
        colima start --profile "$COLIMA_PROFILE" --cpu "$CPU" --memory "$MEM" --disk "$DISK"
    fi

# VM already running
else
    echo "-> Colima $COLIMA_PROFILE is already running."
fi

# show status
echo ""
echo "=== Colima Status Summary ==="
colima status "$COLIMA_PROFILE"

# ============================================================
# 4) DOCKER CONTEXT + VOLUMES
# ============================================================
echo ""
echo "=== Checking Docker Context ==="
docker context ls
docker info | head -n 5

echo ""
echo "=== Checking for Orphaned Docker Volumes ==="
if docker volume ls --format '{{.Name}}' 2>/dev/null | grep -iq "$PG_VOLUME_NAME"; then
    echo "-> Orphaned volume \"$PG_VOLUME_NAME\" found. Deleting..."
    docker volume rm -f "$PG_VOLUME_NAME"
    echo "-> Remaining Docker volumes:"
    docker volume ls
else
    echo "-> No orphaned volumes found."
fi

# ============================================================
# 5) CONTAINER START
# ============================================================
echo ""
echo "=== Checking Docker Container: $DOCKER_PROFILE ==="

# container already running
if docker ps | grep -qi "$DOCKER_PROFILE"; then
    echo "-> $DOCKER_PROFILE is already running."
# container not running → start
else
    echo "-> $DOCKER_PROFILE is not running."
    echo "-> Starting using compose file: $YML_FILE"

    # wait for docker inside Colima
    until docker info >/dev/null 2>&1; do
        echo "Waiting for Docker daemon to become ready..."
        sleep 2
    done

    docker-compose -f "$YML_FILE" up -d
fi

# ============================================================
# 6) FINAL RUNTIME STATUS
# ============================================================
echo ""
echo "=== Final Colima Status ==="
colima list

echo ""
echo "=== Final Docker Status ==="
docker info

echo ""
echo "=== Current Docker Volumes ==="
docker volume ls

# ============================================================
# 7) DATABASE CONNECTION TEST
# ============================================================
echo ""
echo "=== Running Database Connection Test ==="
sleep 3

MAX_RETRIES=5
COUNTER=1

# initial attempt
if python3 "$DB_CONN_TEST"; then
    echo "-> Database reachable, container is up!"
else
    echo "-> Initial DB test failed. Will retry by restarting container..."

    # retry loop
    while ! python3 "$DB_CONN_TEST"; do
        echo "-> DB unreachable. Restarting \"$DOCKER_PROFILE\" (attempt $COUNTER/$MAX_RETRIES)..."
        docker restart "$DOCKER_PROFILE"
        docker port "$DOCKER_PROFILE"
        sleep 2
        COUNTER=$((COUNTER + 1))
        [ "$COUNTER" -gt "$MAX_RETRIES" ] && break
    done
fi

# result
if [ "$COUNTER" -gt "$MAX_RETRIES" ]; then
    echo "ERROR: Database could not be reached after $MAX_RETRIES attempts."
    exit 1
else
    echo "======== Setup Finished Successfully ========"
fi