import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import Mock, patch
from api.v1.routes.auth import auth
from api.v1.models.user import User
from api.v1.models.subscription import Subscription
from api.db.database import get_db
from api.utils.auth import hash_password, create_access_token
from api.v1.routes.subscription import send_cancellation_confirmation_notification
app = FastAPI()
app.include_router(auth)

# Mock database dependency
def override_get_db():
	db = Mock()
	try:
		yield db
	finally:
		db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def mock_db():
	return Mock()

@pytest.fixture
def mock_check_model_exists():
    def mock_check(subscription_id: str) -> bool:
        print(subscription_id)
        return subscription_id == "9f04dd70-0c0b-4c38-b323-f69888a70f46"
    return mock_check

app.dependency_overrides[send_cancellation_confirmation_notification] = mock_check_model_exists

@pytest.fixture(scope="module")
async def client():
	async with AsyncClient(app=app, base_url="http://test") as ac:
		yield ac


@pytest.mark.anyio
async def test_password_reset_email(client, mock_db):
	mock_user = User(
		  		id="3ef669a8-a197-45bd-9b0e-65d3cf13724e",
				email="testuser@cold.com",
			 	username="colduser",
				password=hash_password("fakehashedpassword")
			)
	mock_subscription = Subscription(id="9f04dd70-0c0b-4c38-b323-f69888a70f46", user=mock_user, plan="Premium", is_active=False)
	mock_db.query.return_value.filter.return_value.first.return_value = mock_subscription

	app.dependency_overrides[get_db] = lambda: mock_db
	access_token = create_access_token(data={"sub": str(mock_user.username)})
	
	response = await client.post(
		f"/api/v1/user/subscription/notification/cancellation/{mock_subscription.id}",
		headers={"Authorization": f"Bearer {access_token}"}
	)
	assert response.status_code == 404
			