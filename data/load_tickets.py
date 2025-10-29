import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).parent.parent))
from app.models.tickets import Ticket
from sqlalchemy.ext.asyncio import create_async_engine
from app.config.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def insert_tickets():
    engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URL,
        echo=False,
        connect_args=(
            {"check_same_thread": False}
            if "sqlite" in settings.SQLALCHEMY_DATABASE_URL
            else {}
        ),
    )

    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    
    tickets_file = Path(__file__).parent / "tickets.json"
    with open(tickets_file, "r", encoding="utf-8") as f:
        tickets_data = json.load(f)
    tickets = []
    async with AsyncSessionLocal() as session:
        try:
            for ticket_data in tickets_data:
                ticket_data["created_at"] = datetime.fromisoformat(
                    ticket_data["created_at"].replace("Z", "+00:00")
                )
                ticket_data["updated_at"] = datetime.fromisoformat(
                    ticket_data["updated_at"].replace("Z", "+00:00")
                )
                ticket_obj = Ticket(**ticket_data)
                session.add(ticket_obj)
                tickets.append(ticket_obj)
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await engine.dispose()
if __name__ == "__main__":
    asyncio.run(insert_tickets())
  