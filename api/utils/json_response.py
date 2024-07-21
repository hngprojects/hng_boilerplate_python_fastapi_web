#!/usr/bin/env python3
"""This module contains the Json response class"""

from json import dumps
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class JsonResponseDict(JSONResponse):
    def __init__(
        self, message: str, data: dict | None = None, error: str = "", status_code=200
    ):
        """Initialize your response"""
        self.message = message
        self.data = data
        self.error = error
        self.status_code = status_code  # Ensure this is set
        super().__init__(
            content=jsonable_encoder(self.response()), status_code=status_code
        )

    def __repr__(self):
        return {
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "status_code": self.status_code,
        }

    def __str__(self):
        """String representation"""
        return dumps(
            {
                "message": self.message,
                "data": self.data,
                "error": self.error,
                "status_code": self.status_code,
            }
        )

    def response(self):
        """Return a JSON response dictionary"""
        if self.status_code >= 300:
            return {
                "message": self.message,
                "error": self.error,
                "status_code": self.status_code,
            }
        else:
            return {
                "message": self.message,
                "data": self.data,
                "status_code": self.status_code,
            }
