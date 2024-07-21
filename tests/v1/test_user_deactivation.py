from api.utils.auth import hash_password
from api.v1.models.user import User


def test_user_deactivation(session, client):
    '''Test for user deactivation'''

    user = User(
        username="testuser",
        email="testuser@gmail.com",
        password=hash_password("testpassword"),
        is_active=True,
        is_admin=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)


    login =  client.post('/api/v1/auth/login', json={
        "username": "testuser",
        "password": "testpassword"
    })
    access_token = login.json()['access_token']


    missing_field = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account"
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert missing_field.status_code == 422


    confirmation_false = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account",
        "confirmation": False
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert confirmation_false.status_code == 400


    unauthorized = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account",
        "confirmation": True
    })
    assert unauthorized.status_code == 401


    success_deactivation = client.patch('/api/v1/users/accounts/deactivate', json={
        "reason": "No longer need the account",
        "confirmation": True
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert success_deactivation.status_code == 200
