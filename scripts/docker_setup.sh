#!/bin/zsh

# Install Colima and Docker
brew install colima
brew install docker
brew install docker-compose

# --- Configuration ---
# Import variables from .env
set -e
set -a
source scratches/postgres_poc/.env
set +a

# Colima
COLIMA_PROFILE=$COLIMA_PROFILE
CPU=$CPU
MEM=$MEM
DISK=$DISK

# Docker
YML_FILE="./scratches/postgres_poc/docker-compose.yml"
DOCKER_PROFILE="postgres_db"

# --- Check if Colima is running ---
echo ""
echo "=== Checking $COLIMA_PROFILEc Colima-VM status=="
# If VM is not running
if colima status "$COLIMA_PROFILE" 2>&1 | grep -qi "not running"; then
    echo "-> Colima $COLIMA_PROFILE is not running.."
    # If VM is not running but exists
    if colima list 2>&1| grep -qi "$COLIMA_PROFILE"; then
        echo "-> Colima $COLIMA_PROFILE exist. Restarting it..."
        colima restart "$COLIMA_PROFILE"
    # If VM is not running and does not exist
    else
        echo "-> Colima $COLIMA_PROFILE does not exist. Creating it..."
        colima start --profile "$COLIMA_PROFILE" --cpu "$CPU" --memory "$MEM" --disk "$DISK"
    fi
# If VM is running
else
    echo "-> Colima $COLIMA_PROFILE is running."
fi
# Final Colima status check 
echo ""
echo "== Colima status =="
colima status $COLIMA_PROFILE
#colima stop postgre && colima delete -f postgre 

# --- Check if Docker Container is running ---
echo ""
echo "=== Checking $DOCKER_PROFILE Docker Cointainer status=="
# Docker container is running
if docker ps | grep -qi "$DOCKER_PROFILE"; then
    echo "-> $DOCKER_PROFILE Container is running"
else 
    echo "-> $DOCKER_PROFILE Container is not running"
    echo "-> Starting $DOCKER_PROFILE from $YML_FILE"
    # Wait for Docker daemon socket inside Colima to be available
    until docker info >/dev/null 2>&1; do
    echo "Waiting for Docker daemon..."
    sleep 2
    done
    docker-compose -f "$YML_FILE" up -d
fi

# --- Final Colima status check ---
echo ""
echo "== Colima status =="
colima list

# --- Final Docker status check ---
echo ""
echo "== Docker status =="
docker info

# --- DB connection test ---
echo ""
echo ""
echo "== DB Test =="
sleep 3
if python3 "$DB_CONN_TEST" 2>&1 | grep -iq "Connection refused"; then
    COUNTER=1
    until python3 "$DB_CONN_TEST" | grep -iq "Connection refused"
    do
        echo "DB test failed. Connection to Container refused."
        echo "Restaring Docker Container \"$DOCKER_PROFILE\" to get right port mapping. Try No.: \"$COUNTER\""
        docker restart "$DOCKER_PROFILE"
        docker port "$DOCKER_PROFILE"
        sleep 2
        COUNTER=$((COUNTER + 1))
        [ "$COUNTER" -gt 5 ] && break
    done
else
    echo "-> Conatiner is reachable, DB is up!"
    python3 "$DB_CONN_TEST"
fi

echo ""
echo ""
echo "======== Setup finished ========"