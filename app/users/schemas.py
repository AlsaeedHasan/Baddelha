import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserOut(UserBase):
    id: uuid.UUID
    is_active: bool
    is_admin: bool
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class ReviewCreate(BaseModel):
    reviewed_id: uuid.UUID
    rating: float
    comment: Optional[str] = None


class ReviewOut(ReviewCreate):
    id: int
    reviewer_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
