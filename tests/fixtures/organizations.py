from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src import BuildingDB, ActivityDB, OrganizationDB, PhoneDB, OrganizationActivityDB


async def create_building(
        get_test_async_session: AsyncSession, address: str, latitude: Decimal, longitude: Decimal
) -> BuildingDB:
    """Create building."""
    data = {
        'address': address,
        'latitude': latitude,
        'longitude': longitude,
    }
    building = BuildingDB(**data)
    get_test_async_session.add(building)
    await get_test_async_session.commit()
    return building


@pytest.fixture(scope='function')
async def building(get_test_async_session):
    """Building db fixture."""
    building = await create_building(
        get_test_async_session, 'Пятницкая улица, 25А', Decimal(55.741503), Decimal(37.628861)
    )
    return building


@pytest.fixture(scope='function')
async def building2(get_test_async_session):
    """Building 2 db fixture."""
    building = await create_building(
        get_test_async_session, 'Проспект мира, 211к1', Decimal(55.843941), Decimal(37.662335)
    )
    return building


@pytest.fixture(scope='function')
async def building3(get_test_async_session):
    """Building 3 db fixture."""
    building = await create_building(
        get_test_async_session, 'Проспект мира, 38', Decimal(55.779665), Decimal(37.633636)
    )
    return building


async def create_activity(
        get_test_async_session: AsyncSession, name: str, parent_uuid: UUID | None = None
) -> ActivityDB:
    """Create activity."""
    data = {
        'name': name,
        'parent_uuid': parent_uuid,
    }
    query = (
        insert(ActivityDB)
        .values(**data)
        .returning(ActivityDB)
        .options(
            selectinload(ActivityDB.parent, recursion_depth=2),
            selectinload(ActivityDB.children, recursion_depth=2)
        )
    )
    activity = await get_test_async_session.scalar(query)
    await get_test_async_session.commit()
    return activity


@pytest.fixture(scope='function')
async def activity1(get_test_async_session):
    """Activity 1 db fixture."""
    activity = await create_activity(get_test_async_session, 'Еда')
    return activity


@pytest.fixture(scope='function')
async def activity11(get_test_async_session, activity1):
    """Activity 11 db fixture."""
    activity = await create_activity(get_test_async_session, 'Мясная продукция', activity1.uuid)
    return activity


@pytest.fixture(scope='function')
async def activity111(get_test_async_session, activity11):
    """Activity 111 db fixture."""
    activity = await create_activity(get_test_async_session, 'Курица', activity11.uuid)
    return activity


@pytest.fixture(scope='function')
async def activity112(get_test_async_session, activity11):
    """Activity 112 db fixture."""
    activity = await create_activity(get_test_async_session, 'Говядина', activity11.uuid)
    return activity


@pytest.fixture(scope='function')
async def activity12(get_test_async_session, activity1):
    """Activity 12 db fixture."""
    activity = await create_activity(get_test_async_session, 'Молочная продукция', activity1.uuid)
    return activity


@pytest.fixture(scope='function')
async def activity2(get_test_async_session):
    """Activity 2 db fixture."""
    activity = await create_activity(get_test_async_session, 'Автомобили')
    return activity


async def create_organization(
        get_test_async_session: AsyncSession,
        name: str,
        building_uuid: UUID,
        phones: list[str],
        activity_uuids: list[UUID]
) -> OrganizationDB:
    """Create organization."""
    data = {
        'name': name,
        'building_uuid': building_uuid,
    }
    organization = OrganizationDB(**data)
    get_test_async_session.add(organization)
    await get_test_async_session.flush()
    inserted_data = []
    for phone in phones:
        inserted_data.append(
            PhoneDB(phone=phone, organization_uuid=organization.uuid)
        )
    for activity_uuid in activity_uuids:
        inserted_data.append(
            OrganizationActivityDB(activity_uuid=activity_uuid, organization_uuid=organization.uuid)
        )
    get_test_async_session.add_all(inserted_data)
    await get_test_async_session.commit()
    query = (
        select(OrganizationDB)
        .where(OrganizationDB.uuid == organization.uuid)
        .options(
            joinedload(OrganizationDB.building), selectinload(OrganizationDB.phones),
            selectinload(OrganizationDB.activities).selectinload(ActivityDB.parent, recursion_depth=2),
        )
    )
    organization = await get_test_async_session.scalar(query)
    return organization


@pytest.fixture(scope='function')
async def organization(get_test_async_session, activity111, building):
    """Organization db fixture."""
    organization = await create_organization(
        get_test_async_session, 'Organization 1', building.uuid, ['88005553535'], [activity111.uuid]
    )
    return organization


@pytest.fixture(scope='function')
async def organization2(get_test_async_session, activity112, building2):
    """Organization 2 db fixture."""
    organization = await create_organization(
        get_test_async_session, 'Organization 2', building2.uuid, ['88005553536'], [activity112.uuid]
    )
    return organization


@pytest.fixture(scope='function')
async def organization3(get_test_async_session, activity2, building3):
    """Organization 2 db fixture."""
    organization = await create_organization(
        get_test_async_session, 'Organization 3', building3.uuid, ['88005553537'], [activity2.uuid]
    )
    return organization
