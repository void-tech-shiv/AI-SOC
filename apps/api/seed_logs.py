import asyncio
import json
import os
import sys

# Ensure python-dotenv loads root .env
from dotenv import load_dotenv, find_dotenv
env_path = find_dotenv(usecwd=True)
if not env_path:
    env_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(env_path)

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from apps.api.models import Base, SecurityLog

async def main():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("DATABASE_URL is not set.")
        return

    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    
    if "sslmode=" not in DATABASE_URL:
        sep = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL += f"{sep}sslmode=require"
        
    DATABASE_URL = DATABASE_URL.replace("&channel_binding=require", "").replace("?channel_binding=require&", "?").replace("?channel_binding=require", "")

    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)

    log_file_path = os.path.join(os.path.dirname(__file__), "../../data/synthetic-logs/sample_logs.json")
    if not os.path.exists(log_file_path):
        print(f"File not found: {log_file_path}")
        return

    with open(log_file_path, "r") as f:
        logs = json.load(f)

    from sqlalchemy import select
    import dateutil.parser

    async with AsyncSessionLocal() as session:
        print("Inserting logs...")
        inserted = 0
        skipped_existing = 0
        failed = 0

        for log_data in logs:
            dt_str = log_data.get("timestamp")
            dt = dateutil.parser.isoparse(dt_str) if dt_str else None
            
            stmt = select(SecurityLog).where(
                SecurityLog.timestamp == dt,
                SecurityLog.source == log_data.get("source"),
                SecurityLog.event_type == log_data.get("event_type"),
                SecurityLog.ip_address == log_data.get("ip_address"),
                SecurityLog.message == log_data.get("message")
            )
            result = await session.execute(stmt)
            if result.scalars().first() is None:
                log_entry = SecurityLog(
                    timestamp=dt,
                    source=log_data.get("source"),
                    event_type=log_data.get("event_type"),
                    severity=log_data.get("severity"),
                    username=log_data.get("username"),
                    ip_address=log_data.get("ip_address"),
                    message=log_data.get("message"),
                    raw_event=log_data.get("raw_event")
                )
                session.add(log_entry)
                try:
                    await session.commit()
                    inserted += 1
                except Exception:
                    await session.rollback()
                    failed += 1
            else:
                skipped_existing += 1
                
        print(f"inserted = {inserted}, skipped_existing = {skipped_existing}, failed = {failed}")

    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
