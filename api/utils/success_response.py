from typing import Optional, Dict, Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(
    status_code: int, message: str, data: Optional[Dict[str, Any]] = None
):
    """Returns a JSON response for success responses"""


def success_response(status_code: int, message: str, data: Optional[dict] = None):
    """Returns a JSON response for success responses"""

    response_data = {"status_code": status_code, "success": True, "message": message}

    if data is not None:
        response_data["data"] = data

    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(response_data)
    )
