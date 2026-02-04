from typing import TYPE_CHECKING

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, relationship

from src.base.models import BaseDBModel, mc, FK

if TYPE_CHECKING:
    from src import OrganizationDB


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
    activity_uuid: Mapped[UUID] = mc(FK('activities.uuid', ondelete='RESTRICT'), primary_key=True)
