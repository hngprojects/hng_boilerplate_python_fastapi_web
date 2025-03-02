import json
import httpx
import datetime
from api.utils.settings import settings
from api.utils.logger import logger

TELEX_WEBHOOK_URL = settings.TELEX_WEBHOOK_URL

async def send_error_to_telex(request_method, request_url_path, exc):
    """Send error log to Telex"""
    if not TELEX_WEBHOOK_URL:
        logger.error("TELEX_WEBHOOK_URL is not set")
        return
    
    status_code = getattr(exc, "status_code", 500)
    error_data = {
        "status": "error",
        "username": "hng_boilerplate",
        "message": json.dumps(
            {
                "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                "event_name": "server_error",
                "request_method": request_method,
                "request_path": request_url_path,
                "status_code": status_code,
                "error_message": f"An unexpected error occurred: {exc}",
            },
            indent=4
        ),
        "event_name": "🚨 Internal Server Error",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(TELEX_WEBHOOK_URL, json=error_data)
            response.raise_for_status()
        except httpx.HTTPStatusError as http_err:
            logger.error(f"Telex API returned an error: {http_err.response.status_code} - {http_err.response.text}")
        except Exception as e:
            logger.exception(f"Failed to send error log to Telex: {e}")
