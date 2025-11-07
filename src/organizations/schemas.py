import re
from uuid import UUID

from fastapi import HTTPException
from pydantic import field_validator
from starlette import status

from src.base.schemas import BaseSchema, UUIDNameSchema


class PhoneSchema(BaseSchema):
    """Phone create response schema."""
    uuid: UUID
    phone: str


class OrganizationCreateRequestSchema(BaseSchema):
    """Organization create request schema."""
    name: str
    building_uuid: UUID
    phones: list[str]
    activity_uuids: list[UUID]

    @field_validator('phones')
    def check_animal_uuid(cls, phones: list[str]) -> list[str]:
        """Check data type."""
        pattern = re.compile(r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$')
        for index, phone in enumerate(phones):
            if not pattern.match(phone):
                error = [{'field': 'phones', 'message': f'Phone {phone} not valid'}]
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, error)
            phones[index] = ''.join([a for a in phone if a.isdigit()])
        return list(set(phones))


class OrganizationDetailSchema(BaseSchema):
    """Organization create response schema."""
    uuid: UUID
    name: str
    building: UUIDNameSchema
    activities_tree: list[UUIDNameSchema]
    phones: list[PhoneSchema]
