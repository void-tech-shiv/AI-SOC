import asyncio
import os
import sys

from dotenv import load_dotenv, find_dotenv
env_path = find_dotenv(usecwd=True)
if not env_path:
    env_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(env_path)

from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from apps.api.models import SecurityLog

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

    async with AsyncSessionLocal() as session:
        print("Cleaning up logs...")
        
        stmt1 = delete(SecurityLog).where(SecurityLog.source == 'test_script')
        res1 = await session.execute(stmt1)
        
        stmt2 = delete(SecurityLog).where(SecurityLog.severity.not_in(['low', 'medium', 'high', 'critical']))
        res2 = await session.execute(stmt2)
        
        stmt3 = text("""
            DELETE FROM security_logs
            WHERE id IN (
                SELECT id
                FROM (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY timestamp, source, event_type, ip_address, message
                               ORDER BY id ASC
                           ) as row_num
                    FROM security_logs
                ) sub
                WHERE sub.row_num > 1
            )
        """)
        res3 = await session.execute(stmt3)
        
        # Get count of remaining logs
        res4 = await session.execute(text("SELECT COUNT(*) FROM security_logs"))
        remaining = res4.scalar()
        
        await session.commit()
        print(f"Deleted {res1.rowcount} test logs and {res2.rowcount} invalid severity logs.")
        print(f"Removed {res3.rowcount} duplicate logs.")
        print(f"Remaining logs: {remaining}")

    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
