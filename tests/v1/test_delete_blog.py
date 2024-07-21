import pytest
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app instance
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base, get_db
from api.v1.models.blog import Blog
from api.v1.schemas.blog import DeleteBlogResponseSchema
import uuid

from decouple import config

DB_TYPE = config("DB_TYPE")
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")
MYSQL_DRIVER = config("MYSQL_DRIVER")
DATABASE_URL = ""

# Create a test database and set up the TestClient
SQLALCHEMY_DATABASE_URL = f"{
    DB_TYPE}+{MYSQL_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Test Data Setup


def create_blog(id: str, is_deleted: bool):
    db = SessionLocal()
    blog = Blog(id=id, title="Test Blog", content="Content", image_url="http://example.com/image.jpg",
                tags=["test"], excerpt="Excerpt", is_deleted=is_deleted)
    db.add(blog)
    db.commit()
    db.close()


def test_delete_blog_valid_uuid():
    blog_id = str(uuid.uuid4())
    create_blog(blog_id, False)
    response = client.delete(f"/api/v1/blogs/{blog_id}")
    assert response.status_code == 202
    assert response.json() == {
        "message": "Blog successfully deleted", "status_code": 202}


def test_delete_blog_already_deleted():
    blog_id = str(uuid.uuid4())
    create_blog(blog_id, True)
    response = client.delete(f"/api/v1/blogs/{blog_id}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Blog not active"}


def test_delete_blog_not_exist():
    invalid_id = str(uuid.uuid4())
    response = client.delete(f"/api/v1/blogs/{invalid_id}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Blog with the given Id does not exist"}


def test_delete_blog_invalid_uuid():
    invalid_id = "invalid-uuid"
    response = client.delete(f"/api/v1/blogs/{invalid_id}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid UUID format"}


def test_delete_blog_server_error(monkeypatch):
    def mock_commit():
        raise Exception("Server error")

    monkeypatch.setattr("sqlalchemy.orm.session.Session.commit", mock_commit)
    blog_id = str(uuid.uuid4())
    create_blog(blog_id, False)
    response = client.delete(f"/api/v1/blogs/{blog_id}")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
