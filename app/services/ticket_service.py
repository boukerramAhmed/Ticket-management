from datetime import datetime, timezone
from typing import Optional
from app.models.tickets import Ticket
from app.schema.ticket_schema import (
    TicketResponse,
    TicketCreatePublic,
    TicketStatus,
    TicketCreateDatabase,
    TicketUpdate,
    TicketUpdateStatus,
)
from app.crud import ticket_crud
from app.schema.ticket_schema import TicketsList
from fastapi import HTTPException, status


async def create_ticket(db, ticket: TicketCreatePublic) -> TicketResponse:
    """
    Creer un nouveau ticket"""

    ticket_db = await get_ticket_by_title(db, ticket.title)
    if ticket_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un ticket avec ce titre existe deja",
        )

    ticket_create_object = TicketCreateDatabase(
        title=ticket.title,
        description=ticket.description,
        status=TicketStatus.OPEN.value,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return await ticket_crud.create_ticket(db=db, ticket=ticket_create_object)


async def list_tickets(db, limit: int = 100, offset: int = 0) -> TicketsList:
    """
    Lister les tickets
    """
    tickets, count = await ticket_crud.list_tickets(db, limit, offset)
    return TicketsList(
        tickets=tickets,
        total=count,
        offset=offset,
        limit=limit,
    )


async def get_ticket_by_title(db, ticket_title: str) -> Optional[Ticket]:
    """Récupérer un ticket par son titre"""
    return await ticket_crud.get_ticket_by_title(db, ticket_title)


async def get_ticket_by_id(db, ticket_id: str) -> Optional[Ticket]:
    """Récupérer un ticket par son ID"""
    if ticket_db := await ticket_crud.get_ticket_by_id(db, ticket_id):
        return ticket_db
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Ticket not found",
    )


async def update_ticket_by_id(db, ticket_id: str, ticket: TicketUpdate) -> Ticket:
    """Mettre a jour un ticket par son ID"""
    _ = await get_ticket_by_id(db, ticket_id)
    return await ticket_crud.update_ticket(
        db=db, ticket_id=ticket_id, ticket_payload=ticket
    )


async def close_ticket_by_id(
    db,
    ticket_id: str,
) -> Ticket:
    """Clore un ticket par son ID"""
    ticket_db = await get_ticket_by_id(db, ticket_id)
    if ticket_db.status == TicketStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is already closed",
        )
    ticket_update = TicketUpdateStatus(status=TicketStatus.CLOSED)
    return await ticket_crud.update_ticket(
        db=db, ticket_id=ticket_id, ticket_payload=ticket_update
    )
