from uuid import UUID

import pytest
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src import ActivityDB


async def create_activity(
        session: AsyncSession, name: str, parent_uuid: UUID | None = None
) -> ActivityDB:
    """Create activity."""
    async with session.begin():
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
        activity = await session.scalar(query)
    return activity


@pytest.fixture(scope='function')
async def activity1(get_override_async_session):
    """Activity 1 db fixture."""
    activity = await create_activity(get_override_async_session, 'Еда')
    return activity


@pytest.fixture(scope='function')
async def activity11(get_override_async_session, activity1):
    """Activity 11 db fixture."""
    activity = await create_activity(get_override_async_session, 'Мясная продукция', activity1.uuid)
    return activity


@pytest.fixture(scope='function')
async def activity111(get_override_async_session, activity11):
    """Activity 111 db fixture."""
    activity = await create_activity(get_override_async_session, 'Курица', activity11.uuid)
    return activity


@pytest.fixture(scope='function')
async def activity112(get_override_async_session, activity11):
    """Activity 112 db fixture."""
    activity = await create_activity(get_override_async_session, 'Говядина', activity11.uuid)
    return activity


@pytest.fixture(scope='function')
async def activity12(get_override_async_session, activity1):
    """Activity 12 db fixture."""
    activity = await create_activity(get_override_async_session, 'Молочная продукция', activity1.uuid)
    return activity


@pytest.fixture(scope='function')
async def activity2(get_override_async_session):
    """Activity 2 db fixture."""
    activity = await create_activity(get_override_async_session, 'Автомобили')
    return activity
