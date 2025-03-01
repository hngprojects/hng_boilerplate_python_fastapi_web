import logging
from datetime import datetime
import user_agents
from user_agents.parsers import UserAgent
from fastapi import Request
from api.core.dependencies.email_sender import send_email
from api.v1.models import User
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_login_notification(user: User, request: Request):
    """
    Send a login notification email to the user.

    Args:
        user (User): The user who just logged in
        request (Request): The FastAPI request object
    """

    # Extract IP address from request headers
    ip_address = request.client.host

    if request.headers.get("x-forwarded-for"):
        ip_address = request.headers.get("x-forwarded-for").split(",")[0].strip()

    # Default location
    location = "Unknown Location"

    # Check if IP is local
    if not ip_address.startswith(("127.", "192.168.", "10.", "172.")):  # Ignore local IPs
        try:
            response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
            response.raise_for_status()  # Ensure response is successful (200 OK)
            geo_data = response.json()   # Convert response only if request didn't fail
            city = geo_data.get("city", "Unknown City")
            country = geo_data.get("country", "Unknown Country")
            location = f"{city}, {country}"
        except requests.RequestException as e:
            logger.error(f"Failed to fetch location for IP {ip_address}. Error: {str(e)}")
            location = "Unknown Location"  # Ensure a fallback value

    # Get user agent information
    user_agent_string = request.headers.get("user-agent", "")
    user_agent: UserAgent = user_agents.parse(user_agent_string)

    # Format device information
    device = f"{user_agent.device.family}"
    browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    os_info = f"{user_agent.os.family} {user_agent.os.version_string}"

    if device == "Other":
        device_info = f"{os_info} - {browser}"
    else:
        device_info = f"{device} ({os_info}) - {browser}"

    # Email links
    change_password_link = "https://anchor-python.teams.hng.tech/change-password"
    help_center_link = "https://anchor-python.teams.hng.tech/help-center"

    # Log the notification event
    logger.info(f"Sending login notification to {user.email} from {ip_address} ({location}) on {device_info}")

    # Send the notification email with error handling
    try:
        await send_email(
            recipient=user.email,
            template_name='login-notification.html',
            subject='New Login to Your Account',
            context={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'login_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'ip_address': ip_address,
                'location': location,
                'device': device_info,
                'change_password_link': change_password_link,
                'help_center_link': help_center_link,
                'current_year': datetime.now().year
            }
        )
        logger.info(f"Login notification sent successfully to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send login notification to {user.email}: {str(e)}")