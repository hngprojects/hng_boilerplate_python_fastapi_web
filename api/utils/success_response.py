from typing import Optional, Dict, Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(status_code: int, message: str, data: Optional[dict] = None):
    """Returns a JSON response for success responses"""

    response_data = {
        "status": "success",
        "status_code": status_code,
        "message": message,
        "data": data or {}  # Ensure data is always a dictionary
    }

    return JSONResponse(status_code=status_code, content=jsonable_encoder(response_data))


def auth_response(status_code: int, message: str, access_token: str, data: Optional[dict] = None):
    """Returns a JSON response for successful auth responses"""

    response_data = {
        "status": "success",
        "status_code": status_code,
        "message": message,
        "data": {
            "access_token": access_token,
            **(data or {})  # Merge additional data if provided
        }
    }

    return JSONResponse(status_code=status_code, content=jsonable_encoder(response_data))


def fail_response(status_code: int, message: str, data: Optional[dict] = None):
    """Returns a JSON response for failure responses"""

    response_data = {
        "status": "failure",
        "status_code": status_code,
        "message": message,
        "data": data or {}  # Ensure data is always a dictionary
    }

    return JSONResponse(status_code=status_code, content=jsonable_encoder(response_data))
