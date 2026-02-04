from typing import AsyncGenerator

import pytest
from sqlalchemy import StaticPool, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.base.models import BaseDBModel
from src.config.session import get_async_session
from src.config.settings import project_config
from src.main import app

pytest_plugins = [
    'tests.fixtures.activities',
    'tests.fixtures.buildings',
    'tests.fixtures.organizations',
]

db_url = project_config.database.test_database_url
project_config.database.database_url = db_url
engine_test = create_async_engine(db_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
event.listen(engine_test.sync_engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))

async_session_maker = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Override async session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_async_session] = override_async_session


@pytest.fixture(scope='function')
async def get_override_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get override async session fixture."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(autouse=True, scope='function')
async def prepare_database():
    """Prepare database."""
    async with engine_test.begin() as conn:
        await conn.run_sync(BaseDBModel.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(BaseDBModel.metadata.drop_all)
