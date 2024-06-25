from fastapi import status
from fastapi.exceptions import HTTPException

def is_empty_string(string: str) -> bool:
    if len(string.strip()) == 0:
        return True

    return False

class EmptyStringException(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=None,
        )