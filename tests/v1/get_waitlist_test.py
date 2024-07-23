def test_retrieve_waitlist_users_as_admin(self, mocker):
    from api.v1.models.user import User, WaitlistUser
    from api.v1.schemas.waitlist import WaitlistUserResponse
    from api.utils.dependencies import get_current_user
    from api.v1.routes.waitlist import get_waitlist_users
    from api.db.database import get_db
    from fastapi import HTTPException, status
    from sqlalchemy.orm import Session

    # Mocking dependencies
    mock_db = mocker.Mock(spec=Session)
    mock_user = mocker.Mock(spec=User)
    mock_user.is_admin = True

    mocker.patch('api.utils.dependencies.get_current_user', return_value=mock_user)
    mocker.patch('api.v1.routes.waitlist.get_user_by_current', return_value=mock_user)
    mocker.patch('api.db.database.get_db', return_value=mock_db)

    # Mocking database query
    waitlist_users = [WaitlistUser(email="test1@example.com", full_name="Test User 1"),
                        WaitlistUser(email="test2@example.com", full_name="Test User 2")]
    mock_db.query.return_value.all.return_value = waitlist_users

    response = get_waitlist_users(db=mock_db, current_user=mock_user)

    assert response == WaitlistUserResponse(
        message="Waitlist retrieved successfully",
        status_code=200,
        data=["test1@example.com", "test2@example.com"]
    )