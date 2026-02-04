from decimal import Decimal
from uuid import UUID

from pydantic import field_validator

from src.base.schemas import BaseSchema
from src.organizations.utils import check_latitude, check_longitude


class BuildingOutSchema(BaseSchema):
    """Building out schema"""
    uuid: UUID
    address: str
    latitude: Decimal
    longitude: Decimal


class BuildingListItemSchema(BaseSchema):
    """Building list item schema"""
    uuid: UUID
    address: str


class BuildingInSchema(BaseSchema):
    """Building in schema"""
    latitude: Decimal
    longitude: Decimal

    @field_validator('latitude')
    def check_latitude(cls, latitude: Decimal | None) -> Decimal | None:
        """Check latitude."""
        return check_latitude(latitude)

    @field_validator('longitude')
    def check_longitude(cls, longitude: Decimal | None) -> Decimal | None:
        """Check longitude."""
        return check_longitude(longitude)


class BuildingCreateSchema(BuildingInSchema):
    """Building create schema"""
    address: str


class BuildingUpdateSchema(BuildingInSchema):
    """Building update schema"""
    latitude: Decimal = None
    longitude: Decimal = None
    address: str = None
