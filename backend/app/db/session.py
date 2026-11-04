import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Grab database URLs from your docker-compose.yml
ASYNC_DB_URL = os.getenv("DATABASE_ASYNC_URL", "postgresql+asyncpg://admin:password@db:5432/doodletalk")
SYNC_DB_URL = os.getenv("DATABASE_SYNC_URL", "postgresql+psycopg2://admin:password@db:5432/doodletalk")

# 2. Async Engine for FastAPI (Handles web traffic instantly)
engine_async = create_async_engine(ASYNC_DB_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine_async, expire_on_commit=False)

# 3. Sync Engine for Celery (Handles heavy PDF processing in the background)
engine_sync = create_engine(SYNC_DB_URL, echo=False)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)

# 4. The Base class that all your models will inherit from
Base = declarative_base()

# 5. Dependency generator to inject the database into your FastAPI routes
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session