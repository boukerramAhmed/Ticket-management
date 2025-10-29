from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.core.database.base import Base
from uuid import uuid4
from app.schema.ticket_schema import TicketStatus


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False, default=TicketStatus.OPEN.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
