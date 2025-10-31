#!/bin/zsh
# ============================================================
# ================ TEARDOWN SCRIPT: COLIMA + DOCKER ==========
# ============================================================

# --- Enable unified logging (stdout + stderr to logs/app.log) ---
exec > >(tee -a logs/app.log) 2>&1

# ============================================================
# ====================== CONFIGURATION ========================
# ============================================================

# Import environment variables from .env
set -e
set -a
source .env
set +a

# Define key variables
YAML=$YML_FILE
CONTAINER_NAME=$DOCKER_PROFILE
VM_NAME=$COLIMA_PROFILE
PG_VOLUME_NAME=$PG_VOLUME_NAME


# ============================================================
# ==================== DOCKER TEARDOWN =======================
# ============================================================

echo ""
echo "==================================================="
echo "=============== Docker Teardown ==================="
echo "==================================================="

# --- Docker Context Info ---
echo "== Docker Context =="
docker version
docker info | head -n 5

echo ""
echo "=== Step 1: Container and Volume Cleanup ==="
echo ""
echo "-> Current Docker volumes:"
docker volume ls

# --- Stop running container if active ---
if docker ps 2>/dev/null | grep -i "$CONTAINER_NAME"; then
    echo "-> Container \"$CONTAINER_NAME\" is running. Attempting shutdown..."
    docker-compose --file "$YAML" down --volumes --remove-orphans

    if ! docker ps 2>/dev/null | grep -i "$CONTAINER_NAME"; then
        echo "-> Container \"$CONTAINER_NAME\" shutdown successful!"
    else 
        echo "-> Container \"$CONTAINER_NAME\" still running after shutdown attempt."
    fi
else 
    echo "-> Container \"$CONTAINER_NAME\" is not running. No need for shutdown."
fi

echo ""
echo "-> Rechecking Docker volumes:"
docker volume ls

# --- Remove PostgreSQL volume if it still exists ---
if docker volume ls --format '{{.Name}}' 2>/dev/null | grep -iq "$PG_VOLUME_NAME"; then
    echo ""
    echo "-> Orphaned volume \"$PG_VOLUME_NAME\" found. Removing..."
    docker volume rm "$PG_VOLUME_NAME"
    echo "-> Remaining Docker volumes:"
    docker volume ls
else
    echo ""
    echo "-> No matching volumes named \"$PG_VOLUME_NAME\" found."
    docker volume ls
fi

# --- Remove container from list if it still exists ---
if docker ps -a 2>/dev/null | grep -i "$CONTAINER_NAME"; then
    echo ""
    echo "-> Container \"$CONTAINER_NAME\" still listed. Forcing removal..."
    docker rm -f "$CONTAINER_NAME"

    if ! docker ps -a 2>/dev/null | grep -i "$CONTAINER_NAME"; then
        echo "-> Container \"$CONTAINER_NAME\" removed successfully!"
    else 
        echo "-> Container \"$CONTAINER_NAME\" could not be removed."
    fi
else
    echo ""
    echo "-> Container \"$CONTAINER_NAME\" not found in list. No action needed."
fi

sleep 4


# ============================================================
# ===================== COLIMA TEARDOWN =======================
# ============================================================

echo ""
echo "==================================================="
echo "=============== Colima VM Teardown ================"
echo "==================================================="

# --- Stop Colima VM if running ---
if colima status "$VM_NAME" 2>/dev/null | grep -i "is running"; then
    echo "-> Colima VM \"$VM_NAME\" is running. Attempting shutdown..."
    colima stop "$VM_NAME"

    if ! colima list 2>/dev/null | grep -i "$VM_NAME"; then
        echo "-> VM \"$VM_NAME\" stopped successfully!"
    else
        echo "-> VM \"$VM_NAME\" shutdown may have failed."
    fi
else 
    echo "-> VM \"$VM_NAME\" is not running. No shutdown required."
fi

# --- Delete Colima VM if still listed ---
if colima list 2>/dev/null | grep -i "$VM_NAME"; then
    echo ""
    echo "-> Colima VM \"$VM_NAME\" is listed. Attempting deletion..."
    colima delete -f "$VM_NAME"

    if ! colima list 2>/dev/null | grep -i "$VM_NAME"; then
        echo "-> VM \"$VM_NAME\" deleted successfully!"
    else
        echo "-> VM \"$VM_NAME\" deletion failed!"
    fi
else 
    echo "-> VM \"$VM_NAME\" not listed. No deletion required."
fi

echo ""
echo "======== Teardown Finished Successfully ========"