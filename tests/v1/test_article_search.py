import time
import pytest
from main import app
from api.core import responses
from api.db.database import Base, get_db
from api.v1.models.article import Article
from fastapi.testclient import TestClient
from tests.database import TestingSessionLocal, engine


# Override the get_db dependency to use the in-memory database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


payload = [
    {"title": "Test Article 1", "content": "Content for test article 1"},
    {"title": "Test Article 2", "content": "Content for test article 2"},
    {"title": "Another Test Article", "content": "Content for test article 2"},
]


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    # Create test data
    db = TestingSessionLocal()
    db.add_all([
        Article(title=data["title"], content=data["content"])
        for data in payload
    ])
    db.commit()
    db.close()

    yield

    # Drop the database tables after the tests
    Base.metadata.drop_all(bind=engine)


def test_rate_limiting():
    title = "Test Article"
    for _ in range(2):
        response = client.get(f"/api/v1/topics/search?title={title}")
        assert response.status_code == 200

    # Third request should be rate-limited
    response = client.get(f"/api/v1/topics/search?title={title}")
    assert response.status_code == 429
    assert response.json() == {
        "message": responses.TOO_MANY_REQUEST,
        "success": False,
        "status_code": 429
    }

    # Wait for rate limit period to reset
    time.sleep(10)
    response = client.get(f"/api/v1/topics/search?title={title}")
    assert response.status_code == 200


def test_query_param_response():
    title = "Test Article 1"
    response = client.get(f"/api/v1/topics/search?title={title}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Articles found"
    assert data["status_code"] == 200
    assert "topics" in data
    assert len(data["topics"]) == 1
    article = data["topics"][0]
    assert article["title"] == payload[0].get("title")


def test_no_article_found():
    title = "Nonexistent Article"
    response = client.get(f"/api/v1/topics/search?title={title}")
    assert response.status_code == 404
    data = response.json()
    assert data == {
        "message": responses.NOT_FOUND,
        "success": False,
        "status_code": 404
    }
