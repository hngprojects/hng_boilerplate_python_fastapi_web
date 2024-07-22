#!/usr/bin/python3

"""Defines utils for the 2fa endpoint"""


import asyncio
import io
from typing import List

import pyotp
import qrcode

from api.utils.auth import hash_password, verify_password
from api.utils.password_auth import validate_password


def generate_backup_codes(n=8):
    """Generate 8 word backup codes for secret recovery"""
    return [pyotp.random_base32()[:6] for _ in range(n)]


def hash_backup_codes(backup_codes: List[str]):
    """Hash the backup code"""
    return [hash_password(backup_code) for backup_code in backup_codes]


def verify_backup_codes(
        hashed_backup_codes: List[str],
        backup_codes:  List[str]
) -> bool:
    """Verify the backup code"""
    return any(
        validate_password(code, hash_code.encode("utf-8"))
        for hash_code, code in zip(hashed_backup_codes, backup_codes)
    )


async def generate_qr_code(data: str, size: tuple):
    loop = asyncio.get_event_loop()

    def _generate():
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize(size)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()

    return await loop.run_in_executor(None, _generate)


def verify_totp(secret_key: str, totp_code: str, window: int = 1) -> bool:
    """
    Verify a TOTP code against a secret key.

    Args:
        secret_key (str): The secret key used to generate the TOTP.
        totp_code (str): The TOTP code provided by the user.
        window (int, optional): The time window in which the TOTP is valid.
                                Defaults to 1, which is usually 30 seconds
                                before and after the current time.

    Returns:
        bool: True if the TOTP is valid, False otherwise.
    """
    if not secret_key or not totp_code:
        return False

    totp = pyotp.TOTP(secret_key)
    return totp.verify(totp_code, valid_window=window)
