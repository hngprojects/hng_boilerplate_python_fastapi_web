#!/usr/bin/env python3

"""2FA endpoint implementation"""

import json
from typing import Annotated, List
from fastapi.responses import StreamingResponse

import pyotp
import io
from urllib.parse import unquote
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm.session import Session

from api.db.database import get_db
from api.utils.dependencies import get_current_user
from api.utils.password_auth import validate_password
from api.utils.two_fa import generate_backup_codes, generate_qr_code, hash_backup_codes, verify_backup_codes
from api.v1.models.user import User
from api.v1.schemas.two_fa import (TwoFactorData, TwoFactorDisableRequest,
                                   TwoFactorEnableRequest, TwoFactorRecoveryRequest,
                                   TwoFactorResponse, TwoFactorVerifRequest,
                                   TwoFactorVerifResponse
                                   )

two_fa = APIRouter(prefix="/2fa", tags=["2fa"])


@two_fa.post("/enable", response_model=TwoFactorResponse)
async def enable_2fa(
    current_user: Annotated[User, Depends(get_current_user)],
    request: TwoFactorEnableRequest,
    db: Session = Depends(get_db)
):
    """Enable 2FA for user account"""
    if not validate_password(
        request.password,
            current_user.password.encode("utf-8")
    ):
        raise HTTPException(status_code=400, detail="Invalid password")

    secret = pyotp.random_base32()
    current_user.secret_key = secret

    db.commit()

    totp = pyotp.TOTP(secret)
    qr_code_url = totp.provisioning_uri(
        name=str(current_user.username),
        issuer_name="FastAPI boilerplate",
    )

    return TwoFactorResponse(
        status_code=200,
        message="2FA enabled successfully",
        data=TwoFactorData(
            secret_key=secret,
            qr_code_url=qr_code_url,
            backup_codes=None
        )
    )


@two_fa.post("/verify", response_model=TwoFactorVerifResponse)
def verify_2fa(
    user: Annotated[User, Depends(get_current_user)],
    request: TwoFactorVerifRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """Implements the verification endpoint for two fa"""
    backup_codes: List[str] | None = None
    totp = pyotp.TOTP(str(user.secret_key))
    totp_verified = False

    if (bool(user.secret_key) and not
            bool(user.is_2fa_enabled) and totp.verify(request.totp_code)):
        user.is_2fa_enabled = True
        backup_codes = generate_backup_codes()
        user.backup_codes = json.dumps(hash_backup_codes(
            backup_codes=backup_codes
        ))
        totp_verified = True
        db.commit()

    if (bool(user.is_2fa_enabled) and (totp_verified or totp.
                                       verify(request.totp_code))):
        msg = "2FA verified"
        if totp_verified:
            msg += " and enabled"
        return TwoFactorVerifResponse(
            status_code=200,
            message=msg,
            data=TwoFactorData(
                backup_codes=backup_codes,
                secret_key=None,
                qr_code_url=None
            ))
    raise HTTPException(status_code=400, detail="Invalid Requests")


@two_fa.post("/disable", response_model=TwoFactorResponse)
def disable_2fa(
    user: Annotated[User, Depends(get_current_user)],
    request: TwoFactorDisableRequest,
    db: Annotated[User, Depends(get_db)]
):
    """Disable Two Fa Verification"""
    if not bool(user.is_2fa_enabled) or not validate_password(
        request.current_password,
            user.password.encode("utf-8")
    ):
        raise HTTPException(status_code=400, detail="Invalid request")

    totp = pyotp.TOTP(str(user.secret_key))

    if totp.verify(request.totp_code):
        user.is_2fa_enabled = False
        user.secret_key = None
        user.backup_codes = None
        db.commit()
        return TwoFactorResponse(
            message="2fa has been disabled",
            status_code=200,
            data=TwoFactorData(
                qr_code_url=None,
                backup_codes=None,
                secret_key=None
            )
        )
    raise HTTPException(status_code=400, detail="Invalid request")


@two_fa.post("/backup_codes", response_model=TwoFactorResponse)
def generate_user_backup_codes(
    user: Annotated[User, Depends(get_current_user)],
    request: TwoFactorDisableRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """Generate New Backup Code for the current logged in user"""
    if not bool(user.is_2fa_enabled) and validate_password(
            request.current_password, user.password.encode("utf-8")
    ):
        raise HTTPException(status_code=400, detail="Invalid request")

    totp = pyotp.TOTP(str(user.secret_key))
    if totp.verify(request.totp_code):
        backup_codes = generate_backup_codes()
        user.backup_codes = json.dumps(hash_backup_codes(backup_codes))
        db.commit()
        return TwoFactorResponse(
            status_code=400,
            message="New backup codes generated",
            data=TwoFactorData(
                qr_code_url=None,
                secret_key=None,
                backup_codes=backup_codes)
        )
    raise HTTPException(status_code=400, detail="Invalid request")


@two_fa.post("/recover", response_model=TwoFactorResponse)
def recover_two_fa(
    user: Annotated[User, Depends(get_current_user)],
    request: TwoFactorRecoveryRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """Recover 2fa with backup_codes"""
    if verify_backup_codes(
        json.loads(str(user.backup_codes)),
        request.backup_codes
    ):
        backup_codes = generate_backup_codes()
        user.backup_codes = json.dumps(hash_backup_codes(backup_codes=backup_codes))
        secret_key = pyotp.random_base32()
        user.secret_key = secret_key
        db.commit()
        totp = pyotp.TOTP(secret_key)

        qr_code_url = totp.provisioning_uri(
            name=str(user.username),
            issuer_name="FastAPI boilerplate",
        )

        return TwoFactorResponse(
            status_code=200,
            message="Recovered Backup Code",
            data=TwoFactorData(
                qr_code_url=qr_code_url,
                secret_key=secret_key,
                backup_codes=backup_codes
            ))
    raise HTTPException(status_code=400, detail="2fa recovered successfully")


@two_fa.get("/v1/create-qr-code/")
async def create_qr_code(
    size: str = Query("150x150", regex=r"^\d+x\d+$"),
    data: str = Query(..., min_length=1)
):
    width, height = map(int, size.split('x'))
    decoded_data = unquote(data)

    qr_code_bytes = await generate_qr_code(decoded_data, (width, height))

    async def iterfile():
        yield qr_code_bytes

    return StreamingResponse(iterfile(), media_type="image/png")
