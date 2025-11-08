import re
from uuid import UUID

from fastapi import HTTPException
from pydantic import field_validator
from starlette import status

from src.base.schemas import BaseSchema


class PhoneSchema(BaseSchema):
    """Phone create response schema."""
    uuid: UUID
    phone: str


class BuildingDetailSchema(BaseSchema):
    """Building detail schema"""
    uuid: UUID
    address: str
    latitude: str
    longitude: str


# Organization
class OrganizationInSchema(BaseSchema):
    """Organization create request schema."""
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


class ActivityTreeItemSchema(BaseSchema):
    """Activity tree item schema."""
    uuid: UUID
    name: str
    activities: list['ActivityTreeItemSchema'] = None


class OrganizationDetailSchema(BaseSchema):
    """Organization detail schema."""
    uuid: UUID
    name: str
    building: BuildingDetailSchema
    activities_tree: list[ActivityTreeItemSchema] = list()
    phones: list[PhoneSchema]


class OrganizationUpdateSchema(OrganizationInSchema):
    """Organization update schema."""
    name: str = None
    building_uuid: UUID = None
    phones: list[str] = None
    activity_uuids: list[UUID] = None
