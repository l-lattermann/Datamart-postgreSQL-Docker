#!/bin/zsh

# --- Configuration ---
# Import variables from .env
set -e
set -a
source scratches/postgres_poc/.env
set +a


YAML=$YML_FILE
CONTAINER_NAME=$DOCKER_PROFILE
VM_NAME=$COLIMA_PROFILE


echo ""
echo ""
echo "=== Docker Container Teardown ==="
# Check in Container name is running, if yes, shut down
if docker ps 2>/dev/null | grep -i "$DOCKER_PROFILE"; then
    echo "Docker is running, trying shutdown..."
    docker-compose -f "$YAML" down
    # Check if shutdown was successfull
    if ! docker ps 2>/dev/null | grep -i "$DOCKER_PROFILE"; then
        echo "Container \"$DOCKER_PROFILE\" shutdown successfull!"
    else 
        echo "Container \"$DOCKER_PROFILE\" still running."
    fi
else 
    echo "Docker Container \"$DOCKER_PROFILE\" is not running. No need for shutdown."
fi

# Check in Container name is still in list, if yes, delete
if docker ps -a 2>/dev/null | grep -i "$DOCKER_PROFILE"; then
    echo "Docker Comtainer \"$DOCKER_PROFILE\" is in list, trying delete..."
    docker rm -f "$DOCKER_PROFILE"
    # Check if shutdown was successfull
    if ! docker ps -a 2>/dev/null | grep -i "$DOCKER_PROFILE"; then
        echo "Container \"$DOCKER_PROFILE\" deletion successfull!"
    else 
        echo "\"$DOCKER_PROFILE\" shutdown failed!"
    fi
else 
    echo "Container \"$DOCKER_PROFILE\" is not listed. No need for deletion."
fi


echo ""
echo ""
echo "=== Colima VM Teardown ==="
# Check if vm is running, if yes, stop
if colima status "$COLIMA_PROFILE" 2>/dev/null | grep -i "is running"; then
    echo "Colima VM \"$COLIMA_PROFILE\" is running, trying shutdown..."
    colima stop "$VM_NAME"
    # Check if container is in container list, if yes, remove
    if ! colima list 2>/dev/null | grep -i "$COLIMA_PROFILE"; then
        echo "Stopped \"$COLIMA_PROFILE\" successfull!"
    else
        echo "\"$COLIMA_PROFILE\" shutdown failed!"
    fi
else 
    echo "VM is not running, no need to stop."
fi

# Check if vm is running, if yes, stop
if colima list 2>/dev/null | grep -i "$COLIMA_PROFILE"; then
    echo "Colima VM \"$COLIMA_PROFILE\" is listed, trying deletion..."
    colima delete -f "$VM_NAME"
    # Check if container is in container list, if yes, remove
    if ! colima list 2>/dev/null | grep -i "$COLIMA_PROFILE"; then
        echo "Deleted \"$COLIMA_PROFILE\" successfull!"
    else
        echo "\"$COLIMA_PROFILE\" deletion failed!"
    fi
else 
    echo "VM \"$COLIMA_PROFILE\" is not listed, no need to delete."
fi
echo ""
echo ""
echo "======== Teardown finished ========"