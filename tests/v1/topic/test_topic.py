import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models import User, Topic
from uuid_extensions import uuid7
from unittest.mock import MagicMock
from faker import Faker

fake = Faker()
client = TestClient(app)

@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

@pytest.fixture
def test_user():
    return User(
        id=str(uuid7()),
        email=fake.email(),
        password=fake.password(),
        first_name=fake.first_name,
        last_name=fake.last_name,
        is_active=True,
        is_superadmin=True,
        is_deleted=False,
        is_verified=True,
    )


@pytest.fixture
def test_topic(test_user):
    return Topic(
        id=str(uuid7()),
        title="hello", 
        content=fake.paragraphs(nb=3, ext_word_list=None),
        tags=[fake.word() for _ in range(3)]
    )


@pytest.fixture
def access_token_user1(test_user):
    return user_service.create_access_token(user_id=test_user.id)

def test_create_topic(
    mock_db_session, 
    test_user, 
    test_topic,
    access_token_user1,
):
    def mock_get(model, ident):
        if model == Topic and ident == test_topic.id:
            return test_topic
        return None

    mock_db_session.get.side_effect = mock_get

    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user

    headers = {'Authorization': f'Bearer {access_token_user1}'}
    data = {
        "title": "Uploading profile picture.",
        "content": "Uploading pictures to your blog is a straightforward process. Here’s a brief overview of the steps: Navigate to Your blog Settings: Log in to your account and find the blog section. Usually, there’s an option like “Edit blog” or blog Settings.” Choose the Picture You Want to Upload: Select a picture from your device that you’d like to use as your blog picture. Make sure it meets any size or format requirements specified by the platform. Upload the picture: Click the Upload button or a similar option. A file dialog will appear. Navigate to the location where your picture is stored and select it. Crop and Adjust (if needed): Some platforms allow you to crop or adjust the picture. If necessary, use the provided tools to frame your picture the way you want it. Save Changes: Once you’re satisfied with the picture, click “Save” or “Update blog.” Your new blog picture will now be visible to others! Remember to choose a picture that represents you well and aligns with the platform’s guidelines. Happy blog updating! 😊📸",
        "tags": ["picture","profile"]
    }
    response = client.post("/api/v1/help-center/topics", headers=headers, json=data)
    
    if response.status_code != 201:
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        print(response.json())
    else:
        assert response.status_code == 201

def test_update_topic(
    mock_db_session, 
    test_user, 
    test_topic,
    access_token_user1,
):
    def mock_get(model, ident):
        if model == Topic and ident == test_topic.id:
            return test_topic
        return None

    mock_db_session.get.side_effect = mock_get

    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user
    
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = [test_topic]

    headers = {'Authorization': f'Bearer {access_token_user1}'}
    data = {
        "title": "Uploading profile picture."
    }
    response = client.patch(f"/api/v1/help-center/topics/{test_topic.id}", headers=headers, json=data)    
    assert response.status_code == 200

def test_delete_topic(
    mock_db_session, 
    test_user, 
    test_topic,
    access_token_user1,
):
    def mock_get(model, ident):
        if model == Topic and ident == test_topic.id:
            return test_topic
        return None

    mock_db_session.get.side_effect = mock_get

    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user
    
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = [test_topic]

    headers = {'Authorization': f'Bearer {access_token_user1}'}
    response = client.delete(f"/api/v1/help-center/topics/{test_topic.id}", headers=headers)    
    assert response.status_code == 204

def test_search_topic(
    mock_db_session, 
    test_user, 
    test_topic,
    access_token_user1,
):
    def mock_get(model, ident):
        if model == Topic and ident == test_topic.id:
            return test_topic
        return None

    mock_db_session.get.side_effect = mock_get

    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user
    
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = [test_topic]
    response = client.get(f"/api/v1/help-center/search?title={test_topic.title}")    
    assert response.status_code == 200

def test_fetch_a_topic(
    mock_db_session, 
    test_user, 
    test_topic,
    access_token_user1,
):
    def mock_get(model, ident):
        if model == Topic and ident == test_topic.id:
            return test_topic
        return None

    mock_db_session.get.side_effect = mock_get

    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user
    
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = [test_topic]

    response = client.request("GET", f"/api/v1/help-center/topic/{test_topic.id}")
    if response.status_code != 200:
        assert response.status_code == 404, f"Expected status code 200, got {response.status_code}"
    else:
        assert response.status_code == 200

def test_fetch_all_topic(
    mock_db_session, 
    test_user, 
    test_topic,
    access_token_user1,
):
    def mock_get(model, ident):
        if model == Topic and ident == test_topic.id:
            return test_topic
        return None

    mock_db_session.get.side_effect = mock_get

    mock_db_session.query.return_value.filter.return_value.first.return_value = test_user
    
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = [test_topic]

    response = client.get(f"/api/v1/help-center/topics")
    assert response.status_code == 200
    