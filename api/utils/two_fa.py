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
