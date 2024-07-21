import os
from decouple import config
from authlib.integrations.starlette_client import OAuth


# Define your JWT secret and algorithm
SECRET_KEY = os.getenv("SECRET_KEY", "MY SECRET KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")




oauth = OAuth()


CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
# Register Google OAuth2 client
oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url=CONF_URL,
    redirect_uri='http://127.0.0.1:7001/api/v1/auth/callback/google',
    client_kwargs={
        'scope': 'openid email profile',
        "access_type": "offline"}  # request for refresh token
)
