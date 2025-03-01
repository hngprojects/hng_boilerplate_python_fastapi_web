import requests

from fastapi import Request

from api.v1.schemas.session import SessionCreate
from api.utils.client_helpers import get_ip_address


def get_ip_location(ip):
    """ Get IP location.
    
    Args:
        ip (str): IP address
    """
    country = region = "Unknown"
    
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json/", timeout=10)
        if response.status_code != 200:
            return f"{region}, {country}"
        data = response.json()
        region = data.get("region", "Unknown")
        country = data.get("country", "Unknown")
    except Exception as e:
        return f"{region}, {country}"
    return f"{region}, {country}"


def get_session_schema_data(request: Request, refresh_token: str = "", expires_at: str = ""):
    """Get session schema data.
    
    Args:
        request (Request): Request object
        refresh_token (str): Refresh token
        expires_at (str): Expiry date
    """
    ip = get_ip_address(request)
    user_agent= request.headers.get("User-Agent")
    return SessionCreate(
        ip_address=ip,
        location=get_ip_location(ip),
        device=user_agent,
        is_revoked=False,
        refresh_token=refresh_token,
        expires_at=expires_at
    )
