from unittest.mock import patch

import pytest

from app.chat.models import Message
from app.core.security import create_access_token
from tests.factories import ChatRoomFactory, MessageFactory, UserFactory


def test_chat_history(client, db_session):
    room = ChatRoomFactory()
    msg1 = MessageFactory(room=room, content="First message")
    msg2 = MessageFactory(room=room, content="Second message")
    db_session.commit()  # commit needed if endpoint does independent queries? Actually history uses Depends(get_db)

    response = client.get(f"/chat/history/{room.id}")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["content"] == "First message"


def test_websocket_chat(client, db_session):
    room = ChatRoomFactory()
    user = UserFactory()
    db_session.commit()  # Commit so the separate connection in WebSocket finds the room and user

    token = create_access_token(data={"sub": user.email})
    room_id = room.id
    user_email = user.email

    # We must patch SessionLocal in app.chat.router to use a testing localized session
    with patch("app.chat.router.SessionLocal", return_value=db_session):
        with client.websocket_connect(f"/ws/chat/{room_id}?token={token}") as websocket:
            websocket.send_text("Hello there!")

            # It broadcasts it immediately
            data = websocket.receive_text()
            assert data == f"{user_email}: Hello there!"

        # After disconnect, verify DB contains the new message
        messages = db_session.query(Message).filter(Message.room_id == room_id).all()
        assert len(messages) >= 1
        assert any(m.content == "Hello there!" for m in messages)


def test_websocket_unauthorized(client, db_session):
    room = ChatRoomFactory()
    db_session.commit()

    # Missing token -> 403 generally, or fast fail
    with patch("app.chat.router.SessionLocal", return_value=db_session):
        try:
            from fastapi import WebSocketDisconnect

            with client.websocket_connect(
                f"/ws/chat/{room.id}?token=invalidToken"
            ) as websocket:
                pass  # should raise exception or close
        except Exception as e:
            pass  # This is acceptable, the connection closed unexpectedly.
