from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, CompileError
from sqlalchemy.orm.exc import StaleDataError
from starlette import status


def get_error_message(err: IntegrityError, conflict: bool = False) -> str:
    """Get error message."""
    *_, error_msg = f'{err.orig}'.split(':')
    if conflict:
        *_, error_msg = f'{err.orig}'.split('\n')[0].split(':')
    error = error_msg.strip().replace(')', '').replace('(', '').replace('"', '')
    return error


def handle_error(error: IntegrityError | CompileError | StaleDataError):
    """Handle error message."""
    if isinstance(error, StaleDataError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    if isinstance(error, CompileError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{error}')
    error_text = get_error_message(error)
    sql_query_con = 'UPDATE' in f'{error}' or 'INSERT' in f'{error}'
    if 'not present in table' in error_text or ('FOREIGN KEY' in error_text and sql_query_con):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_text)
    error_text = get_error_message(error, True)
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_text)
