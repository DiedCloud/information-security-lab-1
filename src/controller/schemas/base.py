from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer


class DatetimeBaseModel(BaseModel):
    model_config = ConfigDict()

    @field_serializer("*", when_used="json")
    def serialize_all(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value
