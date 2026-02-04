from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src import BuildingDB


async def create_building(
        session: AsyncSession, address: str, latitude: Decimal, longitude: Decimal
) -> BuildingDB:
    """Create building."""
    async with session.begin():
        data = {
            'address': address,
            'latitude': latitude,
            'longitude': longitude,
        }
        building = BuildingDB(**data)
        session.add(building)
    return building


@pytest.fixture(scope='function')
async def building(get_override_async_session):
    """Building db fixture."""
    building = await create_building(
        get_override_async_session, 'Пятницкая улица, 25А', Decimal(55.741503), Decimal(37.628861)
    )
    return building


@pytest.fixture(scope='function')
async def building2(get_override_async_session):
    """Building 2 db fixture."""
    building = await create_building(
        get_override_async_session, 'Проспект мира, 211к1', Decimal(55.843941), Decimal(37.662335)
    )
    return building


@pytest.fixture(scope='function')
async def building3(get_override_async_session):
    """Building 3 db fixture."""
    building = await create_building(
        get_override_async_session, 'Проспект мира, 38', Decimal(55.779665), Decimal(37.633636)
    )
    return building
