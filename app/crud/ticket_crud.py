from datetime import datetime, timezone
from app.models.tickets import Ticket
from app.schema.ticket_schema import TicketResponse, TicketCreateDatabase, TicketUpdate
from sqlalchemy import select, func
from typing import Optional


async def create_ticket(db, ticket: TicketCreateDatabase) -> Ticket:
    db_ticket = Ticket(**ticket.model_dump())
    db.add(db_ticket)
    await db.commit()
    await db.refresh(db_ticket)
    return db_ticket


async def get_ticket_by_title(db, ticket_title: str) -> Optional[Ticket]:
    result = await db.execute(select(Ticket).where(Ticket.title == ticket_title))
    return result.scalar_one_or_none()


async def get_ticket_by_id(db, ticket_id: str) -> Optional[Ticket]:
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    return result.scalar_one_or_none()


async def list_tickets(db, limit: int = 100, offset: int = 0):
    """
    Lister les tickets
    """
    query = select(Ticket)
    query = query.offset(offset).limit(limit)
    count_query = select(func.count()).select_from(Ticket)
    count = (await db.execute(count_query)).scalar()
    result = await db.execute(query)
    return result.scalars().all(), count


async def update_ticket(
    db, ticket_id: str, ticket_payload: TicketUpdate
) -> TicketResponse:
    """
    Lister les tickets
    """
    ticket = await get_ticket_by_id(db, ticket_id)
    update_data = ticket_payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(ticket, key):
            setattr(ticket, key, value)
        ticket.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(ticket)
    return ticket
