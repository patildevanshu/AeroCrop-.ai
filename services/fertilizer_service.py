"""
AeroCrop.ai — Fertilizer Service

Calculates commercial fertilizer dosages required to correct soil NPK deficits,
offering both DAP and SSP alternative recipes and a growth-stage split application calendar.

Math:
  Standard DAP Recipe:
    DAP qty      = D_P / 0.46
    N from DAP   = DAP_qty * 0.18
    Urea qty     = max(0, D_N - N_from_DAP) / 0.46
    MOP qty      = D_K / 0.60

  Alternative SSP Recipe (Zero Nitrogen in Phosphorus source):
    SSP qty      = D_P / 0.16
    Urea qty     = D_N / 0.46
    MOP qty      = D_K / 0.60

Sources:
  - ICAR NPK recommendations for Maharashtra cash crops
  - Standard commercial fertilizer composition tables
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class FertilizerService:

    @staticmethod
    def calculate(
        crop: str,
        soil_N: float | None = None,
        soil_P: float | None = None,
        soil_K: float | None = None,
    ) -> dict:
        """
        Compute commercial fertilizer quantities (DAP & SSP recipes) and growth-stage
        split application schedules. If soil test values are omitted, computes the
        standard ICAR Recommended Dose of Fertilizer (RDF) for the crop.
        """
        crop_key = crop.lower()
        targets = config.CROP_NPK_TARGETS.get(
            crop_key,
            config.CROP_NPK_TARGETS["wheat"]  # sensible default
        )

        t_N, t_P, t_K = targets["N"], targets["P"], targets["K"]

        is_standard_pop = soil_N is None or soil_P is None or soil_K is None
        if is_standard_pop:
            d_N = t_N
            d_P = t_P
            d_K = t_K
            soil_repr = None
            interpretation = (
                f"Standard ICAR Package of Practices (PoP) recommended fertilizer dosage for {crop.title()}. "
                f"Prescribes balanced basal and split top-dressing applications for optimal seasonal yield."
            )
        else:
            d_N = max(0.0, t_N - float(soil_N))
            d_P = max(0.0, t_P - float(soil_P))
            d_K = max(0.0, t_K - float(soil_K))
            soil_repr = {"N": round(float(soil_N), 1), "P": round(float(soil_P), 1), "K": round(float(soil_K), 1)}
            interpretation = FertilizerService._interpret(d_N, d_P, d_K, t_N, t_P, t_K)

        comp = config.FERTILIZER_COMPOSITION

        # ── 1. Standard DAP + Urea + MOP Recipe ──────────────────────────────
        dap_qty      = d_P / comp["DAP"]["P"]
        n_from_dap   = dap_qty * comp["DAP"]["N"]
        n_remaining  = max(0.0, d_N - n_from_dap)
        urea_qty     = n_remaining / comp["Urea"]["N"]
        mop_qty      = d_K / comp["MOP"]["K"]

        # ── 2. Alternative SSP (Single Superphosphate) Recipe ────────────────
        ssp_qty      = d_P / comp["SSP"]["P"]
        ssp_urea_qty = d_N / comp["Urea"]["N"]
        ssp_mop_qty  = mop_qty

        # ── 3. Surplus N warning ─────────────────────────────────────────────
        surplus_n_warning: str | None = None
        if n_from_dap > d_N and d_P > 0:
            excess = round(n_from_dap - d_N, 1)
            surplus_n_warning = (
                f"DAP application will supply {excess} kg/ha of N beyond the deficit. "
                f"Reduce or skip Urea to avoid excess nitrogen, which can cause vegetative "
                f"overgrowth, lodging, and increased disease susceptibility. Alternatively, "
                f"use Single Superphosphate (SSP)."
            )

        # ── 4. Growth-Stage Split Application Schedule ───────────────────────
        split_schedule = {
            "basal": {
                "stage": "Basal (At Sowing / Transplanting)",
                "DAP_kg_ha": round(dap_qty, 1),
                "SSP_kg_ha": round(ssp_qty, 1),
                "Urea_kg_ha": round(urea_qty * 0.333, 1),
                "MOP_kg_ha": round(mop_qty, 1),
                "instructions": "Apply 100% Phosphorus (DAP or SSP), 100% Potash (MOP), and 1/3rd Nitrogen (Urea) into the root zone at sowing.",
            },
            "vegetative_30d": {
                "stage": "Vegetative Growth (30–35 Days After Sowing)",
                "Urea_kg_ha": round(urea_qty * 0.333, 1),
                "instructions": "Top-dress 1/3rd Nitrogen (Urea) along the crop rows followed by light irrigation.",
            },
            "flowering_60d": {
                "stage": "Flowering / Panicle Initiation (60–65 Days After Sowing)",
                "Urea_kg_ha": round(urea_qty * 0.334, 1),
                "instructions": "Top-dress remaining Nitrogen (Urea) to support grain/fruit development.",
            },
        }

        # ── 5. Commercial Bags & Financial Economics (Per Hectare Baseline) ─
        bag_prices = getattr(config, "FERTILIZER_BAG_PRICES", {
            "Urea": 267.0, "DAP": 1350.0, "MOP": 1700.0, "SSP": 500.0
        })

        urea_r_kg = round(urea_qty, 1)
        dap_r_kg  = round(dap_qty, 1)
        mop_r_kg  = round(mop_qty, 1)

        commercial_bags_ha = {
            "Urea": {
                "kg": urea_r_kg,
                "bags_50kg": round(urea_r_kg / 50.0, 1),
                "bag_price_inr": bag_prices["Urea"],
                "cost_inr": round((urea_r_kg / 50.0) * bag_prices["Urea"], 0),
            },
            "DAP": {
                "kg": dap_r_kg,
                "bags_50kg": round(dap_r_kg / 50.0, 1),
                "bag_price_inr": bag_prices["DAP"],
                "cost_inr": round((dap_r_kg / 50.0) * bag_prices["DAP"], 0),
            },
            "MOP": {
                "kg": mop_r_kg,
                "bags_50kg": round(mop_r_kg / 50.0, 1),
                "bag_price_inr": bag_prices["MOP"],
                "cost_inr": round((mop_r_kg / 50.0) * bag_prices["MOP"], 0),
            },
        }
        total_fert_cost_ha = sum(item["cost_inr"] for item in commercial_bags_ha.values())

        return {
            "crop":   crop.title(),
            "mode":   "standard_pop" if is_standard_pop else "soil_test",
            "target": {"N": t_N, "P": t_P, "K": t_K},
            "soil":   soil_repr,
            "deficit": {"N": round(d_N, 1),   "P": round(d_P, 1),   "K": round(d_K, 1)},
            "fertilizers": {
                "DAP":  round(dap_qty, 1),
                "Urea": round(urea_qty, 1),
                "MOP":  round(mop_qty, 1),
            },
            "ssp_alternative": {
                "SSP":  round(ssp_qty, 1),
                "Urea": round(ssp_urea_qty, 1),
                "MOP":  round(ssp_mop_qty, 1),
                "sulfur_kg_ha": round(ssp_qty * comp["SSP"].get("S", 0.11), 1),
            },
            "commercial_bags":  commercial_bags_ha,
            "total_cost_inr_ha": total_fert_cost_ha,
            "split_schedule":   split_schedule,
            "interpretation":   interpretation,
            "surplus_n_warning": surplus_n_warning,
        }

    @staticmethod
    def _interpret(d_N, d_P, d_K, t_N, t_P, t_K) -> str:
        total_deficit_pct = (
            (d_N / t_N if t_N else 0)
            + (d_P / t_P if t_P else 0)
            + (d_K / t_K if t_K else 0)
        ) / 3 * 100

        if total_deficit_pct == 0:
            return "Soil nutrients are optimal. No fertilizer application required."
        elif total_deficit_pct < 20:
            return "Minor nutrient deficiency detected. Light top-dress application recommended."
        elif total_deficit_pct < 50:
            return "Moderate deficiency. Apply recommended doses in split applications (basal + top-dress)."
        else:
            return "Severe nutrient deficiency. Immediate basal application required; consider soil amendment."
