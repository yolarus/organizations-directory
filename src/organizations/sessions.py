from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import insert, Select, select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload, joinedload
from starlette import status

from src import OrganizationDB, PhoneDB, OrganizationActivityDB, ActivityDB, BuildingDB
from src.base.schemas import UUIDSchema
from src.base.sessions import BaseSession
from src.base.utils import handle_error
from src.organizations.schemas import OrganizationCreateSchema, OrganizationDetailSchema, OrganizationUpdateSchema, \
    BuildingOutSchema, BuildingCreateSchema, BuildingUpdateSchema, ActivityCreateSchema, ActivityOutSchema, \
    ActivityDetailSchema, ActivityUpdateSchema
from src.organizations.services import get_activities_tree, filter_organizations, filter_buildings


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

    async def organization_list(self, **filters) -> Select:
        """Organization list."""
        query = (
            select(OrganizationDB)
            .options(selectinload(OrganizationDB.phones), selectinload(OrganizationDB.building))
        )
        query = await filter_organizations(self.session, query, **filters)
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
                if not organization:
                    raise HTTPException(status.HTTP_404_NOT_FOUND, 'Organization not found')
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
            organization = await self.session.scalar(query)
            if not organization:
                raise HTTPException(status.HTTP_404_NOT_FOUND, 'Organization not found')

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
        async with self.session.begin():
            query = (
                delete(BuildingDB)
                .where(BuildingDB.uuid == building_uuid)
                .returning(BuildingDB)
            )
            building = await self.session.scalar(query)
            if not building:
                raise HTTPException(status.HTTP_404_NOT_FOUND, 'Building not found')

    async def activity_create(self, body: ActivityCreateSchema) -> ActivityDB | ActivityOutSchema:
        """Activity create."""
        try:
            async with self.session.begin():
                data = body.model_dump()
                query = (
                    insert(ActivityDB)
                    .values(**data)
                    .returning(ActivityDB)
                    .options(
                        selectinload(ActivityDB.parent, recursion_depth=2),
                    )
                )
                activity = await self.session.scalar(query)
                if activity.parent and activity.parent.parent and activity.parent.parent.parent_uuid:
                    detail = 'Not possible to choice parent activity with third level depth'
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail)
        except IntegrityError as err:
            return handle_error(err)
        return activity

    async def activity_list(self) -> Select:
        """Activity list."""
        query = (
            select(ActivityDB)
            .where(ActivityDB.parent_uuid.is_(None))
            .options(
                selectinload(ActivityDB.children, recursion_depth=2)
            )
        )
        return query

    async def activity_detail(self, activity_uuid) -> ActivityDB | ActivityDetailSchema:
        """Activity detail."""
        async with self.session.begin():
            query = (
                select(ActivityDB)
                .where(ActivityDB.uuid == activity_uuid)
                .options(
                    selectinload(ActivityDB.parent, recursion_depth=2),
                    selectinload(ActivityDB.children, recursion_depth=2)
                )
            )
            activity = await self.session.scalar(query)
            if not activity:
                raise HTTPException(status.HTTP_404_NOT_FOUND, 'Activity not found')
            return activity

    async def activity_update(self, body: ActivityUpdateSchema, activity_uuid: UUID) -> ActivityDB | ActivityOutSchema:
        """Activity update."""
        try:
            async with self.session.begin():
                data = body.model_dump(exclude_unset=True)
                parent_uuid = data.get('parent_uuid')
                query = (
                    update(ActivityDB)
                    .where(ActivityDB.uuid == activity_uuid)
                    .values(**data)
                    .returning(ActivityDB)
                    .options(
                        selectinload(ActivityDB.parent, recursion_depth=2),
                        selectinload(ActivityDB.children)
                    )
                )
                activity = await self.session.scalar(query)
                if not activity:
                    raise HTTPException(status.HTTP_404_NOT_FOUND, 'Activity not found')
                if parent_uuid and activity.children:
                    detail = 'Not possible to change parent activity while the activity has children activities'
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail)
                if parent_uuid == activity_uuid:
                    detail = 'Not possible to chose the same activity as a parent.'
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail)
                if activity.parent and activity.parent.parent and activity.parent.parent.parent_uuid:
                    detail = 'Not possible to choice parent activity with third level depth'
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail)
        except IntegrityError as err:
            return handle_error(err)
        return activity

    async def activity_delete(self, activity_uuid: UUID) -> None:
        """Activity delete."""
        async with self.session.begin():
            query = (
                delete(ActivityDB)
                .where(ActivityDB.uuid == activity_uuid)
                .returning(ActivityDB)
            )
            activity = await self.session.scalar(query)
            if not activity:
                raise HTTPException(status.HTTP_404_NOT_FOUND, 'Activity not found')
