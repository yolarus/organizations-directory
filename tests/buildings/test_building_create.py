import uuid

from starlette import status

from src.base.base_test import BaseTestCase


class TestBuildingCreateCase(BaseTestCase):
    """Building create test suite."""
    url = '/buildings/'

    @staticmethod
    def get_data() -> dict:
        """Get data."""
        data = {
            'address': 'test_address',
            'latitude': 55.847336,
            'longitude': 37.635552,
            'radius': 10
        }
        return data

    async def test_building_create(self):
        """Test building create."""
        data = self.get_data()
        await self.make_post(self.url, data, status_code=status.HTTP_201_CREATED)
        await self.make_post(self.url, data, status_code=status.HTTP_409_CONFLICT)

    async def test_building_create_401(self):
        """Test building create Unauthorized."""
        data = self.get_data()
        await self.make_post(self.url, data, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_building_create_405(self):
        """Test building create Method not allowed."""
        await self.make_put(self.url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_building_create_422(self, building, building2, building3):
        """Test building create Unprocessable content."""
        data = self.get_data()
        data['latitude'] = str(uuid.uuid4())
        await self.make_post(self.url, data, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
