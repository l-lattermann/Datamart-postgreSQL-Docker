#!/bin/zsh
# ============================================================
# ================ SETUP SCRIPT: COLIMA + DOCKER ===============
# ============================================================

# --- Enable unified logging (stdout + stderr to logs/app.log) ---
exec > >(tee -a logs/app.log) 2>&1

# ============================================================
# ====================== INSTALLATION =========================
# ============================================================

# Install required components if missing
brew install colima
brew install docker
brew install docker-compose


# ============================================================
# ====================== CONFIGURATION ========================
# ============================================================

# Import variables from .env
set -e
set -a
source .env
set +a

# Colima configuration
COLIMA_PROFILE=$COLIMA_PROFILE
CPU=$CPU
MEM=$MEM
DISK=$DISK

# Docker configuration
YML_FILE=$YML_FILE
DOCKER_PROFILE=$DOCKER_PROFILE


# ============================================================
# ======================== COLIMA ============================
# ============================================================

echo ""
echo "=== Checking Colima VM status for profile: $COLIMA_PROFILE ==="

# Check if Colima VM is running
if colima status "$COLIMA_PROFILE" 2>&1 | grep -qi "not running"; then
    echo "-> Colima $COLIMA_PROFILE is not running."
    
    # If the VM exists but is stopped
    if colima list 2>&1 | grep -qi "$COLIMA_PROFILE"; then
        echo "-> Colima $COLIMA_PROFILE exists. Restarting it..."
        colima restart "$COLIMA_PROFILE"

    # If the VM does not exist, create it
    else
        echo "-> Colima $COLIMA_PROFILE does not exist. Creating a new VM..."
        colima start --profile "$COLIMA_PROFILE" --cpu "$CPU" --memory "$MEM" --disk "$DISK"
    fi

# If the VM is already running
else
    echo "-> Colima $COLIMA_PROFILE is already running."
fi

# Show Colima status summary
echo ""
echo "=== Colima Status Summary ==="
colima status "$COLIMA_PROFILE"


# ============================================================
# ========================= DOCKER ===========================
# ============================================================

echo ""
echo "=== Checking Docker Context ==="
docker context ls
docker info | head -n 5

# --- Check for orphaned PostgreSQL volumes ---
echo ""
echo "=== Checking for Orphaned Docker Volumes ==="

if docker volume ls --format '{{.Name}}' 2>/dev/null | grep -iq "$PG_VOLUME_NAME"; then
    echo "-> Orphaned volume \"$PG_VOLUME_NAME\" found. Deleting it..."
    docker volume rm -f "$PG_VOLUME_NAME"
    echo "-> Remaining Docker volumes:"
    docker volume ls
else
    echo "-> No orphaned volumes found."
fi


# --- Check container status ---
echo ""
echo "=== Checking Docker Container: $DOCKER_PROFILE ==="

# If container is already running
if docker ps | grep -qi "$DOCKER_PROFILE"; then
    echo "-> $DOCKER_PROFILE container is already running."

# If container is not running, start it
else
    echo "-> $DOCKER_PROFILE container is not running."
    echo "-> Starting container using $YML_FILE ..."
    
    # Wait until Docker daemon socket inside Colima becomes available
    until docker info >/dev/null 2>&1; do
        echo "Waiting for Docker daemon to become ready..."
        sleep 2
    done
    
    # Start container via docker-compose
    docker-compose -f "$YML_FILE" up -d
fi


# ============================================================
# ====================== FINAL STATUS =========================
# ============================================================

# Show Colima and Docker runtime info
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
# ===================== DATABASE TEST =========================
# ============================================================

echo ""
echo ""
echo "=== Running Database Connection Test ==="
sleep 3

MAX_RETRIES=5
COUNTER=1

# Initial connection attempt
if python3 "$DB_CONN_TEST"; then
    echo "-> Database reachable, container is up!"
else
    echo "-> Initial DB test failed. Attempting container restart..."
    
    # Retry loop
    while ! python3 "$DB_CONN_TEST"; do
        echo "-> DB still unreachable. Restarting \"$DOCKER_PROFILE\" (attempt $COUNTER/$MAX_RETRIES)..."
        docker restart "$DOCKER_PROFILE"
        docker port "$DOCKER_PROFILE"
        sleep 2
        COUNTER=$((COUNTER + 1))
        [ "$COUNTER" -gt "$MAX_RETRIES" ] && break
    done
fi

# Final outcome
if [ "$COUNTER" -gt "$MAX_RETRIES" ]; then
    echo "ERROR: Database could not be reached after $MAX_RETRIES attempts."
    exit 1
else
    echo "======== Setup Finished Successfully ========"
fi