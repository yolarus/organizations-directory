from uuid import UUID, uuid4

from starlette import status

from src.base.base_test import BaseTestCase


class TestOrganizationCreateCase(BaseTestCase):
    """Organization create test suite."""
    url = '/organizations/'

    @staticmethod
    def get_data(building_uuid: UUID, activity_uuids: list[UUID]) -> dict:
        """Get data."""
        data = {
            'name': 'Test organization',
            'building_uuid': str(building_uuid),
            'phones': ['88005553535'],
            'activity_uuids': [str(i) for i in activity_uuids],
        }
        return data

    async def test_organization_create(self, building, activity111):
        """Test organization create."""
        data = self.get_data(building.uuid, [activity111.uuid])
        await self.make_post(self.url, data, status_code=status.HTTP_201_CREATED)
        await self.make_post(self.url, data, status_code=status.HTTP_409_CONFLICT)

    async def test_organization_create_401(self, building, activity111):
        """Test organization create Unauthorized."""
        data = self.get_data(building.uuid, [activity111.uuid])
        await self.make_post(self.url, data, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_organization_create_404(self, building, activity111):
        """Test organization create Not found."""
        data = self.get_data(uuid4(), [activity111.uuid])
        await self.make_post(self.url, data, status_code=status.HTTP_404_NOT_FOUND)

    async def test_organization_create_405(self):
        """Test organization create Method not allowed."""
        await self.make_put(self.url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_organization_create_409(self, organization, building, activity111):
        """Test organization create Conflict."""
        data = self.get_data(building.uuid, [activity111.uuid])
        await self.make_post(self.url, data, status_code=status.HTTP_409_CONFLICT)

    async def test_organization_create_422(self, building, activity111):
        """Test organization create Unprocessable content."""
        data = self.get_data(building.uuid, [activity111.uuid])
        data['name'] = 123
        await self.make_post(self.url, data, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
