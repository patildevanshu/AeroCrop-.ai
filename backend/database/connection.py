"""
AeroCrop.ai — Legacy Async Database Connection & Session Management

[DEPRECATED]
Primary persistence has migrated to MongoDB (backend.database.mongodb).
This module is preserved strictly for legacy SQLite archival and migration utilities.
Do NOT use for new endpoints or services.
"""

import logging
import os
import warnings
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

try:
    import config
    from database.models import Base
except ImportError:
    import backend.config as config
    from backend.database.models import Base

logger = logging.getLogger("aerocrop.database.legacy")


# Ensure local data directory and uploads directory exist
os.makedirs(config.DATA_DIR, exist_ok=True)
os.makedirs(config.UPLOADS_DIR, exist_ok=True)

# Engine connection kwargs based on database backend
engine_kwargs = {"echo": False}
if config.DATABASE_URL.startswith("sqlite"):
    # SQLite connection optimizations for async access with timeout and busy handler
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30.0}
else:
    # Production pool settings for PostgreSQL
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 3600  # Recycle connections after 1 hour

engine = create_async_engine(config.DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database tables on application startup."""
    try:
        async with engine.begin() as conn:
            # For SQLite, enable foreign keys and WAL mode for better concurrency
            if config.DATABASE_URL.startswith("sqlite"):
                from sqlalchemy import text
                await conn.execute(text("PRAGMA journal_mode=WAL;"))
            if Base is not None and hasattr(Base, "metadata"):
                await conn.run_sync(Base.metadata.create_all)
            else:
                logger.debug("[Legacy Database] Base is None; skipping SQLAlchemy table auto-generation (managed by MongoDB).")

            # Auto-migration: Ensure new columns and constraints exist on existing SQLite tables
            if config.DATABASE_URL.startswith("sqlite"):
                from sqlalchemy import text
                try:
                    info_res = await conn.execute(text("PRAGMA table_info(users);"))
                    cols = [row[1] for row in info_res.fetchall()]
                    if cols and "token_version" not in cols:
                        await conn.execute(text("ALTER TABLE users ADD COLUMN token_version INTEGER DEFAULT 1;"))
                        logger.info("[Database] Migrated 'users' table: added 'token_version' column.")
                except Exception as mig_err:
                    logger.debug("[Database] Migration skipped or not needed: %s", mig_err)

                try:
                    diag_info = await conn.execute(text("PRAGMA table_info(diagnosis_records);"))
                    diag_cols = diag_info.fetchall()
                    col_names = [row[1] for row in diag_cols]
                    if diag_cols and ("soil_N" in col_names or "fertilizer_urea_kg" in col_names):
                        await conn.execute(text("PRAGMA foreign_keys=OFF;"))
                        await conn.execute(text("""
                            CREATE TABLE IF NOT EXISTS diagnosis_records_new (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                                plot_id INTEGER REFERENCES farm_plots(id) ON DELETE SET NULL,
                                crop_type VARCHAR(64) NOT NULL,
                                district VARCHAR(64) NOT NULL,
                                image_filename VARCHAR(255),
                                image_url VARCHAR(255),
                                disease_class_idx INTEGER NOT NULL,
                                disease_name VARCHAR(160) NOT NULL,
                                confidence FLOAT NOT NULL,
                                severity VARCHAR(32) DEFAULT 'None',
                                is_healthy BOOLEAN DEFAULT 0,
                                predicted_yield_t_ha FLOAT DEFAULT 0.0,
                                weather_temp FLOAT DEFAULT 0.0,
                                weather_hum FLOAT DEFAULT 0.0,
                                weather_rain FLOAT DEFAULT 0.0,
                                mock_mode BOOLEAN DEFAULT 0,
                                low_confidence BOOLEAN DEFAULT 0,
                                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                            );
                        """))
                        common_cols = [c for c in col_names if c in [
                            "id", "user_id", "plot_id", "crop_type", "district",
                            "image_filename", "image_url", "disease_class_idx",
                            "disease_name", "confidence", "severity", "is_healthy",
                            "predicted_yield_t_ha", "weather_temp", "weather_hum",
                            "weather_rain", "mock_mode", "low_confidence", "created_at"
                        ]]
                        cols_str = ", ".join(common_cols)
                        await conn.execute(text(f"INSERT INTO diagnosis_records_new ({cols_str}) SELECT {cols_str} FROM diagnosis_records;"))
                        await conn.execute(text("DROP TABLE diagnosis_records;"))
                        await conn.execute(text("ALTER TABLE diagnosis_records_new RENAME TO diagnosis_records;"))
                        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_diagnosis_records_user_id ON diagnosis_records (user_id);"))
                        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_diagnosis_records_plot_id ON diagnosis_records (plot_id);"))
                        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_diagnosis_records_created_at ON diagnosis_records (created_at);"))
                        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_user_diagnoses_created_at ON diagnosis_records (user_id, created_at DESC);"))
                        await conn.execute(text("PRAGMA foreign_keys=ON;"))
                        logger.info("[Database] Migrated 'diagnosis_records' table: purged NPK and fertilizer columns.")
                except Exception as mig_err:
                    logger.debug("[Database] diagnosis_records migration skipped or not needed: %s", mig_err)

        logger.info("[Database] Tables initialized successfully at %s", config.DATABASE_URL)
    except Exception as exc:
        logger.error("[Database] Table initialization error: %s", exc)
        raise exc


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding database sessions per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
