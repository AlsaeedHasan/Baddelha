import pytest

from app.chat.models import ChatRoom
from app.swaps.models import Swap
from tests.factories import ItemFactory, SwapFactory, UserFactory


def test_create_swap_request(user_client, db_session):
    client, requester = user_client

    responder = UserFactory()
    offered_item = ItemFactory(owner=requester)
    requested_item = ItemFactory(owner=responder)
    db_session.flush()

    response = client.post(
        "/swaps/request",
        json={
            "offered_item_id": offered_item.id,
            "requested_item_id": requested_item.id,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert str(data["requester_id"]) == str(requester.id)
    assert str(data["responder_id"]) == str(responder.id)
    assert data["status"] == "Pending"


def test_accept_swap_creates_chatroom(user_client, db_session):
    client, responder = user_client
    requester = UserFactory()

    offered_item = ItemFactory(owner=requester)
    requested_item = ItemFactory(owner=responder)
    db_session.flush()

    swap = SwapFactory(
        requester=requester,
        responder=responder,
        offered_item=offered_item,
        requested_item=requested_item,
        status="Pending",
    )
    db_session.flush()

    response = client.put(f"/swaps/{swap.id}/accept")
    assert response.status_code == 200
    assert response.json()["status"] == "Accepted"

    # Verify DB side effect: Chatroom creation
    chat_room = db_session.query(ChatRoom).filter(ChatRoom.swap_id == swap.id).first()
    assert chat_room is not None


def test_reject_swap(user_client, db_session):
    client, responder = user_client
    requester = UserFactory()
    swap = SwapFactory(responder=responder, requester=requester, status="Pending")
    db_session.flush()

    response = client.put(f"/swaps/{swap.id}/reject")
    assert response.status_code == 200
    assert response.json()["status"] == "Rejected"

    chat_room = db_session.query(ChatRoom).filter(ChatRoom.swap_id == swap.id).first()
    assert chat_room is None


def test_unauthorized_accept_by_requester(user_client, db_session):
    client, requester = user_client

    responder = UserFactory()
    swap = SwapFactory(requester=requester, responder=responder, status="Pending")
    db_session.flush()

    response = client.put(f"/swaps/{swap.id}/accept")
    assert response.status_code == 404
    assert db_session.query(Swap).filter(Swap.id == swap.id).first().status == "Pending"


def test_get_my_swaps(user_client, db_session):
    client, user = user_client

    # 1 where user is requester
    SwapFactory(requester=user)
    # 1 where user is responder
    SwapFactory(responder=user)
    # 1 unrelated swap
    SwapFactory()
    db_session.flush()

    response = client.get("/swaps/my-requests")
    assert response.status_code == 200
    assert len(response.json()) == 2
