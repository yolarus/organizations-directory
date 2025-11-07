from datetime import datetime


import uuid
from uuid import UUID
from typing import Any

import sqlalchemy
from sqlalchemy import ForeignKey, func, String, ARRAY, TIMESTAMP, BIGINT, JSON, MetaData
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

FK = ForeignKey
mc = mapped_column


class BaseDBModel(DeclarativeBase):
    """Base PostgresQL database model."""
    __abstract__ = True
    __allow_unmapped__ = True

    type_annotation_map = {
        UUID: sqlalchemy.UUID(),
        int: BIGINT,
        datetime: TIMESTAMP(timezone=True),
        str: String(),
        dict[str, Any]: JSON,
        list[UUID]: ARRAY(sqlalchemy.UUID()),
        list[str]: ARRAY(String()),
    }

    uuid: Mapped[UUID] = mc(primary_key=True, default=uuid.uuid4)
    create_date: Mapped[datetime] = mc(server_default=func.now())
    update_date: Mapped[datetime] = mc(server_default=func.now(), onupdate=func.now())


metadata = MetaData()
