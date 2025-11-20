from typing import ClassVar

from sqlalchemy import JSON, MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models"""

    __abstract__ = True

    CODE_NAME = "ENTITY"
    READABLE_NAME = "Entity"

    metadata = MetaData(
        naming_convention={
            "ix": "%(column_0_label)s_idx",
            "uq": "%(table_name)s_%(column_0_name)s_key",
            "ck": "%(table_name)s_%(constraint_name)s_check",
            "fk": "%(table_name)s_%(column_0_name)s_fkey",
            "pk": "%(table_name)s_pkey",
        }
    )

    type_annotation_map: ClassVar[dict] = {
        dict: JSON,
        list[str]: JSON,
    }
