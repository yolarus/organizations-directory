import uuid

from starlette import status

from src.base.base_test import BaseTestCase


class TestOrganizationListCase(BaseTestCase):
    """Organization list test suite."""
    url = '/organizations/'

    async def test_organization_list(
            self,
            organization, organization2, organization3,
            building,
            activity1, activity111
    ):
        """Test organization list."""
        response = await self.make_get(self.url)
        assert len(response['items']) == 3

        params = {
            'building_uuid': str(building.uuid),
        }
        response = await self.make_get(self.url, params)
        assert len(response['items']) == 1

        params = {
            'activity_uuid': str(activity111.uuid),
        }
        response = await self.make_get(self.url, params)
        assert len(response['items']) == 1

        params = {
            'search_name': organization.name,
        }
        response = await self.make_get(self.url, params)
        assert len(response['items']) == 1

        params = {
            'search_activity': activity1.name[:len(activity1.name) // 2],
        }
        response = await self.make_get(self.url, params)
        assert len(response['items']) == 2

        params = {
            'latitude': '55.847336',
            'longitude': '37.635552',
            'radius': 10
        }
        response = await self.make_get(self.url, params)
        assert len(response['items']) == 2

    async def test_organization_list_400(self, organization, organization2, organization3):
        """Test organization list Bad request."""
        params = {
            'latitude': '55.847336',
            'longitude': '37.635552'
        }
        await self.make_get(self.url, params, status_code=status.HTTP_400_BAD_REQUEST)

    async def test_organization_list_401(self):
        """Test organization list Unauthorized."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_organization_list_405(self):
        """Test organization list Method not allowed."""
        await self.make_put(self.url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_organization_list_422(self, organization, organization2, organization3):
        """Test organization list Unprocessable content."""
        params = {
            'latitude': uuid.uuid4(),
            'longitude': uuid.uuid4(),
            'radius': uuid.uuid4()
        }
        await self.make_get(self.url, params, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
