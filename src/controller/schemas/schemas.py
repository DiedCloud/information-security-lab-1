import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

from src.controller.schemas.base import DatetimeBaseModel


# region publications crud
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
# endregion


# region user, auth
class UserRead(BaseModel):
    id: int
    login: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=6)
# endregion


# region scheduled cleaner
class StartParams(BaseModel):
    interval_seconds: Optional[int] = Field(default=3600, description="Интервал в секундах между удалениями")
    cron: Optional[str] = Field(
        default=None, description="Альтернативно можно передать crontab выражение", examples=["0 * * * *"]
    )

    @model_validator(mode="after")
    def valid_interval_seconds(self):
        if "interval_seconds" in self.model_fields_set and self.interval_seconds and self.interval_seconds < 0:
            raise ValueError("interval_seconds should be > 0")
        return self

    @model_validator(mode="after")
    def valid_cron(self):
        if "cron" in self.model_fields_set and self.cron and not re.match(r"^(\S+ ){4}\S+$", self.cron):
            raise ValueError(f"Wrong cron statement: {self.cron}")
        return self


class CleanerStatus(DatetimeBaseModel):
    message: str
    scheduler_running: bool
    job_scheduled: bool
    next_run_time: Optional[datetime] = None
    trigger: Optional[str] = None
    job_id: Optional[str] = None
# endregion
