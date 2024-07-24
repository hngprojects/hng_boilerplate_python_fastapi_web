import jwt
import time
import pytest
# from uuid import UUID
from decouple import config
# from datetime import datetime
from sqlalchemy import create_engine
# from datetime import datetime, timezone
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from main import app
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.base import Base
from api.v1.models.blog import Blog
# from api.utils.auth import hash_password
from api.v1.services.user import user_service
from api.v1.models.blog_dislike import BlogDislike
# from api.v1.models.blog import Blog, LikesDislikes
# from api.v1.services.blog import likes_dislikes_service as dislike_service

SQLALCHEMY_DATABASE_URL = config('DB_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()


def create_user(db, username, commit=False):
    # Add user to database
    user = User(
        username=username,
        email=f"{username}@gmail.com",
        password=user_service.hash_password('Testpassword@123'),
        first_name='Test',
        last_name='User',
        is_active=True,
    )
    db.add(user)

    if commit:
        db.commit()
        db.refresh(user)
        assert isinstance(user, User)
    return user


def create_blog_post(db, author_id, commit=False):
    # Add blog to database
    blog = Blog(
        author_id=author_id,
        title="Blog Post 1",
        content="This is blog post number 1"
    )
    db.add(blog)

    if commit:
        db.commit()
        db.refresh(blog)
    return blog


def random_token(user_id: str):
    payload = {"user_id": user_id, "expires": time.time() + 600}
    return jwt.encode(payload, config('SECRET_KEY'), algorithm=config('ALGORITHM'))


def test_failure_and_success_disliking(test_db):
    """Test failue and success disliking"""
    if not test_db.query(User).count():
        user1 = create_user(test_db, 'testuser1', True)
        blog1 = create_blog_post(test_db, user1.id)
        test_db.commit()
    else:
        user1 = test_db.query(User).filter_by(username='testuser1').first()
        blog1 = test_db.query(Blog).filter_by(author_id=user1.id).first()

    assert test_db.query(User).count() == 1
    assert test_db.query(Blog).count() == 1

    def make_request(blog_id, token):
        return client.put(
            f"/api/v1/blogs/{blog_id}/dislike",
            headers={"Authorization": f"Bearer {token}"}
        )

    # DO LOG IN
    login = client.post('/api/v1/auth/login', data={
        "username": "testuser1",
        "password": "Testpassword@123"
    })
    print(f"Login {login.json()}")
    assert login.status_code == 200
    access_token = login.json()['data']['access_token']

    ### TEST REQUEST WITH WRONG blog_id ###
    ### using user1.id instead of blog1.id  ###
    print(access_token)
    resp = make_request(user1.id, access_token)
    print(f"Wrong blog {resp.json()}")
    assert resp.status_code == 404
    assert resp.json()['message'] == "Blog post not found"

    # DO SUCCESSFUL DISLIKING FROM Blog AUTHOR
    resp = make_request(blog1.id, access_token)
    assert resp.status_code == 200
    assert resp.json()['message'] == "Dislike recorded successfully."
    test_db.refresh(blog1)

    dislike = test_db.query(BlogDislike).filter_by(user_id=user1.id, blog_id=blog1.id).first()
    assert dislike

    ### TEST ATTEMPT FOR MULTIPLE DISLIKING... ###
    resp = make_request(blog1.id, access_token)
    print(f"Unauth {resp.json()}")
    assert resp.status_code == 403
    assert resp.json()['message'] == "You have already disliked this blog post"

    ### TEST ATTEMPT FOR MULTIPLE DISLIKING... ###
    resp = make_request(blog1.id, random_token("gdhdhdjj366448jagss55333"))
    print(f"Unauth {resp.json()}")
    # assert resp.status_code == 403
    assert resp.json()['message'] == "Could not validate credentials"



if __name__ == "__main__":
    pytest.main()
