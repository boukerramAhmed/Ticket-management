import pytest
from app.schema.ticket_schema import TicketCreatePublic, TicketResponse, TicketsList,TicketStatusUpdate,TicketUpdate
from app.models.tickets import TicketStatus
from pydantic import ValidationError


# create ticket tests
@pytest.mark.parametrize(
    "ticket,http_code_return",
    [
        (
            TicketCreatePublic(
                title="Développer une nouvelle fonctionnlité",
                description="description de la nouvelle fonctionnalité pour consulter les tickets",
            ),
            201,
        )
    ],
)
@pytest.mark.asyncio
async def test_create_ticket(client, ticket, http_code_return):
    response = await client.post("/tickets/", json=ticket.model_dump())
    assert response.status_code == http_code_return
    response: TicketResponse = TicketResponse(**response.json())


@pytest.mark.parametrize(
    "ticket,http_code_return",
    [
        (
            TicketCreatePublic(
                title="Corriger bug connexion", description="Description du bug"
            ),
            409,
        ),
        (
            TicketCreatePublic(
                title="Optimiser base de données", description="Description du bug"
            ),
            409,
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_existing_ticket(
    load_test_tickets, client, ticket, http_code_return
):
    response = await client.post("/tickets/", json=ticket.model_dump())
    assert response.status_code == http_code_return


@pytest.mark.parametrize(
    "ticket,http_code_return",
    [
        (
            {
                "title": "Corriger bug connexion 1",
                "description": "Description du bug 1 ",
            },
            201,
        ),
        (
            {
                "title": "Corriger ### bug connexion",
                "description": "Description du bug",
            },
            422,
        ),
        (
            {
                "title": "Corriger  bug connexion 2",
                "description": "Description du bug ;",
            },
            422,
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_ticket_with_prohibited_caractere(
    load_test_tickets, client, ticket, http_code_return
):
    response = await client.post("/tickets/", json=ticket)
    assert response.status_code == http_code_return


# get all tickets test
@pytest.mark.asyncio
async def test_get_all_tickets(client, load_test_tickets):
    response = await client.get("/tickets/")
    assert response.status_code == 200
    ticket_list: TicketsList = TicketsList(**response.json())
    assert ticket_list.total == len(load_test_tickets)
    assert ticket_list.limit == 100
    assert ticket_list.offset == 0


@pytest.mark.parametrize(
    "ticket_id,http_code_return",
    [
        (
            "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c01",
            200,
        ),
        (
            "4a4b4c4d-5e6f-7a8b-9c0f-1e2f3a4b5c01",
            404,
        ),
        (
            "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c20",
            200,
        ),
        (
            "1a2b3c4d-5e6f-4a4b-4c4d-1e2f3a4b5c20",
            404,
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_ticket_by_id(load_test_tickets, client, ticket_id, http_code_return):
    response = await client.get(f"/tickets/{ticket_id}")
    assert response.status_code == http_code_return


# update ticket tests
@pytest.mark.parametrize(
    "old_ticket,new_ticket,create_ticket,uuid,http_code_return",
    [
        (
            TicketCreatePublic(
                title="Développeur le CICD", description="Description du bug"
            ),
            TicketUpdate(
                title="Corriger bug connexion-updated", description="Description du bug", status=TicketStatusUpdate.STALLED.value
            ),
            True,
            None,
            200,
        ),
        (
            None,
            TicketUpdate(
                title="Corriger bug connexion-updated", description="Description du bug", status=TicketStatusUpdate.STALLED.value
            ),
            False,
            "1a2b3c4d-5e6f-4a4b-4c4d-1e2f3a4b5c20",
            404,
        ),
    ],
)
@pytest.mark.asyncio
async def test_update_ticket_by_id(
    load_test_tickets,
    client,
    old_ticket,
    new_ticket,
    create_ticket,
    uuid,
    http_code_return,
):

    if create_ticket:
        # Create the old ticket first
        response = await client.post("/tickets/", json=old_ticket.model_dump())
        assert response.status_code == 201
        #  Update the ticket
        ticket_created: TicketResponse = TicketResponse(**response.json())
        response_update = await client.put(
            f"/tickets/{ticket_created.id}",
            json=new_ticket.model_dump(),
        )
        assert response_update.status_code == http_code_return
    if not create_ticket:
        response_update = await client.put(
            f"/tickets/{uuid}",
            json=new_ticket.model_dump(),
        )
        assert response_update.status_code == http_code_return


# close ticket tests
@pytest.mark.parametrize(
    "ticket_id,status_current,target_status,http_code_return",
    [
        (
            "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c03",  # check data in data/tickets.json
            "closed",
            "closed",
            400,
        ),
        (
            "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c01",  # check data in data/tickets.json
            "open",
            "closed",
            200,
        ),
    ],
)
@pytest.mark.asyncio
async def test_close_tiket(
    load_test_tickets,
    client,
    ticket_id,
    status_current,
    target_status,
    http_code_return,
):

    response = await client.patch(f"/tickets/{ticket_id}/close")
    assert response.status_code == http_code_return
    if http_code_return == 400:
        assert response.json()["detail"] == "Ticket is already closed"
    if http_code_return == 200:
        ticket: TicketResponse = TicketResponse(**response.json())
        assert ticket.status == target_status
