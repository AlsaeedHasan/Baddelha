from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---- Comments ----
class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class CommentOut(CommentBase):
    id: int
    item_id: int
    author_id: UUID
    model_config = ConfigDict(from_attributes=True)


# ---- Items ----
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    estimated_price: Optional[float] = None
    image_url: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    transaction_type: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_price: Optional[float] = None
    image_url: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    transaction_type: Optional[str] = None


class ItemOut(ItemBase):
    id: int
    owner_id: UUID
    comments: List[CommentOut] = []
    model_config = ConfigDict(from_attributes=True)
