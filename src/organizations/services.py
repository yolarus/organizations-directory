from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src import ActivityDB, OrganizationActivityDB, OrganizationDB, BuildingDB
from src.activities.services import get_all_child_activities
from src.buildings.enums import ShapeEnum
from src.buildings.services import filter_buildings_in_radius
from src.organizations.utils import check_latitude, check_longitude


async def filter_organizations(
        session: AsyncSession, query: Select, building_uuid: UUID | None, activity_uuid: UUID | None,
        search_activity: str | None, search_name: str | None, latitude: Decimal | None, longitude: Decimal | None,
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
        building_query = select(BuildingDB)
        res = list(await session.scalars(building_query))
        filtered_buildings = filter_buildings_in_radius(latitude, longitude, radius, shape, res)
        query = query.where(OrganizationDB.building_uuid.in_(filtered_buildings))
    return query
