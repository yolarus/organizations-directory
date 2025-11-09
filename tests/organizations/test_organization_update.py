import uuid

from starlette import status

from src.base.base_test import BaseTestCase


class TestOrganizationUpdateCase(BaseTestCase):
    """Organization update test suite."""
    url = '/organizations'

    async def test_organization_update(self, organization, building, activity1, activity11, activity112):
        """Test organization update."""
        url = f'{self.url}/{organization.uuid}/'
        data = {
            'address': 'Test address',
            'activity_uuids': [str(activity112.uuid)]
        }
        await self.make_patch(url, data)
        response = await self.make_get(url)
        result = {
            'uuid': str(organization.uuid),
            'name': organization.name,
            'building': {
                'uuid': str(building.uuid),
                'address': building.address,
                'latitude': str(round(building.latitude, 12)),
                'longitude': str(round(building.longitude, 12)),
            },
            'activities_tree': [
                {
                    'uuid': str(activity1.uuid),
                    'name': activity1.name,
                    'activities': [
                        {
                            'uuid': str(activity11.uuid),
                            'name': activity11.name,
                            'activities': [
                                {
                                    'uuid': str(activity112.uuid),
                                    'name': activity112.name,
                                    'activities': None
                                }
                            ]
                        }
                    ]
                }
            ],
            'phones': [
                {
                    'uuid': str(phone.uuid),
                    'phone': phone.phone
                }
                for phone in organization.phones]
        }
        assert response == result

    async def test_organization_update_401(self, organization):
        """Test organization update Unauthorized."""
        url = f'{self.url}/{organization.uuid}/'
        await self.make_patch(url, {}, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_organization_update_404_1(self, organization):
        """Test organization update Not found."""
        url = f'{self.url}/{uuid.uuid4()}/'
        data = {
            'name': 'Test name'
        }
        await self.make_patch(url, data, status_code=status.HTTP_404_NOT_FOUND)

    async def test_organization_update_404_2(self, organization):
        """Test organization update Not found."""
        url = f'{self.url}/{organization.uuid}/'
        data = {
            'name': 'Test name',
            'building_uuid': str(uuid.uuid4())
        }
        await self.make_patch(url, data, status_code=status.HTTP_404_NOT_FOUND)

    async def test_organization_update_405(self, organization):
        """Test organization update Method not allowed."""
        url = f'{self.url}/{organization.uuid}/'
        await self.make_put(url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_organization_update_409(self, organization, organization2):
        """Test organization update Conflict."""
        url = f'{self.url}/{organization.uuid}/'
        data = {
            'name': organization2.name
        }
        await self.make_patch(url, data, status_code=status.HTTP_409_CONFLICT)

    async def test_organization_update_422_1(self, organization):
        """Test organization update Unprocessable content."""
        url = f'{self.url}/{organization.uuid} /'
        data = {
            'name': 'Test name'
        }
        await self.make_patch(url, data, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)

    async def test_organization_update_422_2(self, organization):
        """Test organization update Unprocessable content."""
        url = f'{self.url}/{organization.uuid}/'
        data = {
            'phones': []
        }
        response = await self.make_patch(url, data, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
        assert response['detail'][0]['message'] == 'Organization should have at least one phone number'
