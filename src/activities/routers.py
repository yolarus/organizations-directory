from uuid import UUID

from fastapi import Depends
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.activities.schemas import ActivityCreateSchema, ActivityOutSchema, ActivityListItemSchema, \
    ActivityDetailSchema, ActivityUpdateSchema
from src.activities.sessions import ActivitySession
from src.activities.urls import activity_url
from src.auth.auth import BaseAuth
from src.base.paginators import PaginatePage
from src.base.routers import FastAPIRouter
from src.base.schemas import responses
from src.config.session import get_async_session

activity_router = FastAPIRouter()


@activity_router.post(
    activity_url.activity_create,
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
    result = await ActivitySession(session).activity_create(body)
    return result


@activity_router.get(
    activity_url.activity_list,
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
    activities = await ActivitySession(session).activity_list()
    result = await apaginate(session, activities)
    return result


@activity_router.get(
    activity_url.activity_detail,
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
    result = await ActivitySession(session).activity_detail(activity_uuid)
    return result


@activity_router.patch(
    activity_url.activity_update,
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
    result = await ActivitySession(session).activity_update(body, activity_uuid)
    return result


@activity_router.delete(
    activity_url.activity_delete,
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
    await ActivitySession(session).activity_delete(activity_uuid)
