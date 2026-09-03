"""
tests/test_disease_service.py — Unit tests for DiseaseService

Validates that:
  1. All 38 disease classes are registered
  2. Class indices exactly match dataset.py alphabetical ordering
  3. Critical healthy↔disease inversions are fixed
  4. All treatment lists are properly formed
  5. Lookup by index works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.disease_service import DiseaseService


class TestDiseaseServiceCount:
    def test_exactly_38_diseases(self):
        """Exactly 38 PlantVillage classes must be registered."""
        assert DiseaseService.get_class_count() == 38

    def test_indices_are_zero_to_37(self):
        """Indices must form a contiguous 0..37 range."""
        indices = [d.class_idx for d in DiseaseService.DISEASES]
        assert indices == list(range(38)), "Indices must be 0..37 in order"


class TestDiseaseServiceOrdering:
    """
    Verify the alphabetical ordering that matches model/dataset.py:DISEASE_CLASSES.
    The inversion bugs being tested were:
      Cherry healthy (5) / Powdery_mildew (6)
      Corn   healthy (9) / Northern Leaf Blight (10)
      Grape  healthy (13) / Leaf blight (14)
      Potato healthy (21) / Late blight (22)  ← CRITICAL
      Strawberry healthy (26) / Leaf scorch (27)
      Tomato healthy (30) / Late blight (31)  ← CRITICAL
      Tomato mosaic (36) / TYLCV (37)
    """

    @pytest.mark.parametrize("idx,expected_healthy", [
        (5,  True),   # Cherry healthy
        (6,  False),  # Cherry Powdery Mildew
        (9,  True),   # Corn healthy
        (10, False),  # Corn Northern Leaf Blight
        (13, True),   # Grape healthy
        (14, False),  # Grape Leaf Blight
        (21, True),   # Potato HEALTHY (was showing Late Blight!)
        (22, False),  # Potato LATE BLIGHT (was showing Healthy!)
        (26, True),   # Strawberry healthy
        (27, False),  # Strawberry Leaf Scorch
        (30, True),   # Tomato HEALTHY (was showing Late Blight!)
        (31, False),  # Tomato LATE BLIGHT (was showing Healthy!)
    ])
    def test_healthy_disease_ordering(self, idx, expected_healthy):
        d = DiseaseService.get_by_index(idx)
        assert d is not None, f"No disease at index {idx}"
        assert d.is_healthy == expected_healthy, (
            f"Index {idx}: expected is_healthy={expected_healthy}, "
            f"got is_healthy={d.is_healthy} — name='{d.name}'"
        )

    def test_tomato_mosaic_before_tylcv(self):
        """Index 36 must be Mosaic Virus, 37 must be Yellow Leaf Curl (alphabetical)."""
        d36 = DiseaseService.get_by_index(36)
        d37 = DiseaseService.get_by_index(37)
        assert d36 is not None and d37 is not None
        assert "mosaic" in d36.name.lower(), f"Expected Mosaic at 36, got: {d36.name}"
        assert "yellow" in d37.name.lower() or "curl" in d37.name.lower(), \
            f"Expected Yellow Leaf Curl at 37, got: {d37.name}"

    def test_apple_indices_0_to_3(self):
        for idx, expected in [
            (0, "scab"), (1, "black"), (2, "cedar"), (3, "healthy")
        ]:
            d = DiseaseService.get_by_index(idx)
            assert d is not None
            assert expected in d.name.lower(), f"Index {idx}: expected '{expected}' in '{d.name}'"
            assert d.crop == "Apple"

    def test_orange_at_15(self):
        d = DiseaseService.get_by_index(15)
        assert d is not None
        assert "orange" in d.crop.lower() or "citrus" in d.name.lower()

    def test_potato_critical_inversion(self):
        """The most dangerous inversion — potato healthy↔late blight."""
        healthy    = DiseaseService.get_by_index(21)
        late_blight = DiseaseService.get_by_index(22)
        assert healthy.is_healthy is True,  "idx 21 must be Potato Healthy"
        assert late_blight.is_healthy is False, "idx 22 must be Potato Late Blight"
        assert "blight" in late_blight.name.lower()
        assert late_blight.severity == "Critical"

    def test_tomato_critical_inversion(self):
        """Second-most-dangerous inversion — tomato healthy↔late blight."""
        healthy    = DiseaseService.get_by_index(30)
        late_blight = DiseaseService.get_by_index(31)
        assert healthy.is_healthy is True,  "idx 30 must be Tomato Healthy"
        assert late_blight.is_healthy is False, "idx 31 must be Tomato Late Blight"
        assert "blight" in late_blight.name.lower()
        assert late_blight.severity == "Critical"


class TestDiseaseServiceLookup:
    def test_get_by_index_valid(self):
        d = DiseaseService.get_by_index(0)
        assert d is not None
        assert d.class_idx == 0

    def test_get_by_index_invalid(self):
        d = DiseaseService.get_by_index(99)
        assert d is None

    def test_get_all_names_length(self):
        names = DiseaseService.get_all_names()
        assert len(names) == 38

    def test_all_healthy_classes_have_no_treatments(self):
        """Healthy classes should have empty treatment lists."""
        for d in DiseaseService.DISEASES:
            if d.is_healthy:
                assert d.chemical_treatment == [], f"{d.name} healthy but has chemical treatments"
                assert d.organic_treatment == [],  f"{d.name} healthy but has organic treatments"

    def test_critical_diseases_have_treatments(self):
        """Critical diseases must have at least 1 chemical and 1 organic treatment."""
        for d in DiseaseService.DISEASES:
            if d.severity == "Critical":
                assert len(d.chemical_treatment) > 0, f"{d.name} critical but no chemical treatment"
                assert len(d.organic_treatment) > 0,  f"{d.name} critical but no organic treatment"

    def test_healthy_class_severity_is_none(self):
        for d in DiseaseService.DISEASES:
            if d.is_healthy:
                assert d.severity == "None", f"{d.name} should have severity='None'"
