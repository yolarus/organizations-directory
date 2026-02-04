from typing import TYPE_CHECKING

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, relationship

from src.base.models import BaseDBModel, mc, FK

if TYPE_CHECKING:
    from src import ActivityDB, BuildingDB


class OrganizationDB(BaseDBModel):
    """Organization database model."""
    __tablename__: str = 'organizations'

    name: Mapped[str] = mc(nullable=False, unique=True)
    building_uuid: Mapped[UUID] = mc(FK('buildings.uuid', ondelete='RESTRICT'), nullable=False, unique=False)

    building: Mapped['BuildingDB'] = relationship('BuildingDB', back_populates='organizations')
    phones: Mapped[list['PhoneDB']] = relationship(back_populates='organization')

    activities: Mapped[list['ActivityDB']] = relationship(
        secondary='organizations_activities',
        primaryjoin='OrganizationDB.uuid==OrganizationActivityDB.organization_uuid',
        secondaryjoin='ActivityDB.uuid==OrganizationActivityDB.activity_uuid',
        back_populates='organizations'
    )


class PhoneDB(BaseDBModel):
    """Phone database model."""
    __tablename__: str = 'phones'

    organization_uuid: Mapped[UUID] = mc(FK('organizations.uuid', ondelete='CASCADE'), nullable=False, unique=False)
    phone: Mapped[str] = mc(nullable=False, unique=True)

    organization: Mapped['OrganizationDB'] = relationship('OrganizationDB', back_populates='phones')
