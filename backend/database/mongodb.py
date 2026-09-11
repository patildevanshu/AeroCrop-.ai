"""
AeroCrop.ai — Asynchronous MongoDB Connection & Lifecycle Manager

Provides:
  - Motor AsyncIOMotorClient singleton with connection pooling
  - Schema & collection index initialization
  - Atomic auto-increment integer sequence generation for ID compatibility
  - FastAPI dependency generator: get_db()
"""

import logging
from typing import AsyncGenerator, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ReturnDocument

import asyncio
import backend.config as config

logger = logging.getLogger("aerocrop.database.mongodb")

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


def get_client() -> AsyncIOMotorClient:
    """Return active AsyncIOMotorClient instance bound to current running event loop."""
    global client, db
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if client is not None:
        loop_attr = getattr(client, "io_loop", None)
        if loop_attr and (loop_attr.is_closed() or (current_loop and loop_attr is not current_loop)):
            client = None
            db = None

    if client is None:
        client = AsyncIOMotorClient(
            config.MONGODB_URL,
            maxPoolSize=50,
            minPoolSize=5,
            serverSelectionTimeoutMS=5000,
        )
        db = client[config.MONGODB_DB_NAME]
    return client


def get_database() -> AsyncIOMotorDatabase:
    """Return active AsyncIOMotorDatabase instance."""
    c = get_client()
    return c[config.MONGODB_DB_NAME]


async def init_mongodb() -> None:
    """
    Initialize MongoDB connection, verify connectivity,
    and create required collection indexes and sequence counters.
    """
    global client, db
    logger.info("[MongoDB] Connecting to %s (database: %s)", config.MONGODB_URL, config.MONGODB_DB_NAME)
    
    client = get_client()
    db = client[config.MONGODB_DB_NAME]

    # Verify server is responsive with retry loop
    connected = False
    for attempt in range(1, 6):
        try:
            await client.admin.command("ping")
            logger.info("[MongoDB] Ping successful! Connected to MongoDB server.")
            connected = True
            break
        except Exception as exc:
            logger.warning("[MongoDB] Connection attempt %d/5 failed (%s). Retrying in 2s...", attempt, exc)
            await asyncio.sleep(2)

    if not connected:
        logger.error("[MongoDB] Could not establish MongoDB connection after 5 attempts.")
        raise ConnectionError(f"Could not connect to MongoDB at {config.MONGODB_URL}")

    # Ensure indexes on collections
    try:
        # Users indexes with partial filter expressions for optional unique fields
        await db.users.create_index([("id", 1)], unique=True, background=True)
        await db.users.create_index(
            [("phone_number", 1)],
            unique=True,
            partialFilterExpression={"phone_number": {"$type": "string"}},
            background=True,
        )
        await db.users.create_index(
            [("email", 1)],
            unique=True,
            partialFilterExpression={"email": {"$type": "string"}},
            background=True,
        )
        
        # Farm plots indexes
        await db.farm_plots.create_index([("id", 1)], unique=True, background=True)
        await db.farm_plots.create_index([("user_id", 1), ("id", -1)], background=True)

        # Analyses / diagnoses indexes
        await db.analyses.create_index([("id", 1)], unique=True, background=True)
        await db.analyses.create_index([("user_id", 1), ("created_at", -1)], background=True)
        await db.analyses.create_index([("plot_id", 1)], background=True)
        await db.analyses.create_index([("crop_type", 1)], background=True)

        # Initialize sequence counters if missing
        for seq_name in ("user_id", "plot_id", "analysis_id"):
            existing = await db.counters.find_one({"_id": seq_name})
            if not existing:
                await db.counters.insert_one({"_id": seq_name, "seq": 0})

        logger.info("[MongoDB] Indexes & sequence counters initialized successfully.")
    except Exception as exc:
        logger.warning("[MongoDB] Warning while configuring indexes: %s", exc)


async def close_mongodb() -> None:
    """Close MongoDB connection pool on server shutdown."""
    global client, db
    if client is not None:
        client.close()
        client = None
        db = None
        logger.info("[MongoDB] Connection closed gracefully.")


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    FastAPI dependency yielding the async MongoDB database instance.
    Usage in endpoint:
        db: AsyncIOMotorDatabase = Depends(get_db)
    """
    yield get_database()


async def get_next_sequence(sequence_name: str) -> int:
    """
    Atomically increment and return the next integer ID sequence value.
    Provides backward compatibility with integer IDs in the frontend & JWT claims.
    """
    database = get_database()
    doc = await database.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])
