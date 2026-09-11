"""
tests/test_disease_service.py — Unit tests for DiseaseService

Validates that:
  1. All 50 disease classes are registered
  2. Class indices exactly match model/classes.json alphabetical ordering
  3. Critical healthy vs disease labels are correct
  4. All treatment lists are properly formed
  5. Lookup by index works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.services.disease_service import DiseaseService


class TestDiseaseServiceCount:
    def test_exactly_50_diseases(self):
        """All 50 pathology classes must be registered."""
        assert DiseaseService.get_class_count() == 50

    def test_indices_are_zero_to_49(self):
        """Indices must form a contiguous 0..49 range."""
        indices = [d.class_idx for d in DiseaseService.DISEASES]
        assert indices == list(range(50)), "Indices must be 0..49 in order"


class TestDiseaseServiceOrdering:
    """
    Verify the canonical ordering matching model/classes.json.
    """

    @pytest.mark.parametrize("idx,expected_healthy", [
        (3,  True),   # Banana healthy
        (1,  False),  # Banana Panama disease
        (7,  True),   # Corn healthy
        (6,  False),  # Corn Northern Leaf Blight
        (9,  True),   # Cotton healthy
        (8,  False),  # Cotton Bacterial blight
        (13, True),   # Potato healthy
        (12, False),  # Potato Late blight
        (19, True),   # Soybean healthy
        (24, True),   # Sugarcane healthy
        (21, False),  # Sugarcane Red rot
        (34, True),   # Tomato healthy
        (27, False),  # Tomato Late blight
        (38, True),   # Turmeric healthy
        (37, False),  # Turmeric Rhizome rot
        (49, True),   # Wheat healthy
        (48, False),  # Wheat Yellow rust
    ])
    def test_healthy_disease_ordering(self, idx, expected_healthy):
        d = DiseaseService.get_by_index(idx)
        assert d is not None, f"No disease at index {idx}"
        assert d.is_healthy == expected_healthy, (
            f"Index {idx}: expected is_healthy={expected_healthy}, "
            f"got is_healthy={d.is_healthy} — name='{d.name}'"
        )

    def test_banana_indices_0_to_3(self):
        for idx, expected in [
            (0, "cordana"), (1, "panama"), (2, "sigatoka"), (3, "healthy")
        ]:
            d = DiseaseService.get_by_index(idx)
            assert d is not None
            assert expected in d.name.lower(), f"Index {idx}: expected '{expected}' in '{d.name}'"
            assert d.crop == "Banana"

    def test_orange_at_10(self):
        d = DiseaseService.get_by_index(10)
        assert d is not None
        assert "orange" in d.crop.lower() or "citrus" in d.name.lower()

    def test_potato_healthy_and_late_blight(self):
        healthy     = DiseaseService.get_by_index(13)
        late_blight = DiseaseService.get_by_index(12)
        assert healthy.is_healthy is True,  "idx 13 must be Potato Healthy"
        assert late_blight.is_healthy is False, "idx 12 must be Potato Late Blight"
        assert "blight" in late_blight.name.lower()
        assert late_blight.severity == "Critical"

    def test_tomato_healthy_and_late_blight(self):
        healthy     = DiseaseService.get_by_index(34)
        late_blight = DiseaseService.get_by_index(27)
        assert healthy.is_healthy is True,  "idx 34 must be Tomato Healthy"
        assert late_blight.is_healthy is False, "idx 27 must be Tomato Late Blight"
        assert "blight" in late_blight.name.lower()
        assert late_blight.severity == "Critical"

    def test_wheat_indices_39_to_49(self):
        for idx in range(39, 50):
            d = DiseaseService.get_by_index(idx)
            assert d is not None
            assert d.crop == "Wheat"
        assert DiseaseService.get_by_index(49).is_healthy is True


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
        assert len(names) == 50

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
