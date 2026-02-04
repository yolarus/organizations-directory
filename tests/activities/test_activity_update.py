import uuid

from starlette import status

from src.base.base_test import BaseTestCase


class TestActivityUpdateCase(BaseTestCase):
    """Activity update test suite."""
    url = '/activities'

    async def test_activity_update(self, activity1, activity2):
        """Test activity update."""
        url = f'{self.url}/{activity1.uuid}/'
        data = {
            'name': 'Test name',
            'parent_uuid': str(activity2.uuid),
        }
        response = await self.make_patch(url, data)
        result = {
            'uuid': str(activity1.uuid),
            'name': 'Test name',
            'parent': {
                'uuid': str(activity2.uuid),
                'name': activity2.name,
                'parent': activity2.parent
            }
        }
        assert response == result

    async def test_activity_update_400_1(self, activity2, activity11, activity111):
        """Test activity update Bad request."""
        url = f'{self.url}/{activity11.uuid}/'
        data = {
            'parent_uuid': str(activity2.uuid)
        }
        response = await self.make_patch(url, data, status_code=status.HTTP_400_BAD_REQUEST)
        detail = 'Not possible to change parent activity while the activity has children activities'
        assert response['detail'] == detail

    async def test_activity_update_400_2(self, activity1):
        """Test activity update Bad request."""
        url = f'{self.url}/{activity1.uuid}/'
        data = {
            'parent_uuid': str(activity1.uuid)
        }
        response = await self.make_patch(url, data, status_code=status.HTTP_400_BAD_REQUEST)
        detail = 'Not possible to choice the same activity as a parent'
        assert response['detail'] == detail

    async def test_activity_update_400_3(self, activity111, activity112):
        """Test activity update Bad request."""
        url = f'{self.url}/{activity111.uuid}/'
        data = {
            'parent_uuid': str(activity112.uuid)
        }
        response = await self.make_patch(url, data, status_code=status.HTTP_400_BAD_REQUEST)
        detail = 'Not possible to choice parent activity with third level depth'
        assert response['detail'] == detail

    async def test_activity_update_401(self, activity1):
        """Test activity update Unauthorized."""
        url = f'{self.url}/{activity1.uuid}/'
        await self.make_patch(url, {}, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_activity_update_404_1(self, activity1):
        """Test activity update Not found."""
        url = f'{self.url}/{uuid.uuid4()}/'
        data = {
            'name': 'Test name'
        }
        await self.make_patch(url, data, status_code=status.HTTP_404_NOT_FOUND)

    async def test_activity_update_404_2(self, activity1):
        """Test activity update Not found."""
        url = f'{self.url}/{activity1.uuid}/'
        data = {
            'parent_uuid': str(uuid.uuid4())
        }
        await self.make_patch(url, data, status_code=status.HTTP_404_NOT_FOUND)

    async def test_activity_update_405(self, activity1):
        """Test activity update Method not allowed."""
        url = f'{self.url}/{activity1.uuid}/'
        await self.make_put(url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_activity_update_409(self, activity1, activity2):
        """Test activity update Conflict."""
        url = f'{self.url}/{activity1.uuid}/'
        data = {
            'name': activity2.name
        }
        await self.make_patch(url, data, status_code=status.HTTP_409_CONFLICT)

    async def test_activity_update_422(self, activity1):
        """Test activity update Unprocessable content."""
        url = f'{self.url}/{activity1.uuid} /'
        data = {
            'name': 'Test name'
        }
        await self.make_patch(url, data, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
