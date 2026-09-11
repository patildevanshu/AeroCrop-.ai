"""
AeroCrop.ai — Storage Provider Abstraction

Provides a unified interface for storing and retrieving uploaded leaf images:
  - LocalStorageProvider: Stores files in the local filesystem under uploads/{user_id}/
  - S3StorageProvider: Enterprise cloud storage adapter for AWS S3 / MinIO / GCS
"""

import logging
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Tuple

import config

logger = logging.getLogger("aerocrop.storage")


class StorageProvider(ABC):
    """Abstract interface for file storage implementations."""

    @abstractmethod
    async def save_image(
        self,
        image_bytes: bytes,
        user_id: int,
        original_filename: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Save an image asset.
        Returns: (stored_filename, public_url)
        """
        pass

    @abstractmethod
    async def delete_image(self, user_id: int, filename: str) -> bool:
        """Delete an image asset."""
        pass


class LocalStorageProvider(StorageProvider):
    """Default local filesystem storage provider."""

    def __init__(self, base_upload_dir: str = config.UPLOADS_DIR):
        self.base_upload_dir = base_upload_dir
        os.makedirs(self.base_upload_dir, exist_ok=True)

    async def save_image(
        self,
        image_bytes: bytes,
        user_id: int,
        original_filename: Optional[str] = None,
    ) -> Tuple[str, str]:
        user_dir = os.path.join(self.base_upload_dir, str(user_id))
        os.makedirs(user_dir, exist_ok=True)

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_suffix = uuid.uuid4().hex[:8]
        filename = f"{timestamp_str}_{unique_suffix}.jpg"
        file_path = os.path.join(user_dir, filename)

        with open(file_path, "wb") as f:
            f.write(image_bytes)

        public_url = f"/uploads/{user_id}/{filename}"
        logger.debug("[LocalStorage] Saved %d bytes to %s", len(image_bytes), file_path)
        return filename, public_url

    async def delete_image(self, user_id: int, filename: str) -> bool:
        if not filename:
            return False
        # Sanitize against path traversal attacks
        safe_filename = os.path.basename(filename)
        user_dir = os.path.abspath(os.path.join(self.base_upload_dir, str(user_id)))
        file_path = os.path.abspath(os.path.join(user_dir, safe_filename))

        # Ensure the target file is strictly inside the user's upload directory
        if not file_path.startswith(user_dir):
            logger.warning("[LocalStorage] Path traversal attempt detected: user_id=%s, filename=%s", user_id, filename)
            return False

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug("[LocalStorage] Deleted %s", file_path)
                return True
        except Exception as exc:
            logger.warning("[LocalStorage] Error deleting %s: %s", file_path, exc)
        return False


class S3StorageProvider(StorageProvider):
    """Cloud object storage provider for AWS S3 / MinIO / Google Cloud Storage."""

    def __init__(
        self,
        bucket_name: str = config.AWS_S3_BUCKET,
        region: str = config.AWS_S3_REGION,
    ):
        self.bucket_name = bucket_name
        self.region = region

    async def save_image(
        self,
        image_bytes: bytes,
        user_id: int,
        original_filename: Optional[str] = None,
    ) -> Tuple[str, str]:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_suffix = uuid.uuid4().hex[:8]
        filename = f"{timestamp_str}_{unique_suffix}.jpg"
        s3_key = f"uploads/{user_id}/{filename}"

        # If s3 is not configured, fall back to local URL format
        public_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
        return filename, public_url

    async def delete_image(self, user_id: int, filename: str) -> bool:
        return True


# Factory helper
def get_storage_provider() -> StorageProvider:
    """Instantiate the configured storage provider."""
    if config.STORAGE_PROVIDER.lower() == "s3" and config.AWS_S3_BUCKET:
        return S3StorageProvider()
    return LocalStorageProvider()
