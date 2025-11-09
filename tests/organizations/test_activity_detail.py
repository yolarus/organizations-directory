import uuid

from starlette import status

from src.base.base_test import BaseTestCase


class TestActivityDetailCase(BaseTestCase):
    """Activity detail test suite."""
    url = '/organizations/activities'

    async def test_activity_detail(self, activity1):
        """Test activity detail."""
        url = f'{self.url}/{activity1.uuid}/'
        data = {
            'uuid': str(activity1.uuid),
            'name': str(activity1.name),
            'parent': activity1.parent,
            'children': activity1.children
        }
        response = await self.make_get(url)
        assert response == data

    async def test_activity_detail_401(self, activity1):
        """Test activity detail Unauthorized."""
        url = f'{self.url}/{activity1.uuid}/'
        await self.make_get(url, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_activity_detail_404(self, activity1):
        """Test activity detail Not found."""
        url = f'{self.url}/{uuid.uuid4()}/'
        await self.make_get(url, status_code=status.HTTP_404_NOT_FOUND)

    async def test_activity_detail_405(self, activity1):
        """Test activity detail Method not allowed."""
        url = f'{self.url}/{activity1.uuid}/'
        await self.make_put(url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_activity_detail_422(self, activity1):
        """Test activity detail Unprocessable content."""
        url = f'{self.url}/{activity1.uuid} /'
        await self.make_get(url, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
