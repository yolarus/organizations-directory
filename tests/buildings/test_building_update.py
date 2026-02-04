import uuid
from decimal import Decimal

from starlette import status

from src.base.base_test import BaseTestCase


class TestBuildingUpdateCase(BaseTestCase):
    """Building update test suite."""
    url = '/buildings'

    async def test_building_update(self, building):
        """Test building update."""
        url = f'{self.url}/{building.uuid}/'
        data = {
            'address': 'Test address'
        }
        response = await self.make_patch(url, data)
        for key, value in response.items():
            if key in data:
                assert data[key] == value
            else:
                model_value = getattr(building, key)
                if isinstance(model_value, Decimal):
                    assert round(model_value, 13) == round(Decimal(value), 13)
                else:
                    assert str(model_value) == str(value)

    async def test_building_update_401(self, building):
        """Test building update Unauthorized."""
        url = f'{self.url}/{building.uuid}/'
        await self.make_patch(url, {}, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_building_update_404(self, building):
        """Test building update Not found."""
        url = f'{self.url}/{uuid.uuid4()}/'
        data = {
            'address': 'Test address'
        }
        await self.make_patch(url, data, status_code=status.HTTP_404_NOT_FOUND)

    async def test_building_update_405(self, building):
        """Test building update Method not allowed."""
        url = f'{self.url}/{building.uuid}/'
        await self.make_put(url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_building_update_409(self, building, building2):
        """Test building update Conflict."""
        url = f'{self.url}/{building.uuid}/'
        data = {
            'address': building2.address
        }
        await self.make_patch(url, data, status_code=status.HTTP_409_CONFLICT)

    async def test_building_update_422(self, building):
        """Test building update Unprocessable content."""
        url = f'{self.url}/{building.uuid} /'
        data = {
            'address': 'Test address'
        }
        await self.make_patch(url, data, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
