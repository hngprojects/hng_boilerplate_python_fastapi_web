from math import ceil
from fastapi import status
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.utils import is_body_allowed_for_status_code

from api.core import responses


async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    headers = getattr(exc, "headers", None)
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)
    return JSONResponse(
        {
            "message": exc.detail,
            "success": False,
            "status_code": exc.status_code
        }, 
        status_code=exc.status_code, headers=headers
    )


async def rate_limit_callback(request: Request, response: Response, pexpire: int):
    """
    default callback when too many requests
    :param request:
    :param pexpire: The remaining milliseconds
    :param response:
    :return:
    """
    expire = ceil(pexpire / 1000)

    raise HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS,
        detail=responses.TOO_MANY_REQUEST,
        headers={"Retry-After": str(expire)},
    )