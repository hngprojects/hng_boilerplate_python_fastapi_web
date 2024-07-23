import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from decouple import config
from api.utils.auth import hash_password
from api.v1.models.user import User
from api.v1.models.oauth_token import OauthToken

SQLALCHEMY_DATABASE_URL = config('DB_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def session():
	db = TestingSessionLocal()
	yield db
	db.close()

def test_create_oauth_token_and_user(session: Session):
	"""
	Test to confirm the oauth_token creation and users relationship with oauth_tokens
	"""
	token = OauthToken(provider="google",
					sub="123456789098",
					access_token="fake access",
					refresh_token="fake refresh",
					expires_in=123456,
					id_token="some id_token")
	session.add(token)
	session.commit()

	user = User(
        username="johnson",
        email="johnson@gmail.com",
        password=hash_password('johnson'),
		first_name='johnson',
		last_name='oragui',
        is_active=True,
        is_admin=True,
		oauth_token_id=token.id
    )
	session.add(user)
	session.commit()
	session.refresh(user)
