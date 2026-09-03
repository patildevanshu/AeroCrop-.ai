"""
Tests for AeroCrop.ai Storage Provider Abstraction (services/storage_service.py)
"""

import asyncio
import os
import pytest
import config
from services.storage_service import LocalStorageProvider, get_storage_provider


def run(coro):
    """Execute async coroutine synchronously in tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestLocalStorageProvider:

    def test_save_and_delete_image(self, tmp_path):
        provider = LocalStorageProvider(base_upload_dir=str(tmp_path))
        fake_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 64
        user_id = 999

        # Save image
        filename, public_url = run(provider.save_image(fake_bytes, user_id))
        assert filename.endswith(".jpg")
        assert public_url == f"/uploads/{user_id}/{filename}"

        saved_path = os.path.join(str(tmp_path), str(user_id), filename)
        assert os.path.exists(saved_path)
        assert os.path.getsize(saved_path) == len(fake_bytes)

        # Delete image
        deleted = run(provider.delete_image(user_id, filename))
        assert deleted is True
        assert not os.path.exists(saved_path)

    def test_delete_nonexistent_image(self, tmp_path):
        provider = LocalStorageProvider(base_upload_dir=str(tmp_path))
        deleted = run(provider.delete_image(123, "nonexistent.jpg"))
        assert deleted is False

    def test_factory_returns_local_provider(self):
        provider = get_storage_provider()
        assert isinstance(provider, LocalStorageProvider)
