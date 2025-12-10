#!/bin/zsh

# TEARDOWN: COLIMA + DOCKER
# Purpose:
 load .env to get profile/container/volume names
 stop and remove Docker containers/volumes
 stop and delete Colima VM
 log everything to logs/app.log



# unified logging (stdout + stderr)
exec > >(tee -a logs/app.log) 2>&1


# 1) CONFIGURATION
set -e
set -a
source .env
set +a

YAML=$YML_FILE
CONTAINER_NAME=$DOCKER_PROFILE
VM_NAME=$COLIMA_PROFILE
PG_VOLUME_NAME=$PG_VOLUME_NAME


# 2) DOCKER TEARDOWN
echo ""
echo "==================================================="
echo "=============== Docker Teardown ==================="
echo "==================================================="

# context info
echo "== Docker Context =="
docker version
docker info | head -n 5

echo ""
echo "=== Step 1: Container and Volume Cleanup ==="
echo "-> Current Docker volumes:"
docker volume ls

# stop running container if present
if docker ps 2>/dev/null | grep -i "$CONTAINER_NAME"; then
    echo "-> Container \"$CONTAINER_NAME\" is running. Shutting down via docker-compose..."
    docker-compose --file "$YAML" down --volumes --remove-orphans

    if ! docker ps 2>/dev/null | grep -i "$CONTAINER_NAME"; then
        echo "-> Container \"$CONTAINER_NAME\" shutdown successful."
    else
        echo "-> Container \"$CONTAINER_NAME\" still running after shutdown attempt."
    fi
else
    echo "-> Container \"$CONTAINER_NAME\" is not running. Skipping shutdown."
fi

echo ""
echo "-> Rechecking Docker volumes:"
docker volume ls

# remove PG volume if still present
if docker volume ls --format '{{.Name}}' 2>/dev/null | grep -iq "$PG_VOLUME_NAME"; then
    echo ""
    echo "-> Volume \"$PG_VOLUME_NAME\" found. Removing..."
    docker volume rm "$PG_VOLUME_NAME"
    echo "-> Remaining Docker volumes:"
    docker volume ls
else
    echo ""
    echo "-> No volume named \"$PG_VOLUME_NAME\" found."
    docker volume ls
fi

# remove container from list if still present
if docker ps -a 2>/dev/null | grep -i "$CONTAINER_NAME"; then
    echo ""
    echo "-> Container \"$CONTAINER_NAME\" still listed. Forcing removal..."
    docker rm -f "$CONTAINER_NAME"

    if ! docker ps -a 2>/dev/null | grep -i "$CONTAINER_NAME"; then
        echo "-> Container \"$CONTAINER_NAME\" removed successfully."
    else
        echo "-> Container \"$CONTAINER_NAME\" could not be removed."
    fi
else
    echo ""
    echo "-> Container \"$CONTAINER_NAME\" not found in docker ps -a. No action."
fi

sleep 4


# 3) COLIMA TEARDOWN
echo ""
echo "==================================================="
echo "=============== Colima VM Teardown ================"
echo "==================================================="

# stop VM if running
if colima status "$VM_NAME" 2>/dev/null | grep -i "is running"; then
    echo "-> Colima VM \"$VM_NAME\" is running. Stopping..."
    colima stop "$VM_NAME"

    if ! colima list 2>/dev/null | grep -i "$VM_NAME"; then
        echo "-> VM \"$VM_NAME\" stopped successfully."
    else
        echo "-> VM \"$VM_NAME\" stop may have failed."
    fi
else
    echo "-> Colima VM \"$VM_NAME\" is not running. No stop required."
fi

# delete VM if still listed
if colima list 2>/dev/null | grep -i "$VM_NAME"; then
    echo ""
    echo "-> Colima VM \"$VM_NAME\" still listed. Deleting..."
    colima delete -f "$VM_NAME"

    if ! colima list 2>/dev/null | grep -i "$VM_NAME"; then
        echo "-> VM \"$VM_NAME\" deleted successfully."
    else
        echo "-> VM \"$VM_NAME\" deletion failed."
    fi
else
    echo "-> Colima VM \"$VM_NAME\" not listed. No deletion required."
fi

echo ""
echo "======== Teardown Finished Successfully ========"