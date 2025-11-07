from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from src import OrganizationDB, PhoneDB, OrganizationActivityDB
from src.base.schemas import UUIDSchema
from src.base.sessions import BaseSession
from src.base.utils import handle_error
from src.organizations.schemas import OrganizationCreateRequestSchema


class OrganizationSession(BaseSession):
    """Organization session."""

    async def organization_create(self, body: OrganizationCreateRequestSchema) -> OrganizationDB | UUIDSchema:
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
