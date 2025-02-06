import dns.resolver
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, StringConstraints, model_validator
from email_validator import validate_email, EmailNotValidError

def validate_mx_record(domain: str):
    """
    Validate mx records for email
    """
    try:
        # Try to resolve the MX record for the domain
        mx_records = dns.resolver.resolve(domain, 'MX')
        print('mx_records: ', mx_records.response)
        return True if mx_records else False
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except Exception:
        return False


# Pydantic models for request and response
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: str = None


class TokenRequest(BaseModel):
    email: Optional[EmailStr] = None
    token: Annotated[
        str,
        StringConstraints(
            max_length=6,
            min_length=6,
            strip_whitespace=True
        )
    ]

    @model_validator(mode='before')
    @classmethod
    def validate_email(cls, values: dict):
        """
        Validate email
        """
        email = values.get("email")
        try:
            email = validate_email(email, check_deliverability=True)
            if email.domain.count(".com") > 1:
                raise EmailNotValidError("Email address contains multiple '.com' endings.")
            if not validate_mx_record(email.domain):
                raise ValueError('Email is invalid')
        except EmailNotValidError as exc:
            raise ValueError(exc) from exc
        except Exception as exc:
            raise ValueError(exc) from exc
        return values


class OAuthToken(BaseModel):
    access_token: str
