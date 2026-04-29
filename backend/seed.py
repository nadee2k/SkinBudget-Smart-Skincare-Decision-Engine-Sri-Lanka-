import asyncio
from pathlib import Path

import asyncpg

from .config import get_settings


SEED_FILE = Path(__file__).resolve().parent.parent / "db" / "seeds" / "reference_data.sql"


async def seed_reference_data():
    settings = get_settings()
    sql = SEED_FILE.read_text(encoding="utf-8")
    connection = await asyncpg.connect(dsn=settings.db_dsn)
    try:
        await connection.execute(sql)
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(seed_reference_data())

