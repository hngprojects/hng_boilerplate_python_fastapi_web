#!/usr/bin/env python3
""" This module contains the Json response class
"""
from enum import Enum
from json import dumps
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class RequestStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"


class JsonResponseDict(JSONResponse):

    def __init__(self, message: str, status: RequestStatus, data: dict | None = None, error: str = "", status_code=200):
        """initialize your response"""
        self.message = message
        self.data = data
        self.error = error
        self.status = status.value
        super().__init__(content=jsonable_encoder(self.response()), status_code=status_code)

    def __repr__(self):
        return {
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "status": self.status
        }

    def __str__(self):
        """string representation"""
        return dumps({
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "status": self.status
        })

    def response(self):
        """return a json response dictionary"""
        print(f"response: {format(self)}")
        if self.status == "success":
            return {
                "message": self.message,
                "data": self.data,
                "status": self.status
            }
        else:
            return {
                "message": self.message,
                "error": self.error,
                "status": self.status
            }

"""
usage:

return JsonResponseDict(
            message="Job creation successful",
            status=RequestStatus.SUCCESS,
            data={"job": new_job.to_dict()},
            status_code=status.HTTP_201_CREATED
        )
"""
