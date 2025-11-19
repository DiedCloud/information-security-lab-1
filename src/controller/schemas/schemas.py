from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from src.controller.schemas.base import DatetimeBaseModel


class PublicationCreate(BaseModel):
    title: str = Field(..., max_length=255)
    content: str


class PublicationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None


class PublicationOut(DatetimeBaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserRead(BaseModel):
    id: int
    login: str



