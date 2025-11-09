import uuid

from starlette import status

from src.base.base_test import BaseTestCase


class TestBuildingDeleteCase(BaseTestCase):
    """Building delete test suite."""
    url = '/organizations/buildings'

    async def test_building_delete(self, building):
        """Test building delete."""
        url = f'{self.url}/{building.uuid}/'
        await self.make_delete(url)
        await self.make_delete(url, status_code=status.HTTP_404_NOT_FOUND)

    async def test_building_delete_401(self, building):
        """Test building delete Unauthorized."""
        url = f'{self.url}/{building.uuid}/'
        await self.make_delete(url, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_building_delete_404(self, building):
        """Test building delete Not found."""
        url = f'{self.url}/{uuid.uuid4()}/'
        await self.make_delete(url, status_code=status.HTTP_404_NOT_FOUND)

    async def test_building_delete_405(self, building):
        """Test building delete Method not allowed."""
        url = f'{self.url}/{building.uuid}/'
        await self.make_put(url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_building_delete_409(self, organization, building):
        """Test building delete Conflict."""
        url = f'{self.url}/{building.uuid}/'
        await self.make_delete(url, status_code=status.HTTP_409_CONFLICT)

    async def test_building_delete_422(self, building):
        """Test building delete Unprocessable content."""
        url = f'{self.url}/{building.uuid} /'
        await self.make_delete(url, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
