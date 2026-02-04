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
from src.base.schemas import responses
from src.base.services import get_filters
from src.buildings.enums import ShapeEnum
from src.buildings.schemas import BuildingOutSchema, BuildingCreateSchema, BuildingListItemSchema, BuildingUpdateSchema
from src.buildings.sessions import BuildingSession
from src.buildings.urls import building_url
from src.config.session import get_async_session

building_router = FastAPIRouter()


@building_router.post(
    building_url.building_create,
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
    result = await BuildingSession(session).building_create(body)
    return result


@building_router.get(
    building_url.building_list,
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
    buildings = await BuildingSession(session).building_list(**filters)
    result = await apaginate(session, buildings)
    return result


@building_router.get(
    building_url.building_detail,
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
    result = await BuildingSession(session).building_detail(building_uuid)
    return result


@building_router.patch(
    building_url.building_update,
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
    result = await BuildingSession(session).building_update(body, building_uuid)
    return result


@building_router.delete(
    building_url.building_delete,
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
    await BuildingSession(session).building_delete(building_uuid)
