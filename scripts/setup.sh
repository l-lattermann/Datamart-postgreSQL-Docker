#!/bin/zsh

set -e

mkdir -p logs
exec > >(tee -a logs/app.log) 2>&1

echo ""
echo "=== Installing required components ==="
brew install colima
brew install docker
brew install docker-compose

echo ""
echo "=== Loading environment ==="
set -a
source .env
set +a

echo ""
echo "=== Checking Colima VM status for profile: $COLIMA_PROFILE ==="
if colima status "$COLIMA_PROFILE" 2>&1 | grep -qi "not running"; then
    echo "-> Colima $COLIMA_PROFILE is not running."
    if colima list 2>&1 | grep -qi "$COLIMA_PROFILE"; then
        echo "-> Colima $COLIMA_PROFILE exists. Restarting..."
        colima restart "$COLIMA_PROFILE"
    else
        echo "-> Colima $COLIMA_PROFILE not found. Creating..."
        colima start --profile "$COLIMA_PROFILE" --cpu "$CPU" --memory "$MEM" --disk "$DISK"
    fi
else
    echo "-> Colima $COLIMA_PROFILE is already running."
fi

echo ""
echo "=== Colima Status Summary ==="
colima status "$COLIMA_PROFILE"

echo ""
echo "=== Waiting for Docker daemon ==="
until docker info >/dev/null 2>&1; do
    echo "Waiting for Docker daemon to become ready..."
    sleep 2
done

echo ""
echo "=== Checking Docker Container: $DOCKER_PROFILE ==="
if docker ps --format '{{.Names}}' | grep -qx "$DOCKER_PROFILE"; then
    echo "-> $DOCKER_PROFILE is already running."
else
    echo "-> $DOCKER_PROFILE is not running."

    echo ""
    echo "=== Checking Docker Context ==="
    docker context ls
    docker info | head -n 5

    echo ""
    echo "=== Checking for Orphaned Docker Volumes ==="
    if docker volume ls --format '{{.Name}}' 2>/dev/null | grep -qx "$PG_VOLUME_NAME"; then
        echo "-> Orphaned volume \"$PG_VOLUME_NAME\" found. Deleting..."
        if ! docker volume rm -f "$PG_VOLUME_NAME"; then
            echo "-> Volume is in use. Removing container and retrying..."
            docker stop "$DOCKER_PROFILE" 2>/dev/null || true
            docker rm "$DOCKER_PROFILE" 2>/dev/null || true
            docker volume rm -f "$PG_VOLUME_NAME"
        fi
    else
        echo "-> No orphaned volumes found."
    fi

    echo ""
    echo "=== Starting Docker Compose ==="
    docker-compose -f "$YML_FILE" up -d
fi

echo ""
echo "=== Final Colima Status ==="
colima list

echo ""
echo "=== Final Docker Status ==="
docker info | head -n 20

echo ""
echo "=== Current Docker Volumes ==="
docker volume ls

echo ""
echo "=== Recreating Python virtual environment ==="
if [ -d ".venv" ]; then
    echo "-> Removing existing .venv..."
    rm -rf .venv || {
        echo "ERROR: Failed to remove existing .venv"
        exit 1
    }
fi

echo "-> Creating new .venv..."
python3 -m venv .venv || {
    echo "ERROR: Failed to create .venv"
    exit 1
}

echo "-> Installing requirements..."
.venv/bin/python -m pip install --upgrade pip || {
    echo "ERROR: Failed to upgrade pip"
    exit 1
}

.venv/bin/python -m pip install -r requirements.txt || {
    echo "ERROR: Failed to install requirements.txt"
    exit 1
}

echo "-> Python virtual environment ready."

echo ""
echo "=== Running Database Connection Test ==="
sleep 3

MAX_RETRIES=5
COUNTER=1

until .venv/bin/python "$DB_CONN_TEST"; do
    if [ "$COUNTER" -ge "$MAX_RETRIES" ]; then
        echo "ERROR: Database could not be reached after $MAX_RETRIES attempts."
        exit 1
    fi

    echo "-> DB unreachable. Restarting \"$DOCKER_PROFILE\" (attempt $COUNTER/$MAX_RETRIES)..."
    docker restart "$DOCKER_PROFILE"
    docker port "$DOCKER_PROFILE"
    sleep 2
    COUNTER=$((COUNTER + 1))
done

echo "-> Database reachable, container is up!"

echo "=== Initializing Database and gernerating Dummydata ==="
.venv/bin/python src/main.py

echo "=== Running PyTest ==="
pytest . 

echo "============================================="
echo "======== Setup Finished Successfully ========"
echo "============================================="