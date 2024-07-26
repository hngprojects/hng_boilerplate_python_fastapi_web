import pytest
from main import app
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from api.db.database import get_db
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.v1.services.user import user_service
from api.v1.models import User, Blog, BlogDislike

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    # db_session_mock.user_service = user_service
    # ``user_service mock`` above is replaced with ``mock_user_service`` 
    # fixture below, cos it's failing some tests in `test_superadmin`
    return db_session_mock


@pytest.fixture
def mock_user_service():
    with patch("api.v1.services.user.user_service", autospec=True) as user_service_mock:
        yield user_service_mock


# Test User
@pytest.fixture
def test_user():
    return User(
        id=str(uuid7()),
        username="testuser",
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
    )

@pytest.fixture()
def test_blog(test_user):
    return Blog(
        id=str(uuid7()),
        author_id=test_user.id,
        title="Blog Post 1",
        content="This is blog post number 1"
    )

@pytest.fixture()
def test_blog_dislike(test_user, test_blog):
    return BlogDislike(
            user_id=test_user.id,
            blog_id=test_blog.id,
        )

@pytest.fixture
def access_token_user1(test_user):
    return user_service.create_access_token(user_id=test_user.id)

def make_request(blog_id, token):
    return client.put(
        f"/api/v1/blogs/{blog_id}/dislike",
        headers={"Authorization": f"Bearer {token}"}
    )

# Test for successful dislike
def test_successful_dislike(
    mock_db_session, 
    test_user, 
    test_blog,
    access_token_user1,
):
    mock_user_service.get_current_user = test_user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_blog
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

    resp = make_request(test_blog.id, access_token_user1)
    assert resp.status_code == 200
    assert resp.json()['message'] == "Dislike recorded successfully."


# Test for double dislike
def test_double_dislike(
    mock_db_session, 
    test_user, 
    test_blog, 
    test_blog_dislike,
    access_token_user1,
):
    mock_user_service.get_current_user = test_user
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_blog
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = test_blog_dislike

    ### TEST ATTEMPT FOR MULTIPLE DISLIKING... ###
    resp = make_request(test_blog.id, access_token_user1)
    assert resp.status_code == 403
    assert resp.json()['message'] == "You have already disliked this blog post"

# Test for wrong blog id
def test_wrong_blog_id(
    mock_db_session, 
    test_user,
    access_token_user1,
):
    mock_user_service.get_current_user = test_user

    ### TEST REQUEST WITH WRONG blog_id ###
    ### using random uuid instead of blog1.id  ###
    resp = make_request(str(uuid7()), access_token_user1)
    assert resp.status_code == 404
    assert resp.json()['message'] == "Blog post not found"


# Test for unauthenticated user
def test_wrong_auth_token(
    mock_db_session,
    test_blog
):
    mock_user_service.get_current_user = None

    ### TEST ATTEMPT WITH INVALID AUTH... ###
    resp = make_request(test_blog.id, None)
    assert resp.status_code == 401
    assert resp.json()['message'] == 'Could not validate crenentials'


# import jwt
# import time
# import pytest
# from decouple import config
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from fastapi.testclient import TestClient

# from main import app
# from api.db.database import get_db
# from api.v1.models.user import User
# from api.v1.models.base import Base
# from api.v1.models.blog import Blog
# from api.v1.services.user import user_service
# from api.v1.models.blog_dislike import BlogDislike

# SQLALCHEMY_DATABASE_URL = config('DB_URL')

# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# TestingSessionLocal = sessionmaker(
#     autocommit=False, autoflush=False, bind=engine)

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)


# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# app.dependency_overrides[get_db] = override_get_db

# client = TestClient(app)


# @pytest.fixture(scope="module")
# def test_db():
#     db = TestingSessionLocal()
#     yield db
#     db.close()


# def create_user(db, username, commit=False):
#     # Add user to database
#     user = User(
#         username=username,
#         email=f"{username}@gmail.com",
#         password=user_service.hash_password('Testpassword@123'),
#         first_name='Test',
#         last_name='User',
#         is_active=True,
#     )
#     db.add(user)

#     if commit:
#         db.commit()
#         db.refresh(user)
#         assert isinstance(user, User)
#     return user


# def create_blog_post(db, author_id, commit=False):
#     # Add blog to database
#     blog = Blog(
#         author_id=author_id,
#         title="Blog Post 1",
#         content="This is blog post number 1"
#     )
#     db.add(blog)

#     if commit:
#         db.commit()
#         db.refresh(blog)
#     return blog


# def random_token(user_id: str):
#     payload = {"user_id": user_id, "expires": time.time() + 600}
#     return jwt.encode(payload, config('SECRET_KEY'), algorithm=config('ALGORITHM'))


# def test_failure_and_success_disliking(test_db):
#     """Test failue and success disliking"""
    
#     user1 = create_user(test_db, 'testuser1', True)
#     blog1 = create_blog_post(test_db, user1.id)
#     test_db.commit()

#     assert test_db.query(User).count() == 1
#     assert test_db.query(Blog).count() == 1

#     def make_request(blog_id, token):
#         return client.put(
#             f"/api/v1/blogs/{blog_id}/dislike",
#             headers={"Authorization": f"Bearer {token}"}
#         )


#     # DO LOG IN
#     login = client.post('/api/v1/auth/login', data={
#         "username": "testuser1",
#         "password": "Testpassword@123"
#     })
#     print(f"Login {login.json()}")
#     assert login.status_code == 200
#     access_token = login.json()['data']['access_token']


#     ### TEST REQUEST WITH WRONG blog_id ###
#     ### using user1.id instead of blog1.id  ###
#     print(access_token)
#     resp = make_request(user1.id, access_token)
#     assert resp.status_code == 404
#     assert resp.json()['message'] == "Blog post not found"


#     # DO SUCCESSFUL DISLIKING FROM Blog AUTHOR
#     resp = make_request(blog1.id, access_token)
#     assert resp.status_code == 200
#     assert resp.json()['message'] == "Dislike recorded successfully."
#     test_db.refresh(blog1)


#     # CHECK BlogDislike obj AND relationships
#     dislike = test_db.query(BlogDislike).filter_by(user_id=user1.id, blog_id=blog1.id).first()
#     assert dislike
#     assert len(user1.blog_dislikes) == 1
#     assert len(blog1.dislikes) == 1
#     assert user1.blog_dislikes == [dislike]
#     assert blog1.dislikes == [dislike]


#     ### TEST ATTEMPT FOR MULTIPLE DISLIKING... ###
#     resp = make_request(blog1.id, access_token)
#     print(f"Unauth {resp.json()}")
#     assert resp.status_code == 403
#     assert resp.json()['message'] == "You have already disliked this blog post"


#     ### TEST ATTEMPT WITH INVALID AUTH... ###
#     resp = make_request(blog1.id, random_token("gdhdhdjj366448jagss55333"))
#     print(f"Unauth {resp.json()}")
#     assert resp.status_code == 401
#     assert resp.json()['message'] == "Could not validate credentials"


# if __name__ == "__main__":
#     pytest.main()
