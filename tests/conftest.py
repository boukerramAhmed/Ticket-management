from typing import AsyncGenerator
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings
import pytest
import pytest_asyncio
from app.core.database.base import Base
from app.core.database.dependencies import get_db_session
from httpx import AsyncClient
from app.main import app
from pathlib import Path
import json
from datetime import datetime
from app.models.tickets import Ticket
from httpx import ASGITransport, AsyncClient


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True, scope="function")
async def clear_db(db_session: AsyncSession):
    # Avant : on peut aussi supprimer toutes les données
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(delete(table))
    await db_session.commit()
    yield
    # Après : idem, assure que tout est vide
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(delete(table))
    await db_session.commit()


@pytest_asyncio.fixture(scope="session")
async def initialize_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(initialize_db):
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def load_test_tickets(db_session: AsyncSession):
    """Load test tickets from JSON file."""
    test_data_path = Path(__file__).parent / "data" / "tickets.json"
    if not test_data_path.exists():
        raise FileNotFoundError(f"Test data file not found: {test_data_path}")
    with open(test_data_path, "r", encoding="utf-8") as f:
        tickets_data = json.load(f)
    tickets = []
    for ticket_data in tickets_data:
        try:
            ticket_data["created_at"] = datetime.fromisoformat(
                ticket_data["created_at"].replace("Z", "+00:00")
            )
            ticket_data["updated_at"] = datetime.fromisoformat(
                ticket_data["updated_at"].replace("Z", "+00:00")
            )
            user = Ticket(**ticket_data)
            db_session.add(user)
            tickets.append(user)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid user data: {ticket_data}") from e
    await db_session.commit()
    return tickets


@pytest_asyncio.fixture
@pytest.mark.anyio
async def client(db_session):
    async def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
