from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from src.config.settings import project_config


class BaseAuth(HTTPBearer):
    """Base auth class."""

    async def __call__(
            self, request: Request
    ) -> HTTPAuthorizationCredentials:
        authorization = request.headers.get('Authorization')
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization: Bearer token not specified"
            )
        scheme, credentials = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong authorization schema'
            )
        if not credentials or credentials != project_config.app.STATIC_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong token"
            )
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)
