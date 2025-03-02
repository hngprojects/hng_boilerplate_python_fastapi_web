import httpx
from fastapi import Request, BackgroundTasks
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.schemas.session import SessionCreate
from api.v1.services.session import SessionService
from api.utils.client_helpers import get_ip_address


async def get_ip_location(ip):
    """ Get IP location.
    
    Args:
        ip (str): IP address
    """
    country = region = "Unknown"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://ipinfo.io/{ip}/json/", timeout=10)
            response.raise_for_status()
            data = response.json()
            region = data.get("region", "Unknown")
            country = data.get("country", "Unknown")
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
    except Exception as exc:
        print(f"An unexpected error occurred: {exc}")
    
    return f"{region}, {country}"
    
async def get_session_schema_data(request: Request, refresh_token: str = "", expires_at: str = ""):
    """Get session schema data.
    
    Args:
        request (Request): Request object
        refresh_token (str): Refresh token
        expires_at (str): Expiry date
    """
    ip = get_ip_address(request)
    return SessionCreate(
        ip_address=ip,
        location=await get_ip_location(ip),
        device=request.headers.get("User-Agent"),
        is_revoked=False,
        refresh_token=refresh_token,
        expires_at=expires_at
    )

async def create_session_for_user(
        request: Request,
        user_id: str,
        refresh_token: str = "",
        expires_at: str = "",
    ):
    """Create session for user.
    
    Args:
        request (Request): Request object
        db: Database session
        refresh_token (str): Refresh token
        expires_at (str): Expiry date
    """
    session_data: SessionCreate = await get_session_schema_data(
        request,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )
    db = next(get_db())
    session_service = SessionService(db)
    session_service.create(schema=session_data, user_id=user_id)
