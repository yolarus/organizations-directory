from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import insert, Select, select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from starlette import status

from src import ActivityDB
from src.activities.schemas import ActivityCreateSchema, ActivityOutSchema, ActivityDetailSchema, ActivityUpdateSchema
from src.base.sessions import BaseSession
from src.base.utils import handle_error


class ActivitySession(BaseSession):
    """Activity session."""

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
                parent_uuid = data.pop('parent_uuid', 'plug')
                query = (
                    update(ActivityDB)
                    .where(ActivityDB.uuid == activity_uuid)
                    .values(**data)
                    .returning(ActivityDB)
                    .options(
                        selectinload(ActivityDB.children)
                    )
                )
                activity = await self.session.scalar(query)
                if not activity:
                    raise HTTPException(status.HTTP_404_NOT_FOUND, 'Activity not found')
                if parent_uuid != 'plug' and activity.children:
                    detail = 'Not possible to change parent activity while the activity has children activities'
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail)
                if parent_uuid == activity_uuid:
                    detail = 'Not possible to choice the same activity as a parent'
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail)
                if parent_uuid != 'plug':
                    query = (
                        update(ActivityDB)
                        .where(ActivityDB.uuid == activity_uuid)
                        .values(parent_uuid=parent_uuid)
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

    async def activity_delete(self, activity_uuid: UUID) -> None:
        """Activity delete."""
        try:
            async with self.session.begin():
                query = (
                    delete(ActivityDB)
                    .where(ActivityDB.uuid == activity_uuid)
                    .returning(ActivityDB)
                )
                activity = await self.session.scalar(query)
                if not activity:
                    raise HTTPException(status.HTTP_404_NOT_FOUND, 'Activity not found')
        except IntegrityError as err:
            return handle_error(err)
