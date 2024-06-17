"""utility functions"""
import os
import logging
from fastapi.responses import JSONResponse
from fastapi import status
from json import dumps
from datetime import date
from fastapi.encoders import jsonable_encoder


if os.path.isdir('logs') is False:
    os.mkdir('logs')


logging.basicConfig(
    filename=f'logs/server_logs_{date.today().strftime("%Y_%m_%d")}.log',
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class JsonResponse(JSONResponse):

    def __init__(self, message: str, data: dict | None = None, error: str = None, status_code=200):
        """initialize your response"""
        self.message = message
        self.data = data
        self.error = error
        super().__init__(content=jsonable_encoder(self.response()), status_code=status_code)

    def __repr__(self):
        return {
            "message": self.message,
            "data": self.data,
            "error": self.error,
        }

    def __str__(self):
        """string representation"""
        return dumps({
            "message": self.message,
            "data": self.data,
            "error": self.error,
        })

    def response(self):
        """return a json response dictionary"""
        print(f"response: {format(self)}")
        if self.error is None:
            return {
                "message": self.message,
                "data": self.data,
            }
        else:
            return {
                "message": self.message,
                "error": self.error,
            }


def internal_server_error():
    """standard response for internal server error"""
    return JsonResponse(
        message="Sorry an error occurred while processing your request.",
        error="Internal Server Error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
