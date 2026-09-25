import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from apps.api.database import engine, get_db

async def cleanup():
    # Only run in development
    env = os.environ.get("ENVIRONMENT", "development")
    if env != "development":
        print("Not in development environment. Aborting.")
        return

    async with engine.begin() as conn:
        # Delete incident alerts
        res_alerts = await conn.execute(text("DELETE FROM incident_alerts;"))
        deleted_links = res_alerts.rowcount
        
        # Delete incidents
        res_inc = await conn.execute(text("DELETE FROM incidents;"))
        deleted_incidents = res_inc.rowcount
        
        print(f"Deleted {deleted_links} incident alert links.")
        print(f"Deleted {deleted_incidents} incidents.")

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(cleanup())
