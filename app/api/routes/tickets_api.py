from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import ticket_service
from app.core.database.dependencies import get_db_session
from uuid import UUID
from app.schema.ticket_schema import (
    TicketCreatePublic,
    TicketResponse,
    TicketsList,
    TicketUpdate,
)


router = APIRouter()


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_payload: TicketCreatePublic, db: AsyncSession = Depends(get_db_session)
):
    """Creer un nouveau ticket"""
    return await ticket_service.create_ticket(db=db, ticket=ticket_payload)


@router.get("/", response_model=TicketsList)
async def get_all_tickets(
    offset: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
):
    """Lister tous les tickets"""
    return await ticket_service.list_tickets(db=db, offset=offset, limit=limit)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket_by_id(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Recuperer un ticket par son ID"""
    return await ticket_service.get_ticket_by_id(db=db, ticket_id=str(ticket_id))


@router.put(
    "/{ticket_id}", response_model=TicketResponse, status_code=status.HTTP_200_OK
)
async def update_ticket_by_id(
    ticket_id: UUID,
    ticket_payload: TicketUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Mettre a jour un ticket par son ID"""
    return await ticket_service.update_ticket_by_id(
        db=db, ticket_id=str(ticket_id), ticket=ticket_payload
    )


@router.patch(
    "/{ticket_id}/close", response_model=TicketResponse, status_code=status.HTTP_200_OK
)
async def close_ticket_by_id(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Clore un ticket par son ID"""
    return await ticket_service.close_ticket_by_id(db=db, ticket_id=str(ticket_id))
