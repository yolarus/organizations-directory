from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.auth import BaseAuth
from src.base.paginators import PaginatePage
from src.base.routers import FastAPIRouter
from src.base.schemas import responses, UUIDSchema
from src.base.services import get_filters
from src.config.session import get_async_session
from src.organizations.enums import ShapeEnum
from src.organizations.schemas import OrganizationCreateSchema, OrganizationListItemSchema, OrganizationDetailSchema, \
    OrganizationUpdateSchema, BuildingOutSchema, BuildingCreateSchema, BuildingListItemSchema, BuildingUpdateSchema, \
    ActivityCreateSchema, ActivityOutSchema, ActivityListItemSchema, ActivityDetailSchema, ActivityUpdateSchema
from src.organizations.sessions import OrganizationSession
from src.organizations.urls import organization_url

organization_router = FastAPIRouter()


# Organization
@organization_router.post(
    organization_url.organization_create,
    response_model=UUIDSchema,
    responses=responses(
        UUIDSchema,
        status.HTTP_201_CREATED,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]
    ),
    status_code=status.HTTP_201_CREATED,
    description='Organization create',
)
async def organization_create(
        body: OrganizationCreateSchema,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> UUIDSchema:
    """Organization create."""
    result = await OrganizationSession(session).organization_create(body)
    return result


@organization_router.get(
    organization_url.organization_list,
    response_model=PaginatePage[OrganizationListItemSchema],
    responses=responses(
        PaginatePage[OrganizationListItemSchema],
        statuses=[status.HTTP_400_BAD_REQUEST]
    ),
    description='Organization list',
)
async def organization_list(
        building_uuid: Annotated[UUID, Query(description='Filter by building_uuid')] = None,
        activity_uuid: Annotated[UUID, Query(description='Filter by activity_uuid')] = None,
        latitude: Annotated[
            Decimal, Query(description='Latitude of the point from which the calculation will be made')
        ] = None,
        longitude: Annotated[
            Decimal, Query(description='Longitude of the point from which the calculation will be made')
        ] = None,
        radius: Annotated[
            float, Query(description='Radius in km along which the calculation will be made')
        ] = None,
        shape: Annotated[
            ShapeEnum, Query(description='Shape of the zone for which the calculation will be made')
        ] = ShapeEnum.circle,
        search_activity: Annotated[str, Query(description='Search by activity name')] = None,
        search_name: Annotated[str, Query(description='Search by organization name')] = None,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> PaginatePage[OrganizationListItemSchema]:
    """Organization list."""
    filters = get_filters(
        building_uuid=building_uuid, activity_uuid=activity_uuid, search_activity=search_activity,
        search_name=search_name, latitude=latitude, longitude=longitude, radius=radius, shape=shape
    )
    organizations = await OrganizationSession(session).organization_list(**filters)
    result = await apaginate(session, organizations)
    return result


@organization_router.get(
    organization_url.organization_detail,
    response_model=OrganizationDetailSchema,
    responses=responses(
        OrganizationDetailSchema,
        statuses=[status.HTTP_404_NOT_FOUND]
    ),
    description='Organization detail',
)
async def organization_detail(
        organization_uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> OrganizationDetailSchema:
    """Organization detail."""
    result = await OrganizationSession(session).organization_detail(organization_uuid)
    return result


@organization_router.patch(
    organization_url.organization_update,
    response_model=UUIDSchema,
    responses=responses(
        UUIDSchema,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]
    ),
    description='Organization update',
)
async def organization_update(
        organization_uuid: UUID,
        body: OrganizationUpdateSchema,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> UUIDSchema:
    """Organization update."""
    result = await OrganizationSession(session).organization_update(body, organization_uuid)
    return result


@organization_router.delete(
    organization_url.organization_delete,
    responses=responses(
        response_status=status.HTTP_204_NO_CONTENT,
        statuses=[status.HTTP_404_NOT_FOUND]
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    description='Organization delete',
)
async def organization_delete(
        organization_uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> None:
    """Organization delete."""
    await OrganizationSession(session).organization_delete(organization_uuid)


# Building
@organization_router.post(
    organization_url.building_create,
    response_model=BuildingOutSchema,
    responses=responses(
        BuildingOutSchema,
        status.HTTP_201_CREATED,
        statuses=[status.HTTP_409_CONFLICT]
    ),
    status_code=status.HTTP_201_CREATED,
    description='Building create',
)
async def building_create(
        body: BuildingCreateSchema,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> BuildingOutSchema:
    """Building create."""
    result = await OrganizationSession(session).building_create(body)
    return result


@organization_router.get(
    organization_url.building_list,
    response_model=PaginatePage[BuildingListItemSchema],
    responses=responses(
        PaginatePage[BuildingListItemSchema],
        statuses=[status.HTTP_400_BAD_REQUEST]
    ),
    description='Building list',
)
async def building_list(
        latitude: Annotated[
            Decimal, Query(description='Latitude of the point from which the calculation will be made')
        ] = None,
        longitude: Annotated[
            Decimal, Query(description='Longitude of the point from which the calculation will be made')
        ] = None,
        radius: Annotated[
            float, Query(description='Radius in km along which the calculation will be made')
        ] = None,
        shape: Annotated[
            ShapeEnum, Query(description='Shape of the zone for which the calculation will be made')
        ] = ShapeEnum.circle,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> PaginatePage[BuildingListItemSchema]:
    """Building list."""
    filters = get_filters(latitude=latitude, longitude=longitude, radius=radius, shape=shape)
    buildings = await OrganizationSession(session).building_list(**filters)
    result = await apaginate(session, buildings)
    return result


@organization_router.get(
    organization_url.building_detail,
    response_model=BuildingOutSchema,
    responses=responses(
        BuildingOutSchema,
        statuses=[status.HTTP_404_NOT_FOUND]
    ),
    description='Building detail',
)
async def building_detail(
        building_uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> BuildingOutSchema:
    """Building detail."""
    result = await OrganizationSession(session).building_detail(building_uuid)
    return result


@organization_router.patch(
    organization_url.building_update,
    response_model=BuildingOutSchema,
    responses=responses(
        BuildingOutSchema,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]
    ),
    description='Building update',
)
async def building_update(
        building_uuid: UUID,
        body: BuildingUpdateSchema,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> BuildingOutSchema:
    """Building update."""
    result = await OrganizationSession(session).building_update(body, building_uuid)
    return result


@organization_router.delete(
    organization_url.building_delete,
    responses=responses(
        response_status=status.HTTP_204_NO_CONTENT,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    description='Building delete',
)
async def building_delete(
        building_uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> None:
    """Building delete."""
    await OrganizationSession(session).building_delete(building_uuid)


# Activity
@organization_router.post(
    organization_url.activity_create,
    response_model=ActivityOutSchema,
    responses=responses(
        ActivityOutSchema,
        status.HTTP_201_CREATED,
        statuses=[status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]
    ),
    status_code=status.HTTP_201_CREATED,
    description='Activity create',
)
async def activity_create(
        body: ActivityCreateSchema,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> ActivityOutSchema:
    """Activity create."""
    result = await OrganizationSession(session).activity_create(body)
    return result


@organization_router.get(
    organization_url.activity_list,
    response_model=PaginatePage[ActivityListItemSchema],
    responses=responses(
        PaginatePage[ActivityListItemSchema],
        exclude=[status.HTTP_422_UNPROCESSABLE_CONTENT]
    ),
    description='Activity list',
)
async def activity_list(
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> PaginatePage[ActivityListItemSchema]:
    """Activity list."""
    activities = await OrganizationSession(session).activity_list()
    result = await apaginate(session, activities)
    return result


@organization_router.get(
    organization_url.activity_detail,
    response_model=ActivityDetailSchema,
    responses=responses(
        ActivityDetailSchema,
        statuses=[status.HTTP_404_NOT_FOUND]
    ),
    description='Activity detail',
)
async def activity_detail(
        activity_uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> ActivityDetailSchema:
    """Activity detail."""
    result = await OrganizationSession(session).activity_detail(activity_uuid)
    return result


@organization_router.patch(
    organization_url.activity_update,
    response_model=ActivityOutSchema,
    responses=responses(
        ActivityOutSchema,
        statuses=[status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]
    ),
    description='Activity update',
)
async def activity_update(
        activity_uuid: UUID,
        body: ActivityUpdateSchema,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> ActivityOutSchema:
    """Activity update."""
    result = await OrganizationSession(session).activity_update(body, activity_uuid)
    return result


@organization_router.delete(
    organization_url.activity_delete,
    responses=responses(
        response_status=status.HTTP_204_NO_CONTENT,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    description='Activity delete',
)
async def activity_delete(
        activity_uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
        _: AsyncSession = Depends(BaseAuth())
) -> None:
    """Activity delete."""
    await OrganizationSession(session).activity_delete(activity_uuid)
