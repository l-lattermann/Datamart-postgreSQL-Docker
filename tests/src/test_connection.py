"""
test_check_connection.py

Tests the behavior of src.db.connection.check_connection()
based on the running state of Colima VM and Docker container.

Logic:
- if both Colima and Docker container are running → expect True
- else → expect False
"""


# Stdlib imports
import subprocess
import os
import sys


# Internal imports
from src.db.connection import check_connection

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from src import config



# Test
def test_connection_test():
    """
    Verify check_connection() return value matches Docker/Colima runtime status.
    """
    res_docker = subprocess.run(["docker", "ps"], capture_output=True, text=True)
    res_colima = subprocess.run(["colima", "list"], capture_output=True, text=True)

    docker_running = config.DOCKER_PROFILE in res_docker.stdout
    colima_running = f"{config.COLIMA_PROFILE}" in res_colima.stdout and "Running" in res_colima.stdout

    if docker_running and colima_running:
        assert check_connection() is True
    else:
        assert check_connection() is False