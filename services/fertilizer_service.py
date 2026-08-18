"""
AeroCrop.ai — Fertilizer Service

Calculates commercial fertilizer dosages required to correct soil NPK deficits.

Math:
  DAP qty  = D_P / 0.46
  N from DAP = DAP_qty * 0.18
  Urea qty = max(0, D_N - N_from_DAP) / 0.46
  MOP qty  = D_K / 0.60

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
    def calculate(crop: str, soil_N: float, soil_P: float, soil_K: float) -> dict:
        """
        Compute NPK deficits and recommended commercial fertilizer quantities.

        Args:
            crop   : crop name (cotton | wheat | maize | rice | potato)
            soil_N : current soil Nitrogen   (kg/ha)
            soil_P : current soil Phosphorus (kg/ha)
            soil_K : current soil Potassium  (kg/ha)

        Returns:
            {
                "crop"          : str,
                "target"        : {N, P, K},
                "soil"          : {N, P, K},
                "deficit"       : {N, P, K},
                "fertilizers"   : {
                    "DAP"  : float,   # kg/ha
                    "Urea" : float,   # kg/ha
                    "MOP"  : float,   # kg/ha
                },
                "interpretation": str,
            }
        """
        crop_key = crop.lower()
        targets = config.CROP_NPK_TARGETS.get(
            crop_key,
            config.CROP_NPK_TARGETS["wheat"]  # sensible default
        )

        t_N, t_P, t_K = targets["N"], targets["P"], targets["K"]
        d_N = max(0.0, t_N - soil_N)
        d_P = max(0.0, t_P - soil_P)
        d_K = max(0.0, t_K - soil_K)

        # ── DAP first (satisfies Phosphorus, also contributes some N) ────────
        comp = config.FERTILIZER_COMPOSITION
        dap_qty      = d_P / comp["DAP"]["P"]
        n_from_dap   = dap_qty * comp["DAP"]["N"]
        n_remaining  = max(0.0, d_N - n_from_dap)
        urea_qty     = n_remaining / comp["Urea"]["N"]
        mop_qty      = d_K / comp["MOP"]["K"]

        interpretation = FertilizerService._interpret(d_N, d_P, d_K, t_N, t_P, t_K)

        return {
            "crop":   crop.title(),
            "target": {"N": t_N, "P": t_P, "K": t_K},
            "soil":   {"N": round(soil_N, 1), "P": round(soil_P, 1), "K": round(soil_K, 1)},
            "deficit": {"N": round(d_N, 1),   "P": round(d_P, 1),   "K": round(d_K, 1)},
            "fertilizers": {
                "DAP":  round(dap_qty, 1),
                "Urea": round(urea_qty, 1),
                "MOP":  round(mop_qty, 1),
            },
            "interpretation": interpretation,
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
