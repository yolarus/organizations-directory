from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from src.config.settings import project_config

# Create async engine for interaction with database
engine = create_async_engine(
    project_config.database.database_url
)

# Create session for the interaction with database
async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async session."""
    try:
        async with async_session_maker() as session:
            yield session
    finally:
        await session.close()
