import uuid

from starlette import status

from src.base.base_test import BaseTestCase


class TestOrganizationDetailCase(BaseTestCase):
    """Organization detail test suite."""
    url = '/organizations'

    async def test_organization_detail(self, organization, building, activity1, activity11, activity111):
        """Test organization detail."""
        url = f'{self.url}/{organization.uuid}/'
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
                                    'uuid': str(activity111.uuid),
                                    'name': activity111.name,
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

    async def test_organization_detail_401(self, organization):
        """Test organization detail Unauthorized."""
        url = f'{self.url}/{organization.uuid}/'
        await self.make_get(url, status_code=status.HTTP_401_UNAUTHORIZED, send_auth_token=False)

    async def test_organization_detail_404(self, organization):
        """Test organization detail Not found."""
        url = f'{self.url}/{uuid.uuid4()}/'
        await self.make_get(url, status_code=status.HTTP_404_NOT_FOUND)

    async def test_organization_detail_405(self, organization):
        """Test organization detail Method not allowed."""
        url = f'{self.url}/{organization.uuid}/'
        await self.make_put(url, {}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    async def test_organization_detail_422(self, organization):
        """Test organization detail Unprocessable content."""
        url = f'{self.url}/{organization.uuid} /'
        await self.make_get(url, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
