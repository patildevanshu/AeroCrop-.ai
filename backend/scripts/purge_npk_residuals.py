"""
backend/scripts/purge_npk_residuals.py

Performs an exhaustive purge and verification of any residual NPK, soil,
and fertilizer fields across:
1. Active MongoDB database collections ('analyses', 'farm_plots', etc.)
2. Legacy SQLite database file (data/aerocrop.db)
"""

import os
import sqlite3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQLITE_PATH = os.path.join(PROJECT_ROOT, "data", "aerocrop.db")
MONGODB_URL = os.getenv("MONGODB_URL", os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
DB_NAME = os.getenv("MONGODB_DB_NAME", "aerocrop")


async def purge_mongodb():
    print(f"Connecting to MongoDB at {MONGODB_URL} (db: {DB_NAME})...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    # 1. Unset residual fields in 'analyses' collection if present
    res = await db.analyses.update_many(
        {"$or": [{"soil": {"$exists": True}}, {"fertilizer": {"$exists": True}}]},
        {"$unset": {"soil": "", "fertilizer": ""}},
    )
    print(f"Purged NPK/fertilizer fields from {res.modified_count} analyses documents.")

    # Verify zero documents remain with soil or fertilizer
    remaining = await db.analyses.count_documents(
        {"$or": [{"soil": {"$exists": True}}, {"fertilizer": {"$exists": True}}]}
    )
    print(f"Analyses documents with residual NPK/fertilizer: {remaining}")
    client.close()


def inspect_and_clean_sqlite():
    if not os.path.exists(SQLITE_PATH):
        print(f"SQLite database {SQLITE_PATH} not present.")
        return

    print(f"Inspecting SQLite database at {SQLITE_PATH}...")
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables found:", [t[0] for t in tables])

    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name});")
        cols = [col[1] for col in cursor.fetchall()]
        print(f"Table '{table_name}' initial columns: {cols}")

    # Drop residual columns from farm_plots
    cursor.execute("PRAGMA table_info(farm_plots);")
    fp_cols = [c[1] for c in cursor.fetchall()]
    for col in ["baseline_N", "baseline_P", "baseline_K"]:
        if col in fp_cols:
            cursor.execute(f"ALTER TABLE farm_plots DROP COLUMN {col};")
            print(f"Dropped {col} from farm_plots")

    # Drop residual columns from diagnosis_records
    cursor.execute("PRAGMA table_info(diagnosis_records);")
    dr_cols = [c[1] for c in cursor.fetchall()]
    for col in ["soil_N", "soil_P", "soil_K", "fertilizer_urea_kg", "fertilizer_dap_kg", "fertilizer_mop_kg"]:
        if col in dr_cols:
            cursor.execute(f"ALTER TABLE diagnosis_records DROP COLUMN {col};")
            print(f"Dropped {col} from diagnosis_records")

    conn.commit()

    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name});")
        cols = [col[1] for col in cursor.fetchall()]
        print(f"Table '{table_name}' cleaned columns: {cols}")

    conn.close()


if __name__ == "__main__":
    print("=== AeroCrop NPK Residual Purge & Audit ===")
    asyncio.run(purge_mongodb())
    inspect_and_clean_sqlite()
    print("=== Complete ===")
