from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.services.user import UserService


from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
endpoint = "/api/v1/waitlist"


def test_delete_waitist_success(
    mock_db_session: Session,
    mock_user_service: UserService,
    mock_delete_waitlist_success,
    mock_admin_user: User,
):
    response = client.delete(
        f"{endpoint}/xxx-yyy-zzz",
        headers={"authorization": "Bearer 123"},
    )

    assert response.status_code == 204


def test_delete_waitlist_not_found(
    mock_db_session: Session,
    mock_user_service: UserService,
    mock_waitlist_not_found,
    mock_admin_user: User,
):
    response = client.delete(
        f"{endpoint}/xxx-yyy-zzz",
        headers={"authorization": "Bearer 123"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "status_code": 404,
        "status": False,
        "message": "No waitlisted user found with given id",
    }
