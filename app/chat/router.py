from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.chat import schemas, sockets
from app.chat.models import ChatRoom, Message
from app.core.config import settings
from app.core.database import SessionLocal, get_db
from app.users.models import User

router = APIRouter(tags=["Chat"])


def get_user_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        user = db.query(User).filter(User.email == email).first()
        return user
    except JWTError:
        return None


@router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, token: str):
    db: Session = SessionLocal()
    user = get_user_from_token(token, db)

    if not user:
        await websocket.close(code=1008)
        db.close()
        return

    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        await websocket.close(code=1008)
        db.close()
        return

    await sockets.manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()

            # Save message to database
            new_message = Message(room_id=room_id, sender_id=user.id, content=data)
            db.add(new_message)
            db.commit()

            # Broadcast the message
            await sockets.manager.broadcast(f"{user.email}: {data}", room_id)
    except WebSocketDisconnect:
        sockets.manager.disconnect(websocket, room_id)
        await sockets.manager.broadcast(f"{user.email} left the chat", room_id)
    finally:
        db.close()


@router.get("/chat/history/{room_id}", response_model=List[schemas.MessageOut])
def get_chat_history(room_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(Message)
        .filter(Message.room_id == room_id)
        .order_by(Message.timestamp.asc())
        .all()
    )
    return messages
