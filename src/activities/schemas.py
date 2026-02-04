from typing import Optional
from uuid import UUID

from src.base.schemas import BaseSchema


class ActivityTreeItemSchema(BaseSchema):
    """Activity tree item schema."""
    uuid: UUID
    name: str
    activities: list['ActivityTreeItemSchema'] = None


class ActivityCreateSchema(BaseSchema):
    """Activity create schema."""
    name: str
    parent_uuid: UUID | None = None


class ActivityOutSchema(BaseSchema):
    """Activity out schema."""
    uuid: UUID
    name: str
    parent: Optional['ActivityOutSchema']


class ActivityListItemSchema(BaseSchema):
    """Activity out schema."""
    uuid: UUID
    name: str
    children: list['ActivityListItemSchema']


class ActivityDetailSchema(ActivityOutSchema):
    """Activity detail schema."""
    children: list['ActivityListItemSchema']


class ActivityUpdateSchema(BaseSchema):
    """Activity update schema."""
    name: str = None
    parent_uuid: UUID | None = None
