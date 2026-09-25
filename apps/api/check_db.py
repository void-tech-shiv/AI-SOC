import os
import sys
import asyncio
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load root .env explicitly
env_path = find_dotenv(usecwd=True)
if not env_path:
    env_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(env_path)

async def check_database():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL is not set.")
        return False
        
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        
    try:
        engine = create_async_engine(database_url, connect_args={"connect_timeout": 3})
        async with asyncio.timeout(3.0):
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
        print("Database connected successfully.")
        return True
    except Exception as e:
        print(f"Error: {type(e).__name__} - Connection failed.")
        return False

if __name__ == "__main__":
    asyncio.run(check_database())
