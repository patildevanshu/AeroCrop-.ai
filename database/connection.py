"""
AeroCrop.ai — Async Database Connection & Session Management

Provides:
  - Async SQLAlchemy engine configuration
  - Scoped async session maker
  - FastAPI dependency generator: get_db()
  - Database schema initialization: init_db()
"""

import logging
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import config
from database.models import Base

logger = logging.getLogger("aerocrop.database")

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
                await conn.execute(text("PRAGMA foreign_keys=ON;"))
            await conn.run_sync(Base.metadata.create_all)

            # Auto-migration: Ensure new columns exist on existing SQLite tables
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
