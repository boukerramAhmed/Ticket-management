from sqlalchemy.orm import DeclarativeBase
from app.core.database.meta import meta
from app.core.database.dependencies import engine


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
