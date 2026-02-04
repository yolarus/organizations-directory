from decimal import Decimal
from math import cos, radians
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src import BuildingDB
from src.buildings.enums import ShapeEnum
from src.organizations.utils import haversine, check_latitude, check_longitude


def filter_buildings_in_radius(
        center_lat: Decimal, center_lon: Decimal, radius_km: float, shape: ShapeEnum, buildings: list[BuildingDB]
) -> list[UUID]:
    """Filter buildings in radius."""
    max_d_lat = Decimal(radius_km / 111.0)
    max_d_lon = Decimal(radius_km / (111.0 * abs(cos(radians(center_lat)))))
    min_lat = center_lat - max_d_lat
    max_lat = center_lat + max_d_lat
    min_lon = center_lon - max_d_lon
    max_lon = center_lon + max_d_lon
    result = []
    for building in buildings:
        lat, lon = building.latitude, building.longitude
        if shape == ShapeEnum.circle:
            if haversine(center_lat, center_lon, lat, lon) <= radius_km:
                result.append(building.uuid)
        elif shape == ShapeEnum.square:
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                result.append(building.uuid)
    return result


async def filter_buildings(
        session: AsyncSession,
        query: Select,
        latitude: Decimal | None,
        longitude: Decimal | None,
        radius: float | None,
        shape: ShapeEnum
) -> Select:
    """Filter buildings."""
    if any([latitude, longitude, radius]) and not all([latitude, longitude, radius]):
        detail = 'Fields latitude, longitude, radius should be specified together or not specified at all'
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail)
    if all([latitude, longitude, radius]):
        check_latitude(latitude)
        check_longitude(longitude)
        building_query = select(BuildingDB)
        res = list(await session.scalars(building_query))
        filtered_buildings = filter_buildings_in_radius(latitude, longitude, radius, shape, res)
        query = query.where(BuildingDB.uuid.in_(filtered_buildings))
    return query
