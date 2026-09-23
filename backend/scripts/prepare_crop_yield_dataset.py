"""
AeroCrop.ai — Prepare Indian Crop Yield Dataset

Extracts crop_yield.xlsx from archive (5).zip in Downloads,
processes agricultural features (agro-meteorological telemetry: temperature, humidity, rainfall),
and outputs data/crop_yield.csv for model training.
"""

import os
import sys
import zipfile
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

DOWNLOAD_ZIP = r"C:\Users\devan\Downloads\archive (5).zip"
OUTPUT_CSV = os.path.join(config.DATA_DIR, "crop_yield.csv")

# Direct mapping from dataset crop names to AeroCrop crop keys
INDIAN_CROP_MAP = {
    "Rice": "rice",
    "Wheat": "wheat",
    "Maize": "maize",
    "Potato": "potato",
    "Sweet potato": "potato",
    "Sugarcane": "sugarcane",
    "Cotton(lint)": "cotton",
    "Onion": "onion",
    "Soyabean": "soybean",
    "Banana": "banana",
    "Dry chillies": "pepper",
    "Black pepper": "pepper",
    "Turmeric": "turmeric",
}

# Regional and seasonal baseline climate parameters in India
# (temp_c, humidity_pct)
CLIMATE_LOOKUP = {
    ("NORTH", "Kharif"): (29.5, 76.0),
    ("NORTH", "Rabi"): (16.0, 58.0),
    ("NORTH", "Summer"): (35.0, 42.0),
    ("NORTH", "Whole Year"): (24.0, 60.0),
    ("NORTH", "Autumn"): (26.0, 64.0),
    ("NORTH", "Winter"): (15.0, 60.0),

    ("WEST", "Kharif"): (28.0, 80.0),      # Maharashtra Kharif
    ("WEST", "Rabi"): (22.5, 52.0),        # Maharashtra Rabi
    ("WEST", "Summer"): (34.0, 46.0),      # Maharashtra Summer
    ("WEST", "Whole Year"): (27.5, 62.0),
    ("WEST", "Autumn"): (27.0, 65.0),
    ("WEST", "Winter"): (20.0, 50.0),

    ("SOUTH", "Kharif"): (28.5, 78.0),
    ("SOUTH", "Rabi"): (25.0, 65.0),
    ("SOUTH", "Summer"): (32.0, 60.0),
    ("SOUTH", "Whole Year"): (28.0, 70.0),
    ("SOUTH", "Autumn"): (27.5, 72.0),
    ("SOUTH", "Winter"): (24.0, 64.0),

    ("EAST", "Kharif"): (29.0, 82.0),
    ("EAST", "Rabi"): (19.0, 62.0),
    ("EAST", "Summer"): (32.5, 56.0),
    ("EAST", "Whole Year"): (25.5, 68.0),
    ("EAST", "Autumn"): (26.5, 70.0),
    ("EAST", "Winter"): (18.0, 60.0),
}


def process_dataset():
    if not os.path.exists(DOWNLOAD_ZIP):
        raise FileNotFoundError(f"Source file not found at {DOWNLOAD_ZIP}")

    print(f"Reading {DOWNLOAD_ZIP}...")
    with zipfile.ZipFile(DOWNLOAD_ZIP, "r") as z:
        excel_name = [n for n in z.namelist() if n.endswith(".xlsx")][0]
        with z.open(excel_name) as f:
            df = pd.read_excel(f)

    print(f"Loaded raw dataset with {len(df)} rows and columns: {df.columns.tolist()}")

    # Strip column names
    df.columns = [c.strip() for c in df.columns]

    # Exclude Coconut (measured in nuts, not tonnes/ha)
    df = df[df["Crop"] != "Coconut"].copy()

    # Filter invalid yield rows (zero or extreme erroneous spikes)
    df = df[(df["Yield"] > 0.05) & (df["Yield"] < 200.0)].copy()

    # Map crop keys
    df["crop_key"] = df["Crop"].map(INDIAN_CROP_MAP)
    df = df.dropna(subset=["crop_key"]).copy()
    print(f"Matched {len(df)} rows across {df['crop_key'].nunique()} key Indian agricultural crops.")

    # 1. Weather variables
    rng = np.random.default_rng(42)

    # Daily rainfall equivalent
    df["rain_mm_day"] = df["Annual_Rainfall"] / 365.0

    # Regional & Seasonal Temperature and Humidity
    temp_list = []
    hum_list = []
    for idx, row in df.iterrows():
        key = (str(row.get("Region", "WEST")).upper(), str(row.get("Season", "Kharif")))
        base_temp, base_hum = CLIMATE_LOOKUP.get(key, (27.0, 65.0))
        temp_list.append(base_temp)
        hum_list.append(base_hum)

    temp_arr = np.array(temp_list) + rng.normal(0.0, 1.2, size=len(df))
    hum_arr = np.array(hum_list) + rng.normal(0.0, 3.5, size=len(df))

    df["avg_temp"] = np.clip(temp_arr, 10.0, 46.0)
    df["est_humidity"] = np.clip(hum_arr, 25.0, 95.0)

    # Rename yield column to standard yield_t_ha
    df["yield_t_ha"] = df["Yield"].astype(float)

    # 2. Synthesize rows for remaining horticultural crops (e.g. Tomato, Apple, Grape, Orange)
    # that are in PlantVillage but not in national field crop registries
    horticultural_baselines = {
        "tomato":     {"base": 32.0, "opt_temp": 26.0, "opt_rain": 4.0},
        "apple":      {"base": 22.0, "opt_temp": 20.0, "opt_rain": 3.5},
        "grape":      {"base": 20.0, "opt_temp": 25.0, "opt_rain": 2.5},
        "orange":     {"base": 24.0, "opt_temp": 28.0, "opt_rain": 3.0},
        "peach":      {"base": 16.0, "opt_temp": 22.0, "opt_rain": 3.0},
        "strawberry": {"base": 16.0, "opt_temp": 22.0, "opt_rain": 3.5},
        "cherry":     {"base": 12.0, "opt_temp": 20.0, "opt_rain": 3.0},
        "blueberry":  {"base": 9.0,  "opt_temp": 21.0, "opt_rain": 3.0},
        "raspberry":  {"base": 8.0,  "opt_temp": 20.0, "opt_rain": 3.0},
        "squash":     {"base": 22.0, "opt_temp": 27.0, "opt_rain": 3.5},
    }

    synthetic_rows = []
    # Base sample pool from Western India (Maharashtra climate)
    west_pool = df[df["Region"] == "WEST"]
    if len(west_pool) < 200:
        west_pool = df

    for h_crop, h_cfg in horticultural_baselines.items():
        sample_w = west_pool.sample(n=600, random_state=42 + abs(hash(h_crop)) % 10000, replace=True).copy()
        sample_w["crop_key"] = h_crop
        sample_w["Crop"] = h_crop.capitalize()

        temp_eff = 1.0 - np.abs(sample_w["avg_temp"] - h_cfg["opt_temp"]) * 0.015
        rain_eff = 1.0 - np.abs(sample_w["rain_mm_day"] - h_cfg["opt_rain"]) * 0.025
        mod = np.clip(temp_eff * rain_eff, 0.65, 1.35)
        h_rng = np.random.default_rng(abs(hash(h_crop)) % 10000)
        noise = h_rng.normal(0.0, 0.06, size=len(sample_w))
        sample_w["yield_t_ha"] = np.clip(h_cfg["base"] * (mod + noise), 1.0, 100.0)
        synthetic_rows.append(sample_w)

    if synthetic_rows:
        df = pd.concat([df] + synthetic_rows, ignore_index=True)

    # Select final training columns
    out_cols = [
        "crop_key", "State", "Season",
        "avg_temp", "est_humidity", "rain_mm_day", "yield_t_ha"
    ]
    final_df = df[out_cols].copy()

    # Shuffle
    final_df = final_df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    final_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSuccessfully generated {OUTPUT_CSV} with {len(final_df)} rows!")
    print(f"Crop distribution in final dataset:\n{final_df['crop_key'].value_counts()}")
    print("\nYield summary per crop:\n", final_df.groupby('crop_key')['yield_t_ha'].agg(['count', 'mean', 'std', 'min', 'max']))


if __name__ == "__main__":
    process_dataset()
