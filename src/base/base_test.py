import json
from typing import Any

from httpx import ASGITransport, AsyncClient
from starlette import status

from src.config.settings import project_config
from src.main import app


class BaseTestCase:
    """Base class for testing the project."""
    base_url = 'http://test/api'
    token: str = project_config.app.STATIC_TOKEN
    transport = ASGITransport(app=app)

    async def _make_request(
            self,
            method: str,
            url: str,
            data: object = None,
            status_code: int = status.HTTP_200_OK,
            headers: dict = None,
            send_auth_token: bool = True
    ) -> dict | None:
        """Method for request with authorization."""
        async with AsyncClient(transport=self.transport, base_url=self.base_url, follow_redirects=True) as client:
            url = f'{self.base_url}{url}'

            headers_to_send = {}
            if send_auth_token:
                headers_to_send = {
                    'Authorization': f'Bearer {self.token}', 'content-type': 'application/json'
                }
            if headers is not None:
                headers_to_send.update(headers)
            client.headers = headers_to_send

            request_data = None
            if data and method.lower() != 'get':
                request_data = json.dumps(data)

            response = await client.request(method, url, content=request_data, follow_redirects=True, params=data)
            assert response is not None
            assert response.status_code == status_code, f'status: {response.status_code}, response: {response.text}'

            if method != 'DELETE' and response.status_code != status.HTTP_204_NO_CONTENT:
                return response.json()

    async def make_post(
            self,
            url: str,
            data: Any = None,
            status_code: int = status.HTTP_200_OK,
            headers: dict = None,
            send_auth_token: bool = True
    ) -> dict:
        """Make post method."""
        if data is None:
            data = {}
        return await self._make_request('POST', url, data, status_code, headers, send_auth_token)

    async def make_get(
            self,
            url: str,
            params: dict = None,
            status_code: int = status.HTTP_200_OK,
            headers: dict = None,
            send_auth_token: bool = True
    ) -> dict:
        """Make get method."""
        return await self._make_request('GET', url, params, status_code, headers, send_auth_token)

    async def make_patch(
            self,
            url: str,
            data: dict,
            status_code: int = status.HTTP_200_OK,
            headers: dict = None,
            send_auth_token: bool = True
    ) -> dict:
        """Make patch method."""
        return await self._make_request('PATCH', url, data, status_code, headers, send_auth_token)

    async def make_put(
            self,
            url: str,
            data: dict,
            status_code: int = status.HTTP_200_OK,
            headers: dict = None,
            send_auth_token: bool = True
    ) -> dict:
        """Make put method."""
        return await self._make_request('PUT', url, data, status_code, headers, send_auth_token)

    async def make_delete(
            self,
            url: str,
            data: dict = None,
            status_code: int = status.HTTP_204_NO_CONTENT,
            headers: dict = None,
            send_auth_token: bool = True
    ) -> None:
        """Make delete method."""
        return await self._make_request('DELETE', url, data, status_code, headers, send_auth_token)
