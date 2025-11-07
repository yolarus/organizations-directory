from sqlalchemy import UUID, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from src.base.models import BaseDBModel, mc, FK


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


class BuildingDB(BaseDBModel):
    """Phone database model."""
    __tablename__: str = 'buildings'
    __table_args__ = (UniqueConstraint('latitude', 'longitude', name='latitude_longitude_uc'),)

    address: Mapped[str] = mc(nullable=False, unique=True)
    latitude: Mapped[str] = mc(nullable=False)
    longitude: Mapped[str] = mc(nullable=False)

    organizations: Mapped[list['OrganizationDB']] = relationship(back_populates='building')


class ActivityDB(BaseDBModel):
    """Activity database model."""
    __tablename__: str = 'activities'

    name: Mapped[str] = mc(nullable=False, unique=True)
    parent_uuid: Mapped[UUID] = mc(FK('activities.uuid', ondelete='CASCADE'), nullable=True, unique=False)

    parent: Mapped['ActivityDB'] = relationship(foreign_keys=[parent_uuid], remote_side='ActivityDB.uuid')
    children: Mapped[list['ActivityDB']] = relationship(back_populates='parent')
    organizations: Mapped[list['OrganizationDB']] = relationship(
        secondary='organizations_activities',
        back_populates='activities'
    )


class OrganizationActivityDB(BaseDBModel):
    """Organization activity database model."""
    __tablename__: str = 'organizations_activities'

    uuid = None
    organization_uuid: Mapped[UUID] = mc(FK('organizations.uuid', ondelete='CASCADE'), primary_key=True)
    activity_uuid: Mapped[UUID] = mc(FK('activities.uuid', ondelete='CASCADE'), primary_key=True)
