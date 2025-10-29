import pytest
from datetime import datetime
from uuid import UUID
from app.schema.ticket_schema import (
    TicketStatus,
    TicketBase,
    TicketCreatePublic,
    TicketCreateDatabase,
    TicketResponse,
    TicketsList,
    TicketUpdate,
    TicketUpdateStatus,
)


import pytest
from datetime import datetime
from uuid import UUID
from app.schema.ticket_schema import (
    TicketStatus,
    TicketBase,
    TicketCreatePublic,
    TicketCreateDatabase,
    TicketResponse,
    TicketsList,
    TicketUpdate,
    TicketUpdateStatus,
)


valid_ticket_data = {
    "title": "Bug de connexion utilisateur",
    "description": "Description valide du probleme"
}


@pytest.mark.parametrize("title,description,valid", [
    ("Bug de connexion", "Description valide du probleme", True),
    ("Nouvelle fonctionnalité", "Ajout d'une nouvelle page de profil", True),
    ("Bu", "Trop court", False), 
    ("a" * 300, "Trop long", False),
    ("Title@#$%", "Caractères invalides", False), 
    ("Bon titre", "a" * 2000, False), 
])
def test_ticket_base_validation(title, description, valid):
    """Test la validation des champs de base d'un ticket."""
    data = {"title": title, "description": description}
    
    if valid:
        ticket = TicketBase(**data)
        assert ticket.title == title
        assert ticket.description == description
    else:
        with pytest.raises(ValueError):
            TicketBase(**data)


def test_ticket_create_public():
    ticket = TicketCreatePublic(**valid_ticket_data)
    assert ticket.title == valid_ticket_data["title"]
    assert ticket.description == valid_ticket_data["description"]


def test_ticket_create_database():
    now = datetime.utcnow()
    data = {
        **valid_ticket_data,
        "created_at": now,
        "updated_at": now,
        "status": TicketStatus.OPEN
    }
    
    ticket = TicketCreateDatabase(**data)
    assert ticket.status == TicketStatus.OPEN
    assert isinstance(ticket.created_at, datetime)
    assert isinstance(ticket.updated_at, datetime)


def test_ticket_response():
    now = datetime.utcnow()
    data = {
        **valid_ticket_data,
        "created_at": now,
        "updated_at": now,
        "status": TicketStatus.OPEN
    }
    
    ticket = TicketResponse(**data)
    assert isinstance(ticket.id, UUID)
    assert ticket.status == TicketStatus.OPEN
    assert ticket.title == valid_ticket_data["title"]


@pytest.mark.parametrize("status", [
    TicketStatus.OPEN,
    TicketStatus.STALLED,
    TicketStatus.CLOSED
])
def test_ticket_status_update(status):
    update = TicketUpdateStatus(status=status)
    assert update.status == status


def test_tickets_list():
    now = datetime.utcnow()
    ticket_data = {
        **valid_ticket_data,
        "created_at": now,
        "updated_at": now,
        "status": TicketStatus.OPEN
    }
    
    ticket = TicketResponse(**ticket_data)
    tickets_list = TicketsList(
        tickets=[ticket],
        total=1,
        offset=0,
        limit=100
    )

    assert len(tickets_list.tickets) == 1
    assert tickets_list.total == 1
    assert tickets_list.offset == 0
    assert tickets_list.limit == 100


@pytest.mark.parametrize("status", [
    "invalid",
    "OPEN", 
    "pending",
    123,  
])
def test_invalid_ticket_status(status):
    with pytest.raises(ValueError):
        TicketUpdateStatus(status=status)


def test_ticket_update():
    data = {
        **valid_ticket_data,
        "status": TicketStatus.STALLED
    }
    
    update = TicketUpdate(**data)
    assert update.title == valid_ticket_data["title"]
    assert update.description == valid_ticket_data["description"]
    assert update.status == TicketStatus.STALLED


@pytest.mark.parametrize("field,value,error_message", [
    ("title", "x" * 300, "String should have at most 256 characters"),
    ("description", "y" * 1500, "String should have at most 1024 characters"),
    ("title", "ab", "String should have at least 8 characters"),
    ("description", "cd", "String should have at least 8 characters"),
    ("title", "Invalid@#$", "String should match pattern"),
    ("description", "Invalid@#$", "String should match pattern"),
])
def test_field_constraints(field, value, error_message):
    """Test détaillé des contraintes sur les champs."""
    data = valid_ticket_data.copy()
    data[field] = value
    
    with pytest.raises(ValueError) as exc_info:
        TicketBase(**data)
    assert error_message in str(exc_info.value)
