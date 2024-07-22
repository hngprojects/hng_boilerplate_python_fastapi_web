import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from api.v1.models.blog import Blog
from api.db.database import get_db

client = TestClient(app)


@pytest.fixture
def db_session_mock():
    return MagicMock()


@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    yield
    app.dependency_overrides[get_db] = None


def test_successful_retrieval_of_paginated_blog_posts(db_session_mock):
    blog1 = Blog(
        id=1,
        title="My First Blog",
        excerpt="This is an excerpt from my first blog.",
        content="Content of the first blog",
        image_url="https://example.com/image1.jpg",
        tags=["python", "coding"],
    )
    blog2 = Blog(
        id=2,
        title="My Second Blog",
        excerpt="This is an excerpt from my second blog.",
        content="Content of the second blog",
        image_url="https://example.com/image2.jpg",
        tags=["django", "web"],
    )

    db_session_mock.query().filter().order_by().offset().limit().all.return_value = [
        blog1
    ]
    db_session_mock.query().filter().order_by().count.return_value = 2

    response = client.get("/api/v1/blogs?page=1&page_size=1")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["next"] == "/api/v1/blogs?page=2&page_size=1"
    assert data["previous"] is None
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "My First Blog"


def test_no_blog_posts_present(db_session_mock):
    db_session_mock.query().filter().order_by().offset().limit().all.return_value = []
    db_session_mock.query().filter().order_by().count.return_value = 0

    response = client.get("/api/v1/blogs?page=1&page_size=10")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["next"] is None
    assert data["previous"] is None
    assert len(data["results"]) == 0


def test_internal_server_error(mocker):
    mocker.patch(
        "api.v1.routes.blog.list_blog", side_effect=Exception("Test exception")
    )

    response = client.get("/api/v1/blogs?page=1&page_size=10")

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Internal server error."


def test_invalid_page_or_page_size_parameters():
    # Test invalid page parameter
    response = client.get("/api/v1/blogs?page=-1&page_size=10")
    assert response.status_code == 422

    # Test invalid page_size parameter
    response = client.get("/api/v1/blogs?page=1&page_size=-1")
    assert response.status_code == 422

    # Test non-integer page parameter
    response = client.get("/api/v1/blogs?page=abc&page_size=10")
    assert response.status_code == 422


def test_invalid_method():
    response = client.post("/api/v1/blogs")

    assert response.status_code == 405
    data = response.json()
    assert data["detail"] == "Method Not Allowed"


def test_soft_deleted_blog_post_access_control(db_session_mock):
    soft_deleted_blog = Blog(
        id=1,
        title="Soft Deleted Blog",
        excerpt="This is an excerpt from a soft deleted blog.",
        content="Content of the soft deleted blog",
        image_url="https://example.com/image1.jpg",
        tags=["softdeleted"],
        is_deleted=True,
    )
    db_session_mock.query().filter().order_by().offset().limit().all.return_value = []
    db_session_mock.query().filter().order_by().count.return_value = 0

    response = client.get("/api/v1/blogs?page=1&page_size=10")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["next"] is None
    assert data["previous"] is None
    assert len(data["results"]) == 0
