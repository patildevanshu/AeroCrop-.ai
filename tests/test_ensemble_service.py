"""
tests/test_ensemble_service.py — Verification tests for Agronomic Ensemble Service
"""

import io
import pytest
from PIL import Image
from backend.services.ensemble_service import EnsembleService
from backend.services.disease_service import DiseaseService


def make_test_image() -> bytes:
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


import asyncio

def test_ensemble_offline_fallback():
    """Verify that when validator microservice is offline, verify() returns None silently."""
    image_bytes = make_test_image()
    res = asyncio.run(EnsembleService.verify(
        image_bytes=image_bytes,
        district="Pune",
        weather={"temperature": 28.0, "humidity": 65.0, "rainfall": 0.0},
        local_crop="Tomato",
        local_class_idx=29,
        local_confidence=0.75,
    ))
    assert res is None


def test_ensemble_disabled():
    """Verify that when ENABLE_REMOTE_VALIDATOR is False, verify() immediately returns None."""
    import backend.config as config
    original_setting = config.ENABLE_REMOTE_VALIDATOR
    try:
        config.ENABLE_REMOTE_VALIDATOR = False
        image_bytes = make_test_image()
        res = asyncio.run(EnsembleService.verify(
            image_bytes=image_bytes,
            district="Pune",
            weather={"temperature": 28.0, "humidity": 65.0, "rainfall": 0.0},
            local_crop="Tomato",
            local_class_idx=29,
            local_confidence=0.75,
        ))
        assert res is None
    finally:
        config.ENABLE_REMOTE_VALIDATOR = original_setting
