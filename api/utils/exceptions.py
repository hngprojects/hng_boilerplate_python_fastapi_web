from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from api.utils.json_response import JsonResponseDict

class CustomException(HTTPException):
    """
    Custom error handling
    """
    def __init__(self, status_code: int, detail: dict):
        super().__init__(status_code=status_code, detail=detail)
        self.message = detail.get("message")
        self.success = detail.get("success")
        self.status_code = detail.get("status_code")

async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "success": exc.success,
            "status_code": exc.status_code
        }
    )

class CustomWaitlistException(HTTPException):
    """
    Custom error handling
    """

    def __init__(self, detail: dict, status_code: int):
        super().__init__(detail=detail, status_code=status_code)
        self.message = detail.get("message")
        self.error = detail.get("error")
        self.status_code = status_code


def custom_waitlist_exception_handler(
    request: Request, exc: CustomWaitlistException
):
    content = {
        "message": exc.message,
        "error": exc.error,
        "status_code": exc.status_code,
    }
    return JsonResponseDict(**content)