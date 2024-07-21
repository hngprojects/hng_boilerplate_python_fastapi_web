#!/usr/bin/env python3
""" This module contains the functions to hash and validate password
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """ generates a salted hashed password
    """
    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

def validate_password(password: str, hashed_password: bytes) -> bool:
    """ Validates a password
    """

    return bcrypt.checkpw(password.encode(), hashed_password)
