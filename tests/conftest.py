"""
Pytest configuration and global session fixtures.
Ensures database tables and schema migrations are initialized before test execution.
"""

import asyncio
import pytest
from database.connection import init_db


@pytest.fixture(scope="session", autouse=True)
def initialize_test_database():
    """Ensure database schema is created and migrated prior to test suite execution."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(init_db())
    finally:
        loop.close()
