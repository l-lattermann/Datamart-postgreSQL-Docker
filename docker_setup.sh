#!/bin/zsh

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
        colima start --COLIMA_profile "$COLIMA_PROFILE" --cpu "$CPU" --memory "$MEM" --disk "$DISK"
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
    docker-compose -f "$YML_FILE" up -d
fi

# --- Final status check ---
echo ""
echo "== Docker status =="
docker ps

# --- DB connection test ---
echo ""
echo ""
echo "== DB Test =="
python3 "$DB_CONN_TEST"
