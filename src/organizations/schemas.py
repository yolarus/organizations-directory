import re
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from pydantic import field_validator
from starlette import status

from src.base.schemas import BaseSchema
from src.organizations.utils import check_latitude, check_longitude


class PhoneSchema(BaseSchema):
    """Phone create response schema."""
    uuid: UUID
    phone: str


# Building
class BuildingOutSchema(BaseSchema):
    """Building out schema"""
    uuid: UUID
    address: str
    latitude: str
    longitude: str


class BuildingListItemSchema(BaseSchema):
    """Building list item schema"""
    uuid: UUID
    address: str


class BuildingInSchema(BaseSchema):
    """Building in schema"""
    latitude: str
    longitude: str

    @field_validator('latitude')
    def check_latitude(cls, latitude: str | None) -> str | None:
        """Check latitude."""
        return check_latitude(latitude)

    @field_validator('longitude')
    def check_longitude(cls, longitude: str | None) -> str | None:
        """Check longitude."""
        return check_longitude(longitude)


class BuildingCreateSchema(BuildingInSchema):
    """Building create schema"""
    address: str


class BuildingUpdateSchema(BuildingInSchema):
    """Building update schema"""
    latitude: str = None
    longitude: str = None
    address: str = None


# Activity
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


# Organization
class OrganizationInSchema(BaseSchema):
    """Organization in schema."""
    phones: list[str]

    @field_validator('phones')
    def check_phones(cls, phones: list[str] | None) -> list[str]:
        """Check phone numbers."""
        pattern = re.compile(r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$')
        if phones is not None:
            for index, phone in enumerate(phones):
                if not pattern.match(phone):
                    error = [{'field': 'phones', 'message': f'Phone {phone} not valid'}]
                    raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, error)
                phones[index] = ''.join([a for a in phone if a.isdigit()])
            return list(set(phones))


class OrganizationCreateSchema(OrganizationInSchema):
    """Organization create schema."""
    name: str
    building_uuid: UUID
    activity_uuids: list[UUID]


class OrganizationListItemSchema(BaseSchema):
    """Organization list item schema."""
    uuid: UUID
    name: str
    phones: list[PhoneSchema]


class OrganizationDetailSchema(BaseSchema):
    """Organization detail schema."""
    uuid: UUID
    name: str
    building: BuildingOutSchema
    activities_tree: list[ActivityTreeItemSchema] = list()
    phones: list[PhoneSchema]


class OrganizationUpdateSchema(OrganizationInSchema):
    """Organization update schema."""
    name: str = None
    building_uuid: UUID = None
    phones: list[str] = None
    activity_uuids: list[UUID] = None
