from uuid import UUID

from pydantic import BaseModel, ConfigDict
from starlette import status


class BaseSchema(BaseModel):
    """Base Schema."""
    model_config = ConfigDict(from_attributes=True)


class UUIDSchema(BaseModel):
    """uuid Schema."""
    uuid: UUID


class UUIDNameSchema(UUIDSchema):
    """uuid name Schema."""
    name: str


class ExceptionSchema(BaseModel):
    """Base Exception Schema."""
    detail: str


class ExceptionValidationFieldSchema(BaseModel):
    """Exception Validation Field Schema."""
    field: str = 'field name'
    message: str = 'message error'


class ExceptionValidationSchema(BaseModel):
    """Base Exception Validation Schema."""
    detail: list[ExceptionValidationFieldSchema]


class ResponseSchema:
    """Response Schema."""
    base = {
        status.HTTP_401_UNAUTHORIZED: {'model': ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {'model': ExceptionSchema},
        status.HTTP_405_METHOD_NOT_ALLOWED: {'model': ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {'model': ExceptionValidationSchema},
    }

    def get_base_statuses(self, exclude: list = None) -> dict:
        """Get base statuses."""
        if exclude is not None:
            return {k: v for k, v in self.base.items() if k not in exclude}
        return self.base

    def statuses(
            self,
            schema,
            response_status: int = status.HTTP_200_OK,
            statuses: list = None,
            exclude: list = None
    ) -> dict:
        """Get create statuses."""
        exception_schema = {'model': ExceptionSchema}
        if statuses is None:
            statuses = []
        get_status = {response_status: {'model': schema}}
        for status_ in statuses:
            get_status[status_] = exception_schema if status_ != status.HTTP_204_NO_CONTENT else {'model': None}
        return {**get_status, **self.get_base_statuses(exclude=exclude)}

    def __call__(
            self,
            schema=None,
            response_status: int = status.HTTP_200_OK,
            statuses: list = None,
            exclude: list = None
    ) -> dict:
        return self.statuses(schema=schema, response_status=response_status, statuses=statuses, exclude=exclude)


responses = ResponseSchema()
