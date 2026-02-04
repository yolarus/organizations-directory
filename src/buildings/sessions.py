from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import insert, Select, select, update, delete
from sqlalchemy.exc import IntegrityError
from starlette import status

from src import BuildingDB
from src.base.sessions import BaseSession
from src.base.utils import handle_error
from src.buildings.schemas import BuildingCreateSchema, BuildingOutSchema, BuildingUpdateSchema
from src.buildings.services import filter_buildings


class BuildingSession(BaseSession):
    """Building session."""

    async def building_create(self, body: BuildingCreateSchema) -> BuildingDB | BuildingOutSchema:
        """Building create."""
        try:
            async with self.session.begin():
                data = body.model_dump()
                query = insert(BuildingDB).values(**data).returning(BuildingDB)
                building = await self.session.scalar(query)
        except IntegrityError as err:
            return handle_error(err)
        return building

    async def building_list(self, **filters) -> Select:
        """Building list."""
        query = select(BuildingDB)
        query = await filter_buildings(self.session, query, **filters)
        return query

    async def building_detail(self, building_uuid) -> BuildingDB | BuildingOutSchema:
        """Building detail."""
        async with self.session.begin():
            query = (
                select(BuildingDB)
                .where(BuildingDB.uuid == building_uuid)
            )
            building = await self.session.scalar(query)
            if not building:
                raise HTTPException(status.HTTP_404_NOT_FOUND, 'Building not found')
            return building

    async def building_update(self, body: BuildingUpdateSchema, building_uuid: UUID) -> BuildingDB | BuildingOutSchema:
        """Building update."""
        try:
            async with self.session.begin():
                data = body.model_dump(exclude_unset=True)
                query = (
                    update(BuildingDB)
                    .where(BuildingDB.uuid == building_uuid)
                    .values(**data)
                    .returning(BuildingDB)
                )
                building = await self.session.scalar(query)
                if not building:
                    raise HTTPException(status.HTTP_404_NOT_FOUND, 'Building not found')
        except IntegrityError as err:
            return handle_error(err)
        return building

    async def building_delete(self, building_uuid: UUID) -> None:
        """Building delete."""
        try:
            async with self.session.begin():
                query = (
                    delete(BuildingDB)
                    .where(BuildingDB.uuid == building_uuid)
                    .returning(BuildingDB)
                )
                building = await self.session.scalar(query)
                if not building:
                    raise HTTPException(status.HTTP_404_NOT_FOUND, 'Building not found')
        except IntegrityError as err:
            return handle_error(err)
