import uuid

from starlette import status

from src.base.base_test import BaseTestCase


class TestActivityCreateCase(BaseTestCase):
    """Activity create test suite."""
    url = '/organizations/activities/'

    @staticmethod
    def get_data(name: str = 'Test activity', parent_uuid: uuid.UUID = None) -> dict:
        """Get data."""
        data = {
            'name': name,
            'parent_uuid': str(parent_uuid) if parent_uuid else None,
        }
        return data

    async def test_activity_create(self):
        """Test activity create."""
        data = self.get_data()
        await self.make_post(self.url, data, status_code=status.HTTP_201_CREATED)
        await self.make_post(self.url, data, status_code=status.HTTP_409_CONFLICT)

    async def test_activity_create_400(self, activity111):
        """Test activity create Bad request."""
        data = self.get_data(parent_uuid=activity111.uuid)
        await self.make_post(self.url, data, status_code=status.HTTP_400_BAD_REQUEST)

    async def test_activity_create_401(self):
        """Test activity create Unauthorized."""
        data = self.get_data()
        await self.make_post(self.url, data, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_activity_create_404(self):
        """Test activity create Not found."""
        data = self.get_data(parent_uuid=uuid.uuid4())
        await self.make_post(self.url, data, status_code=status.HTTP_404_NOT_FOUND)

    async def test_activity_create_405(self):
        """Test activity create Method not allowed."""
        await self.make_put(self.url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_activity_create_409(self, activity1):
        """Test activity create Conflict."""
        data = self.get_data('Еда')
        await self.make_post(self.url, data, status_code=status.HTTP_409_CONFLICT)

    async def test_activity_create_422(self, ):
        """Test activity create Unprocessable content."""
        data = self.get_data()
        data['name'] = 123
        await self.make_post(self.url, data, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
