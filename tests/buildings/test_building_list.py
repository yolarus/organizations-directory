import uuid

from starlette import status

from src.base.base_test import BaseTestCase


class TestBuildingListCase(BaseTestCase):
    """Building list test suite."""
    url = '/buildings/'

    async def test_building_list(self, building, building2, building3):
        """Test building list."""
        response = await self.make_get(self.url)
        assert len(response['items']) == 3

        params = {
            'latitude': '55.847336',
            'longitude': '37.635552',
            'radius': 10
        }
        response = await self.make_get(self.url, params)
        assert len(response['items']) == 2

    async def test_building_list_400(self, building, building2, building3):
        """Test building list Bad request."""
        params = {
            'latitude': '55.847336',
            'longitude': '37.635552'
        }
        await self.make_get(self.url, params, status_code=status.HTTP_400_BAD_REQUEST)

    async def test_building_list_401(self):
        """Test building list Unauthorized."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_building_list_405(self):
        """Test building list Method not allowed."""
        await self.make_put(self.url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_building_list_422(self, building, building2, building3):
        """Test building list Unprocessable content."""
        params = {
            'latitude': uuid.uuid4(),
            'longitude': uuid.uuid4(),
            'radius': uuid.uuid4()
        }
        await self.make_get(self.url, params, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
