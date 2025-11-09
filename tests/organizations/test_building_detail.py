import uuid
from decimal import Decimal

from starlette import status

from src.base.base_test import BaseTestCase


class TestBuildingDetailCase(BaseTestCase):
    """Building detail test suite."""
    url = '/organizations/buildings'

    async def test_building_detail(self, building):
        """Test building detail."""
        url = f'{self.url}/{building.uuid}/'
        response = await self.make_get(url)
        for key, value in response.items():
            model_value = getattr(building, key)
            if isinstance(model_value, Decimal):
                assert round(model_value, 13) == round(Decimal(value), 13)
            else:
                assert str(model_value) == str(value)

    async def test_building_detail_401(self, building):
        """Test building detail Unauthorized."""
        url = f'{self.url}/{building.uuid}/'
        await self.make_get(url, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_building_detail_404(self, building):
        """Test building detail Not found."""
        url = f'{self.url}/{uuid.uuid4()}/'
        await self.make_get(url, status_code=status.HTTP_404_NOT_FOUND)

    async def test_building_detail_405(self, building):
        """Test building detail Method not allowed."""
        url = f'{self.url}/{building.uuid}/'
        await self.make_put(url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_building_detail_422(self, building):
        """Test building detail Unprocessable content."""
        url = f'{self.url}/{building.uuid} /'
        await self.make_get(url, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
