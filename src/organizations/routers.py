from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.base.schemas import responses, UUIDSchema
from src.config.session import get_async_session
from src.organizations.schemas import OrganizationCreateRequestSchema
from src.organizations.sessions import OrganizationSession
from src.organizations.urls import organization_url

organization_router = APIRouter()


@organization_router.post(
    organization_url.organization_create,
    response_model=UUIDSchema,
    responses=responses(
        UUIDSchema,
        status.HTTP_201_CREATED,
        exclude=[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    ),
    status_code=status.HTTP_201_CREATED,
    description='Organization create',
)
async def organization_create(
        body: OrganizationCreateRequestSchema,
        session: AsyncSession = Depends(get_async_session),
) -> UUIDSchema:
    """Organization create."""
    result = await OrganizationSession(session).organization_create(body)
    return result
