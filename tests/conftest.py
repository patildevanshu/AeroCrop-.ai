"""
Pytest configuration and global session fixtures.
Ensures database tables and schema migrations are initialized before test execution.
"""

import os
import sys
from pathlib import Path
import asyncio
import pytest

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

for p in [str(PROJECT_ROOT), str(BACKEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.database.mongodb import init_mongodb as init_db, close_mongodb


@pytest.fixture(scope="session", autouse=True)
def initialize_test_database():
    """Ensure database schema is created and migrated prior to test suite execution."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(init_db())
    finally:
        loop.run_until_complete(close_mongodb())
        loop.close()
