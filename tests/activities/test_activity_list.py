from starlette import status

from src.base.base_test import BaseTestCase


class TestActivityListCase(BaseTestCase):
    """Activity list test suite."""
    url = '/activities/'

    async def test_activity_list(self, activity1, activity2, activity11, activity12, activity111, activity112):
        """Test activity list."""
        response = await self.make_get(self.url)
        assert len(response['items']) == 2
        for item in response['items']:
            if item['uuid'] == str(activity1.uuid):
                assert len(item['children']) == 2
            elif item['uuid'] == str(activity2.uuid):
                assert len(item['children']) == 0
            elif item['uuid'] == str(activity11.uuid):
                assert len(item['children']) == 2
            elif item['uuid'] == str(activity12.uuid):
                assert len(item['children']) == 0
            elif item['uuid'] == str(activity111.uuid):
                assert len(item['children']) == 0
            elif item['uuid'] == str(activity112.uuid):
                assert len(item['children']) == 0

    async def test_activity_list_401(self):
        """Test activity list Unauthorized."""
        await self.make_get(self.url, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_activity_list_405(self):
        """Test activity list Method not allowed."""
        await self.make_put(self.url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
