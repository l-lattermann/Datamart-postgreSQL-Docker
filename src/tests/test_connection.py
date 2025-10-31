# Test if the connection testfunction behaves as expected

import subprocess
import os
import sys
from src.db.connection import check_connection

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from src import config

def test_connection_test():
    res_docker = subprocess.run(["docker", "ps"], capture_output=True, text=True)
    res_colima = subprocess.run(["colima", "list"], capture_output=True, text=True)
    docker_running = config.DOCKER_PROFILE in res_docker.stdout
    conlima_running = config.COLIMA_PROFILE + '    Running' in res_colima.stdout
    if docker_running and conlima_running:
        assert check_connection() == True
    else:
        assert check_connection() == False