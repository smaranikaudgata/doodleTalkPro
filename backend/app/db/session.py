import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Load variables from your .env file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "../../../.env"))

load_dotenv(ENV_PATH, override=True)

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
# Use localhost for local dev, fallback to 'db' for Docker
DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1") 

# Build the exact URLs dynamically
ASYNC_DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SYNC_DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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