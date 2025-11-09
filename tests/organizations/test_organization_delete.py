import uuid

from starlette import status

from src.base.base_test import BaseTestCase


class TestOrganizationDeleteCase(BaseTestCase):
    """Organization delete test suite."""
    url = '/organizations'

    async def test_organization_delete(self, organization):
        """Test organization delete."""
        url = f'{self.url}/{organization.uuid}/'
        await self.make_delete(url)
        await self.make_delete(url, status_code=status.HTTP_404_NOT_FOUND)

    async def test_organization_delete_401(self, organization):
        """Test organization delete Unauthorized."""
        url = f'{self.url}/{organization.uuid}/'
        await self.make_delete(url, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_organization_delete_404(self, organization):
        """Test organization delete Not found."""
        url = f'{self.url}/{uuid.uuid4()}/'
        await self.make_delete(url, status_code=status.HTTP_404_NOT_FOUND)

    async def test_organization_delete_405(self, organization):
        """Test organization delete Method not allowed."""
        url = f'{self.url}/{organization.uuid}/'
        await self.make_put(url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_organization_delete_422(self, organization):
        """Test organization delete Unprocessable content."""
        url = f'{self.url}/{organization.uuid} /'
        await self.make_delete(url, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
