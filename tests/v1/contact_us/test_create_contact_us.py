import pytest
from tests.database import session, client
from api.v1.models import *

# setup the test database
adabtingMapper = {
    "full_name": "full_name",
    "email": "email",
    "phone_number": "phone_number",
    "message": "message",
    "org_id": "org_id",
}

org_payload = [
    {
        "company_name": "Company 1",
        "company_email": "contact_us@com1.com",
        "industry": "Tech",
        "organization_type": "Tech",
        "country": "Nigeria",
        "state": "Lagos",
        "address": "1, Company Street",
    },
    {
        "company_name": "Company 2",
        "company_email": "contact_us@com2.com",
        "industry": "Tech",
        "organization_type": "Tech",
        "country": "Nigeria",
        "state": "Lagos",
        "address": "2, Company Street",
    },
]


# '{ "full_name": "John Doe","email": "john@gmail.com","phone_number": "Hello","message": "Hello, I am John Doe"}'
payload = [
    { # all fields are valid
        "full_name": "John Doe",
        "email": "john@gmail.com",
        "phone_number": "0123456789",
        "message": "Hello, I am John Doe",
        "status_code": 201, # will be stripped out later
    },
    { # all fields are valid
        "full_name": "Jane Doe",
        "email": "jane@gmail.com",
        "phone_number": "0123456789",
        "message": "Hi, I am Jane Doe",
        "status_code": 201, # will be stripped out later
    },
    { # missing phone_number field
        "full_name": "John Doe",
        "email": "john@gmail.com",
        "message": "Hello, I am John Doe",
        "status_code": 422, # will be stripped out later
    },
    { # missing message field
        "full_name": "John Doe",
        "email": "john@gmail.com",
        "phone_number": "0123456789",
        "status_code": 422, # will be stripped out later
    },
    { # missing full_name field
        "email": "jane@gmail.com",
        "phone_number": "0123456789",
        "message": "Hi, I am Jane Doe",
        "status_code": 422, # will be stripped out later
    },
    { # missing email field
        "full_name": "Jane Doe",
        "phone_number": "0123456789",
        "message": "Hi, I am Jane Doe",
        "status_code": 422, # will be stripped out later
    },
    { # invalid email field
        "full_name": "John Doe",
        "email": "john",
        "phone_number": "0123456789",
        "message": "Hello, I am John Doe",
        "status_code": 422, # will be stripped out later
    },
]


def get_orgs() -> list:
    orgs = []
    for org in org_payload:
        orgs.append(Organization(**org))
    return orgs

@pytest.fixture(autouse=True)
def setup_db(session: session) -> pytest.fixture:
    orgs = get_orgs()
    session.add_all(orgs)
    session.commit()
    for i, p in enumerate(payload):
        p["org_id"] = orgs[i%2].id

def test_create_new_contact_us_message(client: client, session: session) -> pytest:
    json_payload = payload[0]
    status_code = json_payload.pop("status_code")
    res = client.post("/api/v1/contact", json=json_payload)
    assert res.status_code == status_code
    if status_code == 201:
        data = res.json()
        contact_us_message = session.query(ContactUs).get(data["data"]["id"])  # noqa: F405
        assert getattr(contact_us_message, adabtingMapper["full_name"]) == json_payload["full_name"]
        assert getattr(contact_us_message, adabtingMapper["email"]) == json_payload["email"]
        assert getattr(contact_us_message, adabtingMapper["phone_number"]) == json_payload["phone_number"]
        assert getattr(contact_us_message, adabtingMapper["message"]) == json_payload["message"]

def test_create_new_contact_us_message_2(client: client, session: session) -> pytest:
    json_payload = payload[1]
    status_code = json_payload.pop("status_code")
    res = client.post("/api/v1/contact", json=json_payload)
    assert res.status_code == status_code
    if status_code == 201:
        data = res.json()
        contact_us_message = session.query(ContactUs).get(data["data"]["id"])  # noqa: F405
        assert getattr(contact_us_message, adabtingMapper["full_name"]) == json_payload["full_name"]
        assert getattr(contact_us_message, adabtingMapper["email"]) == json_payload["email"]
        assert getattr(contact_us_message, adabtingMapper["phone_number"]) == json_payload["phone_number"]
        assert getattr(contact_us_message, adabtingMapper["message"]) == json_payload["message"]

def test_create_new_contact_us_message_with_missing_phone_number_field(client: client, session: session) -> pytest:
    json_payload = payload[2]
    status_code = json_payload.pop("status_code")
    res = client.post("/api/v1/contact", json=json_payload)
    assert res.status_code == status_code

def test_create_new_contact_us_message_with_missing_message_field(client: client, session: session) -> pytest:
    json_payload = payload[3]
    status_code = json_payload.pop("status_code")
    res = client.post("/api/v1/contact", json=json_payload)
    assert res.status_code == status_code

def test_create_new_contact_us_message_with_missing_full_name_field(client: client, session: session) -> pytest:
    json_payload = payload[4]
    status_code = json_payload.pop("status_code")
    res = client.post("/api/v1/contact", json=json_payload)
    assert res.status_code == status_code

def test_create_new_contact_us_message_with_missing_email_field(client: client, session: session) -> pytest:
    json_payload = payload[5]
    status_code = json_payload.pop("status_code")
    res = client.post("/api/v1/contact", json=json_payload)
    assert res.status_code == status_code
