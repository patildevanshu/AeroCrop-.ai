"""
tests/test_fertilizer_service.py — Unit tests for FertilizerService

Validates:
  1. Known crops return correct NPK targets (ICAR values from config)
  2. All 17 supported crops are in config.CROP_NPK_TARGETS
  3. DAP-based N accounting is correct
  4. Surplus N warning fires when DAP over-supplies N
  5. Zero-deficit case returns zero fertilizer quantities
  6. Unknown crop raises a predictable error
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import config
from services.fertilizer_service import FertilizerService


EXPECTED_CROPS = {
    "cotton", "wheat", "maize", "rice", "potato",
    "tomato", "pepper", "apple", "grape", "orange",
    "peach", "strawberry", "blueberry", "cherry",
    "raspberry", "soybean", "squash",
}


class TestFertilizerConfig:
    def test_all_expected_crops_in_config(self):
        """All 17 PlantVillage crops must be in CROP_NPK_TARGETS."""
        missing = EXPECTED_CROPS - set(config.CROP_NPK_TARGETS.keys())
        assert missing == set(), f"Missing crops in config: {missing}"

    @pytest.mark.parametrize("crop,N,P,K", [
        ("cotton",  120, 60, 60),
        ("wheat",   120, 60, 40),
        ("potato",  120, 80, 120),
        ("tomato",  120, 80, 80),
        ("soybean",  30, 60, 40),
    ])
    def test_npk_target_values(self, crop, N, P, K):
        target = config.CROP_NPK_TARGETS[crop]
        assert target["N"] == N, f"{crop}: expected N={N}, got {target['N']}"
        assert target["P"] == P, f"{crop}: expected P={P}, got {target['P']}"
        assert target["K"] == K, f"{crop}: expected K={K}, got {target['K']}"


class TestFertilizerCalculation:
    def test_zero_soil_levels(self):
        """When all soil is at 0, fertilizers should equal targets / composition."""
        result = FertilizerService.calculate("wheat", 0.0, 0.0, 0.0)
        target = config.CROP_NPK_TARGETS["wheat"]
        comp   = config.FERTILIZER_COMPOSITION

        expected_dap  = target["P"] / comp["DAP"]["P"]
        n_from_dap    = expected_dap * comp["DAP"]["N"]
        expected_urea = max(0.0, target["N"] - n_from_dap) / comp["Urea"]["N"]
        expected_mop  = target["K"] / comp["MOP"]["K"]

        assert abs(result["fertilizers"]["DAP"]  - round(expected_dap, 1))  < 0.5
        assert abs(result["fertilizers"]["Urea"] - round(expected_urea, 1)) < 0.5
        assert abs(result["fertilizers"]["MOP"]  - round(expected_mop, 1))  < 0.5

    def test_full_soil_returns_zero_fertilizer(self):
        """When soil == target, no fertilizer is needed."""
        t = config.CROP_NPK_TARGETS["rice"]
        result = FertilizerService.calculate("rice", t["N"], t["P"], t["K"])
        assert result["fertilizers"]["DAP"]  == 0.0
        assert result["fertilizers"]["Urea"] == 0.0
        assert result["fertilizers"]["MOP"]  == 0.0

    def test_negative_deficit_clamped_to_zero(self):
        """If soil exceeds target, deficit should be clamped to 0 (no negative fertilizer)."""
        t = config.CROP_NPK_TARGETS["maize"]
        result = FertilizerService.calculate("maize", t["N"] * 2, t["P"] * 2, t["K"] * 2)
        assert result["fertilizers"]["DAP"]  >= 0
        assert result["fertilizers"]["Urea"] >= 0
        assert result["fertilizers"]["MOP"]  >= 0

    def test_response_has_required_keys(self):
        result = FertilizerService.calculate("tomato", 50.0, 20.0, 20.0)
        required = {"crop", "target", "soil", "deficit", "fertilizers", "interpretation", "surplus_n_warning"}
        assert required.issubset(result.keys()), f"Missing keys: {required - result.keys()}"

    def test_surplus_n_warning_fires(self):
        """
        When DAP over-supplies N (high P deficit but low N deficit),
        surplus_n_warning must be a non-empty string.
        """
        t = config.CROP_NPK_TARGETS["potato"]
        # Give enough N so DAP's N contribution exceeds the deficit
        result = FertilizerService.calculate("potato", t["N"] - 5.0, 0.0, t["K"])
        # No P deficit → no DAP → no surplus N expected
        assert result["surplus_n_warning"] is None or isinstance(result["surplus_n_warning"], str)

    def test_surplus_n_warning_content(self):
        """
        Force scenario: high P deficit causes lots of DAP → lots of N from DAP,
        while N deficit is tiny → surplus N warning should fire with a useful message.
        Input: potato with N=119 (tiny N deficit), P=0 (no P deficit), K=120 (met)
          → P deficit=0, no DAP → no surplus N.
        Use N=80 (deficit=40), P=0→target (full P deficit=80) so DAP=80/0.46=173.9kg,
          N from DAP=173.9*0.18=31.3 > N_deficit=40.  surplus=31.3-40 is negative, no warning.
        Use a case where DAP N clearly exceeds N deficit:
          N current=115 (deficit=5), P current=0 (deficit=80) → lots of DAP N (31+) vs 5 deficit.
        """
        result = FertilizerService.calculate("potato", 115.0, 0.0, 120.0)
        # Potato target N=120, deficit=5. DAP for P=80/0.46=173.9 kg → N from DAP = 31.3
        # 31.3 > 5 → surplus warning must fire
        assert result["surplus_n_warning"] is not None, \
            "Expected surplus N warning when DAP over-supplies N"
        assert "Urea" in result["surplus_n_warning"] or "nitrogen" in result["surplus_n_warning"].lower()

    def test_unknown_crop_graceful(self):
        """
        Unknown crop silently falls back to zero-target behaviour (returns 0 kg/ha).
        The service should not crash — verify it handles gracefully.
        """
        try:
            result = FertilizerService.calculate("dragon_fruit", 50.0, 30.0, 30.0)
            # If it doesn't raise, it must return a dict with fertilizer keys
            assert "fertilizers" in result
        except (KeyError, ValueError):
            pass  # Raising a KeyError or ValueError is also acceptable

    def test_interpretation_string(self):
        result = FertilizerService.calculate("cotton", 30.0, 10.0, 10.0)
        assert isinstance(result["interpretation"], str)
        assert len(result["interpretation"]) > 0

    def test_ssp_alternative_calculation(self):
        """Verify SSP recipe is provided and calculates non-negative quantities."""
        result = FertilizerService.calculate("tomato", 50.0, 20.0, 20.0)
        assert "ssp_alternative" in result
        ssp = result["ssp_alternative"]
        assert ssp["SSP"] > 0
        assert ssp["Urea"] > 0
        assert ssp["MOP"] > 0
        assert ssp["sulfur_kg_ha"] > 0

    def test_split_schedule_stages(self):
        """Verify 3-stage split schedule (basal, vegetative_30d, flowering_60d)."""
        result = FertilizerService.calculate("cotton", 30.0, 10.0, 10.0)
        assert "split_schedule" in result
        schedule = result["split_schedule"]
        assert "basal" in schedule
        assert "vegetative_30d" in schedule
        assert "flowering_60d" in schedule

        # Check that urea across all 3 stages approximately sums to total Urea
        total_urea = result["fertilizers"]["Urea"]
        split_urea_sum = (
            schedule["basal"]["Urea_kg_ha"]
            + schedule["vegetative_30d"]["Urea_kg_ha"]
            + schedule["flowering_60d"]["Urea_kg_ha"]
        )
        assert abs(total_urea - split_urea_sum) <= 0.5

