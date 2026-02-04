from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src import OrganizationDB, PhoneDB, OrganizationActivityDB, ActivityDB


async def create_organization(
        session: AsyncSession,
        name: str,
        building_uuid: UUID,
        phones: list[str],
        activity_uuids: list[UUID]
) -> OrganizationDB:
    """Create organization."""
    async with session.begin():
        data = {
            'name': name,
            'building_uuid': building_uuid,
        }
        organization = OrganizationDB(**data)
        session.add(organization)
        await session.flush()
        inserted_data = []
        for phone in phones:
            inserted_data.append(
                PhoneDB(phone=phone, organization_uuid=organization.uuid)
            )
        for activity_uuid in activity_uuids:
            inserted_data.append(
                OrganizationActivityDB(activity_uuid=activity_uuid, organization_uuid=organization.uuid)
            )
        session.add_all(inserted_data)
        await session.flush()
        query = (
            select(OrganizationDB)
            .where(OrganizationDB.uuid == organization.uuid)
            .options(
                joinedload(OrganizationDB.building), selectinload(OrganizationDB.phones),
                selectinload(OrganizationDB.activities).selectinload(ActivityDB.parent, recursion_depth=2),
            )
        )
        organization = await session.scalar(query)
    return organization


@pytest.fixture(scope='function')
async def organization(get_override_async_session, activity111, building):
    """Organization db fixture."""
    organization = await create_organization(
        get_override_async_session, 'Organization 1', building.uuid, ['88005553535'], [activity111.uuid]
    )
    return organization


@pytest.fixture(scope='function')
async def organization2(get_override_async_session, activity112, building2):
    """Organization 2 db fixture."""
    organization = await create_organization(
        get_override_async_session, 'Organization 2', building2.uuid, ['88005553536'], [activity112.uuid]
    )
    return organization


@pytest.fixture(scope='function')
async def organization3(get_override_async_session, activity2, building3):
    """Organization 2 db fixture."""
    organization = await create_organization(
        get_override_async_session, 'Organization 3', building3.uuid, ['88005553537'], [activity2.uuid]
    )
    return organization
