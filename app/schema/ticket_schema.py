from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class TicketStatus(str, Enum):
    OPEN = "open"
    STALLED = "stalled"
    CLOSED = "closed"


class TicketStatusUpdate(str, Enum):
    OPEN = "open"
    STALLED = "stalled"


class TicketBase(BaseModel):
    title: str = Field(
        pattern=r"^[A-Za-z0-9À-ÿ \-’'\.,]+$",
        examples=["Bug de connexion", "Nouvelle fonctionnalité"],
        min_length=8,
        max_length=256,
        description="Le titre ne peut contenir que lettres, chiffres, \
            espaces ou tirets",
    )
    description: str = Field(
        pattern=r"^[A-Za-z0-9À-ÿ \-’'\.,]+$",
        min_length=8,
        max_length=1024,
        examples=[
            "L'utilisateur ne peut pas se connecter\
            après la mise à jour"
        ],
        description="La description ne peut contenir que lettres, chiffres, \
            espaces ou tirets",
    )


class TicketCreatePublic(TicketBase):
    pass


class TicketCreateDatabase(TicketBase):
    updated_at: datetime
    created_at: datetime
    status: TicketStatus


class TicketResponse(TicketCreateDatabase):
    id: UUID = Field(default_factory=uuid4)
    model_config = ConfigDict(from_attributes=True)


class TicketsList(BaseModel):
    tickets: list[TicketResponse]
    total: int
    offset: int = 0
    limit: int = 100


class TicketUpdate(TicketBase):
    status: TicketStatus


class TicketUpdateStatus(BaseModel):
    status: TicketStatus
