from uuid import UUID

from fastapi import Depends
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.base.paginators import PaginatePage
from src.base.routers import FastAPIRouter
from src.base.schemas import responses, UUIDSchema
from src.config.session import get_async_session
from src.organizations.schemas import OrganizationCreateSchema, OrganizationListItemSchema, OrganizationDetailSchema, \
    OrganizationUpdateSchema, BuildingOutSchema, BuildingCreateSchema, BuildingListItemSchema, BuildingUpdateSchema
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
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
        exclude=[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    ),
    status_code=status.HTTP_201_CREATED,
    description='Organization create',
)
async def organization_create(
        body: OrganizationCreateSchema,
        session: AsyncSession = Depends(get_async_session),
) -> UUIDSchema:
    """Organization create."""
    result = await OrganizationSession(session).organization_create(body)
    return result


@organization_router.get(
    organization_url.organization_list,
    response_model=PaginatePage[OrganizationListItemSchema],
    responses=responses(
        PaginatePage[OrganizationListItemSchema],
        exclude=[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    ),
    description='Organization list',
)
async def organization_list(
        session: AsyncSession = Depends(get_async_session),
) -> PaginatePage[OrganizationListItemSchema]:
    """Organization list."""
    organizations = await OrganizationSession(session).organization_list()
    result = await paginate(session, organizations)
    return result


@organization_router.get(
    organization_url.organization_detail,
    response_model=OrganizationDetailSchema,
    responses=responses(
        OrganizationDetailSchema,
        exclude=[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    ),
    description='Organization detail',
)
async def organization_detail(
        organization_uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
) -> OrganizationDetailSchema:
    """Organization detail."""
    result = await OrganizationSession(session).organization_detail(organization_uuid)
    return result


@organization_router.post(
    organization_url.organization_update,
    response_model=UUIDSchema,
    responses=responses(
        UUIDSchema,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
        exclude=[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    ),
    description='Organization update',
)
async def organization_update(
        organization_uuid: UUID,
        body: OrganizationUpdateSchema,
        session: AsyncSession = Depends(get_async_session),
) -> UUIDSchema:
    """Organization update."""
    result = await OrganizationSession(session).organization_update(body, organization_uuid)
    return result


@organization_router.delete(
    organization_url.organization_delete,
    responses=responses(
        response_status=status.HTTP_204_NO_CONTENT,
        statuses=[status.HTTP_404_NOT_FOUND],
        exclude=[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    description='Organization delete',
)
async def organization_delete(
        organization_uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
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
        statuses=[status.HTTP_409_CONFLICT],
        exclude=[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    ),
    status_code=status.HTTP_201_CREATED,
    description='Building create',
)
async def building_create(
        body: BuildingCreateSchema,
        session: AsyncSession = Depends(get_async_session),
) -> BuildingOutSchema:
    """Building create."""
    result = await OrganizationSession(session).building_create(body)
    return result


@organization_router.get(
    organization_url.building_list,
    response_model=PaginatePage[BuildingListItemSchema],
    responses=responses(
        PaginatePage[BuildingListItemSchema],
        exclude=[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    ),
    description='Building list',
)
async def building_list(
        session: AsyncSession = Depends(get_async_session),
) -> PaginatePage[BuildingListItemSchema]:
    """Building list."""
    buildings = await OrganizationSession(session).building_list()
    result = await paginate(session, buildings)
    return result


@organization_router.get(
    organization_url.building_detail,
    response_model=BuildingOutSchema,
    responses=responses(
        BuildingOutSchema,
        exclude=[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    ),
    description='Building detail',
)
async def building_detail(
        building_uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
) -> BuildingOutSchema:
    """Building detail."""
    result = await OrganizationSession(session).building_detail(building_uuid)
    return result


@organization_router.post(
    organization_url.building_update,
    response_model=BuildingOutSchema,
    responses=responses(
        BuildingOutSchema,
        statuses=[status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT],
        exclude=[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    ),
    description='Building update',
)
async def building_update(
        building_uuid: UUID,
        body: BuildingUpdateSchema,
        session: AsyncSession = Depends(get_async_session),
) -> BuildingOutSchema:
    """Building update."""
    result = await OrganizationSession(session).building_update(body, building_uuid)
    return result


@organization_router.delete(
    organization_url.building_delete,
    responses=responses(
        response_status=status.HTTP_204_NO_CONTENT,
        statuses=[status.HTTP_404_NOT_FOUND],
        exclude=[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    description='Building delete',
)
async def building_delete(
        building_uuid: UUID,
        session: AsyncSession = Depends(get_async_session),
) -> None:
    """Building delete."""
    await OrganizationSession(session).building_delete(building_uuid)
