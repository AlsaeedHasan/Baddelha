from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MessageOut(BaseModel):
    id: int
    room_id: int
    sender_id: UUID
    content: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


class ChatRoomOut(BaseModel):
    id: int
    swap_id: int
    model_config = ConfigDict(from_attributes=True)
