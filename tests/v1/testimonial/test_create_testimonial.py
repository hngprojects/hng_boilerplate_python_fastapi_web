import pytest
from tests.database import session, client
from api.v1.models import *  # noqa: F403

auth_token = None

payload = [
    {
        "content": "Testimonial 1",
        "ratings": 2.5,
        # expected
        "status_code": 201,
    },
    {
        "content": "Testimonial 2",
        "ratings": 3.5,
        # expected
        "status_code": 201,
    },
    { # missing content
        "ratings": 3.5,
        # expected
        "status_code": 422,
    },
    { # missing ratings
        "content": "Testimonial 2",
        # expected
        "status_code": 201,
    },
]

# before all tests generate an access token
@pytest.fixture(autouse=True)
def before_all(client: client, session: session) -> pytest.fixture:
    # create a user
    user = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser1",
            "password": "strin8Hsg263@",
            "first_name": "string",
            "last_name": "string",
            "email": "test@email.com",
        }
    )
    global auth_token
    auth_token = user.json()["data"]["access_token"]


def test_create_testimonial(client: client, session: session) -> pytest:
    status_code = payload[0].pop("status_code")
    res = client.post(
        "api/v1/testimonials",
        json=payload[0],
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert res.status_code == status_code
    testimonial_id = res.json()["data"]["id"]
    testimonial = session.query(Testimonial).get(testimonial_id)
    assert testimonial.content == payload[0]["content"]
    assert testimonial.ratings == payload[0]["ratings"]

def test_create_testimonial_unauthorized(client: client, session: session) -> pytest:
    status_code = 401
    res = client.post(
        "api/v1/testimonials",
        json=payload[1],
    )

    assert res.status_code == status_code

def test_create_testimonial_missing_content(client: client, session: session) -> pytest:
    status_code = payload[2].pop("status_code")
    res = client.post(
        "api/v1/testimonials",
        json=payload[2],
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert res.status_code == status_code

def test_create_testimonial_missing_ratings(client: client, session: session) -> pytest:
    status_code = payload[3].pop("status_code")
    res = client.post(
        "api/v1/testimonials",
        json=payload[3],
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert res.status_code == status_code
    testimonial_id = res.json()["data"]["id"]
    testimonial = session.query(Testimonial).get(testimonial_id)
    assert testimonial.ratings == 0