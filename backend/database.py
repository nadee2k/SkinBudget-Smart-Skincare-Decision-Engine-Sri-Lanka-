import asyncpg
import logging
from .config import get_settings

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            settings = get_settings()
            self.pool = await asyncpg.create_pool(
                dsn=settings.db_dsn,
                min_size=1,
                max_size=10,
                command_timeout=30,
            )
            logger.info("Database connected.")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            logger.info("Database disconnected.")

    async def fetch(self, query: str, *args):
        if not self.pool:
            raise Exception("Database not connected")
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def execute(self, query: str, *args):
        if not self.pool:
            raise Exception("Database not connected")
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        if not self.pool:
            raise Exception("Database not connected")
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def health_check(self):
        if not self.pool:
            raise Exception("Database not connected")
        async with self.pool.acquire() as connection:
            await connection.execute("SELECT 1")

db = Database()
