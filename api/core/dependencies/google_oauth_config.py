from decouple import config
from authlib.integrations.starlette_client import OAuth


google_oauth = OAuth()


CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
# Register Google OAuth2 client
google_oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    server_metadata_url=CONF_URL,
    client_kwargs={
        "scope": "openid email profile",
        "access_type": "offline",
    },  # request for refresh token
)
