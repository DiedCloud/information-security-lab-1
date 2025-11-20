from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field


class DatetimeBaseModel(BaseModel):
    class Config:
        json_encoders: ClassVar[dict] = {datetime: lambda v: v.strftime("%d.%m.%Y %H:%M:%S")}
