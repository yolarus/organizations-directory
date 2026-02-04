from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint, Numeric
from sqlalchemy.orm import Mapped, relationship

from src.base.models import BaseDBModel, mc

if TYPE_CHECKING:
    from src import OrganizationDB


class BuildingDB(BaseDBModel):
    """Building database model."""
    __tablename__: str = 'buildings'
    __table_args__ = (UniqueConstraint('latitude', 'longitude', name='latitude_longitude_uc'),)

    address: Mapped[str] = mc(nullable=False, unique=True)
    latitude: Mapped[Decimal] = mc(Numeric(14, 12), nullable=False)
    longitude: Mapped[Decimal] = mc(Numeric(15, 12), nullable=False)

    organizations: Mapped[list['OrganizationDB']] = relationship(back_populates='building')
