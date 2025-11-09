from decimal import Decimal
from math import cos, radians
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import Select, and_, ScalarSelect, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src import ActivityDB, OrganizationActivityDB, OrganizationDB, BuildingDB
from src.organizations.enums import ShapeEnum
from src.organizations.schemas import ActivityTreeItemSchema
from src.organizations.utils import check_latitude, check_longitude, haversine


async def get_activities_tree(activities: list[ActivityDB]) -> list[ActivityTreeItemSchema]:
    """Get activities tree from list for activities"""

    def convert(value_):
        if not isinstance(value, dict):
            return value
        new_value = {k_: v_ for k_, v_ in value_.items()}
        if 'activities' in new_value:
            activities_list = []
            for v_ in new_value['activities'].values():
                converted_value = convert(v_)
                activities_list.append(converted_value)
            new_value['activities'] = activities_list
        return new_value

    result = {}
    for activity in activities:
        data = {}
        counter = 2
        if activity.parent:
            counter = 0
            if not activity.parent.parent:
                counter = 1
        while activity.parent:
            data[counter] = activity
            counter += 1
            activity = activity.parent
        else:
            data[counter] = activity
        for k, v in sorted(data.items(), key=lambda x: x[0], reverse=True):
            schema = ActivityTreeItemSchema.model_validate(v, from_attributes=True)
            schema_data = schema.model_dump(exclude={'activities'})
            if k == 2:
                if v.uuid not in result:
                    result[v.uuid] = {**schema_data, 'activities': {}}
            elif k == 1:
                if v.uuid not in result[v.parent_uuid]['activities']:
                    result[v.parent_uuid]['activities'][v.uuid] = {**schema_data, 'activities': {}}
            elif k == 0:
                result[v.parent.parent_uuid]['activities'][v.parent_uuid]['activities'][v.uuid] = {**schema_data}
    temp_result = {}
    for key, value in result.items():
        temp_result[key] = convert(value)
    final_result = []
    for value in temp_result.values():
        final_result.append(ActivityTreeItemSchema(**value))
    return final_result


async def get_all_child_activities(activity_uuids: list[UUID] | ScalarSelect) -> ScalarSelect:
    """Get all child activities"""
    queries = []
    for i in range(3):
        field = ActivityDB.uuid if i == 0 else ActivityDB.parent_uuid
        subquery = select(ActivityDB.uuid).where(field.in_(activity_uuids)).subquery()
        activity_uuids = select(subquery).scalar_subquery()
        queries.append(subquery)
    activities = union_all(*[select(q) for q in queries]).scalar_subquery()
    return activities


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
        lat, lon = Decimal(building.latitude), Decimal(building.longitude)
        if shape == ShapeEnum.circle:
            if haversine(center_lat, center_lon, lat, lon) <= radius_km:
                result.append(building.uuid)
        elif shape == ShapeEnum.square:
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                result.append(building.uuid)
    return result


async def filter_organizations(
        session: AsyncSession, query: Select, building_uuid: UUID | None, activity_uuid: UUID | None,
        search_activity: str | None, search_name: str | None, latitude: str | None, longitude: str | None,
        radius: float | None, shape: ShapeEnum
) -> Select:
    """Filter organizations."""
    if building_uuid:
        query = query.where(OrganizationDB.building_uuid == building_uuid)
    if activity_uuid:
        subquery = (
            select(query.subquery().c.uuid)
            .join(
                OrganizationActivityDB,
                and_(
                    OrganizationDB.uuid == OrganizationActivityDB.organization_uuid,
                    OrganizationActivityDB.activity_uuid == activity_uuid
                )
            )
        ).scalar_subquery()
        query = query.where(OrganizationDB.uuid.in_(subquery))
    if search_activity is not None:
        activity_subquery = (
            select(ActivityDB.uuid).where(ActivityDB.name.ilike(f'%{search_activity}%')).scalar_subquery()
        )
        activities = await get_all_child_activities(activity_subquery)
        subquery = (
            select(query.subquery().c.uuid)
            .join(
                OrganizationActivityDB,
                and_(
                    OrganizationDB.uuid == OrganizationActivityDB.organization_uuid,
                    OrganizationActivityDB.activity_uuid.in_(activities)
                )
            )
        ).scalar_subquery()
        query = query.where(OrganizationDB.uuid.in_(subquery))
    if search_name is not None:
        query = query.where(OrganizationDB.name.ilike(f'%{search_name}%'))
    if any([latitude, longitude, radius]) and not all([latitude, longitude, radius]):
        detail = 'Fields latitude, longitude, radius should be specified together or not specified at all'
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail)
    if all([latitude, longitude, radius]):
        check_latitude(latitude)
        check_longitude(longitude)
        latitude = Decimal(latitude)
        longitude = Decimal(longitude)
        building_query = select(BuildingDB)
        res = list(await session.scalars(building_query))
        filtered_buildings = filter_buildings_in_radius(latitude, longitude, radius, shape, res)
        query = query.where(OrganizationDB.building_uuid.in_(filtered_buildings))
    return query


async def filter_buildings(
        session: AsyncSession, query: Select, latitude: str | None, longitude: str | None, radius: float | None,
        shape: ShapeEnum
) -> Select:
    """Filter buildings."""
    if any([latitude, longitude, radius]) and not all([latitude, longitude, radius]):
        detail = 'Fields latitude, longitude, radius should be specified together or not specified at all'
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail)
    if all([latitude, longitude, radius]):
        check_latitude(latitude)
        check_longitude(longitude)
        latitude = Decimal(latitude)
        longitude = Decimal(longitude)
        building_query = select(BuildingDB)
        res = list(await session.scalars(building_query))
        filtered_buildings = filter_buildings_in_radius(latitude, longitude, radius, shape, res)
        query = query.where(BuildingDB.uuid.in_(filtered_buildings))
    return query
