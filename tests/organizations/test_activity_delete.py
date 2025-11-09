import uuid

from starlette import status

from src.base.base_test import BaseTestCase


class TestActivityDeleteCase(BaseTestCase):
    """Activity delete test suite."""
    url = '/organizations/activities'

    async def test_activity_delete(self, activity1, activity11, activity12):
        """Test activity delete."""
        url = f'{self.url}/{activity1.uuid}/'
        await self.make_delete(url)
        await self.make_delete(url, status_code=status.HTTP_404_NOT_FOUND)
        url = f'{self.url}/{activity11.uuid}/'
        await self.make_delete(url, status_code=status.HTTP_404_NOT_FOUND)
        url = f'{self.url}/{activity12.uuid}/'
        await self.make_delete(url, status_code=status.HTTP_404_NOT_FOUND)

    async def test_activity_delete_401(self, activity1):
        """Test activity delete Unauthorized."""
        url = f'{self.url}/{activity1.uuid}/'
        await self.make_delete(url, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_activity_delete_404(self, activity1):
        """Test activity delete Not found."""
        url = f'{self.url}/{uuid.uuid4()}/'
        await self.make_delete(url, status_code=status.HTTP_404_NOT_FOUND)

    async def test_activity_delete_405(self, activity1):
        """Test activity delete Method not allowed."""
        url = f'{self.url}/{activity1.uuid}/'
        await self.make_put(url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_activity_delete_409(self, activity1, organization):
        """Test activity delete Conflict."""
        url = f'{self.url}/{activity1.uuid}/'
        await self.make_delete(url, status_code=status.HTTP_409_CONFLICT)

    async def test_activity_delete_422(self, activity1):
        """Test activity delete Unprocessable content."""
        url = f'{self.url}/{activity1.uuid} /'
        await self.make_delete(url, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
