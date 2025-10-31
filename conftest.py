# conftest.py
import os
import sys
import logging
import pytest

ROOT = os.path.dirname(__file__)
sys.path.insert(0, ROOT)

def pytest_configure(config):
    log_file = "logs/test.log"
    logging.basicConfig(
        filename=log_file,
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    # Capture print() too
    config.option.capture = "tee-sys"