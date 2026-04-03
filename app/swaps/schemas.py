from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SwapCreate(BaseModel):
    offered_item_id: int
    requested_item_id: int


class SwapOut(BaseModel):
    id: int
    requester_id: UUID
    responder_id: UUID
    offered_item_id: int
    requested_item_id: int
    status: str
    model_config = ConfigDict(from_attributes=True)
