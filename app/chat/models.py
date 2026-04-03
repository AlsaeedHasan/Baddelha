from datetime import datetime, timezone

from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    swap_id = Column(Integer, ForeignKey("swaps.id"), unique=True, nullable=False)

    # Cascade deletes messages when a chat room is deleted
    messages = relationship(
        "Message", back_populates="room", cascade="all, delete-orphan"
    )
    swap = relationship("Swap", backref="chat_room")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    sender_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", backref="messages")
