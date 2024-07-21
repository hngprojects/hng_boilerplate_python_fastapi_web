#!/usr/bin/python3

"""Defines pydantic class for 2fa auth request and response"""

from typing import List
from pydantic import BaseModel


class TwoFactorEnableRequest(BaseModel):
    """Defines expected response for Twofactor Auth"""
    password:  str


class TwoFactorData(BaseModel):
    """Data field of 2fa response"""
    secret_key: str | None
    qr_code_url: str | None
    backup_codes: list[str] | None


class TwoFactorResponse(BaseModel):
    """Defines expected response for Twofactor Auth"""
    status_code: int
    message: str
    data: TwoFactorData


class TwoFactorVerifResponse(BaseModel):
    """Defines the response model for two factor verification
    """
    status_code: int
    message: str
    data: TwoFactorData | None


class TwoFactorVerifRequest(BaseModel):
    """Defines the request model for two factor verification
    """
    totp_code: str


class TwoFactorDisableRequest(TwoFactorVerifRequest):
    """Defines the request model for disable two factor verification
    """
    current_password: str


class TwoFactorRecoveryRequest(BaseModel):
    """Defines request model to recover 2fa"""
    backup_codes: List[str]
