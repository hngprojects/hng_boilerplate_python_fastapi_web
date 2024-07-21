#!/usr/bin/env python3
"""
Handles 400, 401 and 500 HTTP errors
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Type
from fastapi.exceptions import RequestValidationError


class ErrorResponse(BaseModel):
    status: str
    message: str
    status_code: int

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "Unauthorized" if exc.status_code == 401 else "Internal Server Error",
            "message": "Unauthorized. Please log in." if exc.status_code == 401 else "Internal Server Error. Please try again later.",
            "status_code": exc.status_code
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "status": "Bad Request",
            "message": "Please check the submitted data",
            "status_code": 400
        }
    )

async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "status": "Internal Server Error",
            "message": "Internal Server Error. Please try again later.",
            "status_code": 500
        }
    )
