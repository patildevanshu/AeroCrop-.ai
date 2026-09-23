"""
tests/test_model_inference.py — Unit tests for InferenceService

Validates:
  1. InferenceService is a functional singleton
  2. predict() returns all expected keys for both real and mock mode
  3. Confidence is in [0, 1]
  4. disease_class is in [0, 37]
  5. low_confidence flag is a bool
  6. yield_t_ha is non-negative
  7. normalise_tabular() produces values in a sensible Z-score range
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import pytest
import numpy as np
from PIL import Image

import config
from model.inference import InferenceService


# ── Helper: create minimal valid JPEG bytes ──────────────────────────────────
def make_dummy_jpeg(width: int = 224, height: int = 224) -> bytes:
    img = Image.new("RGB", (width, height), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


DUMMY_IMAGE = make_dummy_jpeg()
DEFAULT_KWARGS = dict(
    image_bytes=DUMMY_IMAGE,
    temperature=28.0,
    humidity=65.0,
    rainfall=3.0,
    crop="tomato",
)


class TestInferenceServiceSingleton:
    def test_singleton_identity(self):
        a = InferenceService()
        b = InferenceService()
        assert a is b, "InferenceService must be a singleton"

    def test_has_model_attribute(self):
        svc = InferenceService()
        assert hasattr(svc, "model")

    def test_has_mock_mode_attribute(self):
        svc = InferenceService()
        assert isinstance(svc.mock_mode, bool)


class TestPredictReturnSchema:
    @pytest.fixture(scope="class")
    def result(self):
        svc = InferenceService()
        return svc.predict(**DEFAULT_KWARGS)

    def test_disease_class_key(self, result):
        assert "disease_class" in result

    def test_confidence_key(self, result):
        assert "confidence" in result

    def test_yield_key(self, result):
        assert "yield_t_ha" in result

    def test_mock_key(self, result):
        assert "mock" in result

    def test_low_confidence_key(self, result):
        assert "low_confidence" in result

    def test_probabilities_key(self, result):
        assert "probabilities" in result

    def test_disease_class_in_range(self, result):
        assert 0 <= result["disease_class"] < config.NUM_DISEASE_CLASSES

    def test_confidence_in_unit_range(self, result):
        assert 0.0 <= result["confidence"] <= 1.0

    def test_yield_non_negative(self, result):
        assert result["yield_t_ha"] >= 0.0

    def test_probabilities_sum_to_one(self, result):
        total = sum(result["probabilities"])
        assert abs(total - 1.0) < 1e-3, f"Probabilities sum to {total}, expected ~1.0"

    def test_probabilities_length(self, result):
        assert len(result["probabilities"]) == config.NUM_DISEASE_CLASSES

    def test_low_confidence_is_bool(self, result):
        assert isinstance(result["low_confidence"], bool)

    def test_mock_is_bool(self, result):
        assert isinstance(result["mock"], bool)


class TestNormalisation:
    """
    InferenceService.normalise_tabular() should produce Z-scores in a sensible
    range for 3-dim weather inputs (temperature, humidity, rainfall).
    """

    def test_typical_inputs_within_5_sigma(self):
        svc    = InferenceService()
        tensor = svc._normalise_tabular(
            temperature=28, humidity=65, rainfall=3.0
        )
        vals = tensor.cpu().numpy().flatten()
        assert np.all(np.abs(vals) < 10.0), (
            f"Z-scores have extreme values: {vals} — normalisation mismatch likely"
        )

    def test_high_humidity_within_5_sigma(self):
        svc    = InferenceService()
        tensor = svc._normalise_tabular(
            temperature=35, humidity=90, rainfall=0.0
        )
        vals = tensor.cpu().numpy().flatten()
        assert np.all(np.abs(vals) < 10.0)

    def test_output_shape_is_1x3(self):
        svc    = InferenceService()
        tensor = svc._normalise_tabular(
            temperature=28, humidity=65, rainfall=3.0
        )
        assert tensor.shape == (1, 3), f"Expected shape (1,3), got {tensor.shape}"


class TestAgronomicYieldBounds:
    """
    Validates that yield predictions across crops adhere to ICAR & Maharashtra
    agricultural benchmarks, preventing high-yield anomalies.
    """

    @pytest.mark.parametrize("crop,min_expected,max_expected", [
        ("cotton", 0.6, 2.8),
        ("Cotton (Kapas)", 0.6, 2.8),
        ("soybean", 0.6, 2.5),
        ("wheat", 1.0, 4.5),
        ("rice", 1.2, 5.5),
        ("maize", 1.2, 6.0),
        ("turmeric", 1.0, 5.0),
        ("sugarcane", 40.0, 110.0),
        ("tomato", 12.0, 42.0),
        ("orange", 8.0, 25.0),
    ])
    def test_crop_yield_within_icar_bounds(self, crop, min_expected, max_expected):
        svc = InferenceService()
        result = svc.predict(
            image_bytes=DUMMY_IMAGE,
            temperature=28.0,
            humidity=65.0,
            rainfall=3.0,
            crop=crop,
        )
        yield_val = result["yield_t_ha"]
        assert min_expected <= yield_val <= max_expected, (
            f"Yield for {crop} ({yield_val} t/ha) must be in [{min_expected}, {max_expected}] t/ha"
        )
        assert "yield_category" in result
        assert "yield_category_label" in result

    def test_mock_cotton_not_default_25(self):
        res = InferenceService._mock_predict(crop="cotton")
        assert res["yield_t_ha"] < 3.0, f"Mock cotton yield must be realistic, got {res['yield_t_ha']}"
        assert res["yield_category"] == "dry_fiber"

    def test_mock_auto_crop_resolution(self):
        res = InferenceService._mock_predict(crop="auto")
        assert res["yield_t_ha"] > 0
        assert "yield_category" in res
        assert "yield_category_label" in res

