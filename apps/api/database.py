import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# 1. Ensure python-dotenv loads root .env
env_path = find_dotenv(usecwd=True)
if not env_path:
    env_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
db_configured = bool(DATABASE_URL)
db_connected = False

# 2. Ensure DATABASE_URL uses postgresql+psycopg://
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    
    if "sslmode=" not in DATABASE_URL:
        sep = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL += f"{sep}sslmode=require"
        
    DATABASE_URL = DATABASE_URL.replace("&channel_binding=require", "").replace("?channel_binding=require&", "?").replace("?channel_binding=require", "")

try:
    if DATABASE_URL:
        # Echo is False so we don't accidentally leak credentials in logs
        engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"connect_timeout": 15})
        AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    else:
        engine = None
except Exception as e:
    print(f"Failed to initialize database engine: {type(e).__name__}")
    engine = None

async def get_db():
    if not engine:
        raise HTTPException(status_code=500, detail="Database not configured")
    async with AsyncSessionLocal() as session:
        yield session

async def check_db_connection() -> bool:
    if not engine:
        return False
    try:
        async with asyncio.timeout(15.0):
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {type(e).__name__} - Could not connect to DB")
        return False
