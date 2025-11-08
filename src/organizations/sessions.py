from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import insert, Select, select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload, joinedload
from starlette import status

from src import OrganizationDB, PhoneDB, OrganizationActivityDB, ActivityDB
from src.base.schemas import UUIDSchema
from src.base.sessions import BaseSession
from src.base.utils import handle_error
from src.organizations.schemas import OrganizationCreateSchema, OrganizationDetailSchema, OrganizationUpdateSchema
from src.organizations.services import get_activities_tree


class OrganizationSession(BaseSession):
    """Organization session."""

    async def organization_create(self, body: OrganizationCreateSchema) -> OrganizationDB | UUIDSchema:
        """Organization create."""
        try:
            async with self.session.begin():
                data = body.model_dump()
                phones = data.pop('phones', [])
                activity_uuids = data.pop('activity_uuids', [])
                query = insert(OrganizationDB).values(**data).returning(OrganizationDB)
                organization = await self.session.scalar(query)
                inserted_data = []
                for phone in phones:
                    inserted_data.append(PhoneDB(phone=phone, organization_uuid=organization.uuid))
                for activity_uuid in activity_uuids:
                    inserted_data.append(
                        OrganizationActivityDB(activity_uuid=activity_uuid, organization_uuid=organization.uuid)
                    )
                self.session.add_all(inserted_data)
        except IntegrityError as err:
            return handle_error(err)
        return organization

    async def organization_list(self) -> Select:
        """Organization list."""
        query = select(OrganizationDB).options(selectinload(OrganizationDB.phones))
        return query

    async def organization_detail(self, organization_uuid) -> OrganizationDetailSchema:
        """Organization detail."""
        async with self.session.begin():
            query = (
                select(OrganizationDB)
                .where(OrganizationDB.uuid == organization_uuid)
                .options(
                    joinedload(OrganizationDB.building), selectinload(OrganizationDB.phones),
                    selectinload(OrganizationDB.activities).selectinload(ActivityDB.parent, recursion_depth=2),
                )
            )
            organization = await self.session.scalar(query)
            if not organization:
                raise HTTPException(status.HTTP_404_NOT_FOUND, 'Organization not found')
            schema = OrganizationDetailSchema.model_validate(organization, from_attributes=True)
            schema.activities_tree = await get_activities_tree(organization.activities)
            return schema

    async def organization_update(
            self, body: OrganizationUpdateSchema, organization_uuid: UUID
    ) -> OrganizationDB | UUIDSchema:
        """Organization update."""
        try:
            async with self.session.begin():
                data = body.model_dump(exclude_unset=True)
                phones: list[str] | None = data.pop('phones', None)
                activity_uuids: list[UUID] | None = data.pop('activity_uuids', None)
                query = (
                    update(OrganizationDB)
                    .where(OrganizationDB.uuid == organization_uuid)
                    .values(**data)
                    .returning(OrganizationDB)
                )
                organization = await self.session.scalar(query)
                inserted_data = []
                if phones is not None:
                    if len(phones) == 0:
                        detail = {'field': 'phones', 'message': 'Organization should have at least one phone number'}
                        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, [detail])
                    query = delete(PhoneDB).where(PhoneDB.organization_uuid == organization.uuid)
                    await self.session.execute(query)
                    for phone in phones:
                        inserted_data.append(PhoneDB(phone=phone, organization_uuid=organization.uuid))
                if activity_uuids is not None:
                    query = (
                        delete(OrganizationActivityDB)
                        .where(OrganizationActivityDB.organization_uuid == organization.uuid)
                    )
                    await self.session.execute(query)
                    for activity_uuid in activity_uuids:
                        inserted_data.append(
                            OrganizationActivityDB(activity_uuid=activity_uuid, organization_uuid=organization.uuid)
                        )
                self.session.add_all(inserted_data)
        except IntegrityError as err:
            return handle_error(err)
        return organization

    async def organization_delete(self, organization_uuid: UUID) -> None:
        """Organization delete."""
        async with self.session.begin():
            query = (
                delete(OrganizationDB)
                .where(OrganizationDB.uuid == organization_uuid)
                .returning(OrganizationDB)
            )
            organization = await self.session.execute(query)
            if not organization:
                raise HTTPException(status.HTTP_404_NOT_FOUND, 'Organization not found')
