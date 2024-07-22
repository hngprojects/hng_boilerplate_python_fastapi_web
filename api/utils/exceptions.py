from fastapi import HTTPException, Request, Response
from fastapi.utils import is_body_allowed_for_status_code

from .json_response import JsonResponseDict


async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    headers = getattr(exc, "headers", None)
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)
    return JsonResponseDict(message=exc.detail, status_code=exc.status_code)
