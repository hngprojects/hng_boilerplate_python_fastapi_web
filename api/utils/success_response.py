from typing import Optional, Dict, Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(status_code: int, message: str, data: Optional[dict] = None):
    '''Returns a JSON response for success responses'''

    response_data = {
        "status_code": status_code,
        "success": True,
        "message": message
    }
    
    if data is not None:
        response_data["data"] = data

    return JSONResponse(status_code=status_code, content=jsonable_encoder(response_data))


def auth_response(status_code: int, message: str, access_token: str, data: Optional[dict] = None):
    '''Returns a JSON response for successful auth responses'''

    response_data = {
        "status_code": status_code,
        "message": message,
        "access_token": access_token
    }
    
    if data is not None:
        response_data["data"] = data

    return JSONResponse(status_code=status_code, content=jsonable_encoder(response_data))


def fail_response(status_code: int, message: str, data: Optional[dict] = None):
    '''Returns a JSON response for success responses'''

    response_data = {
        "status_code": status_code,
        "success": False,
        "message": message
    }
    
    if data is not None:
        response_data["data"] = data

    return JSONResponse(status_code=status_code, content=jsonable_encoder(response_data))