from typing import Optional
from fastapi.responses import JSONResponse


def success_response(status_code: int, message: str, data: Optional[dict] = None):
    '''Returns a JSON response for success responses'''

    response_data = {
        "status_code": status_code,
        "message": message
    }

    if data:
        response_data['data'] = data

    return JSONResponse(
        status_code=status_code,
        content=response_data
    )
