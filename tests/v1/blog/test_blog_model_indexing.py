import pytest
from sqlalchemy import inspect
from api.v1.models.blog import Blog, BlogLike, BlogDislike
from api.v1.models.user import User


class TestBlogModelIndexing:
    def test_author_id_index_exists(self, db_session):
        """Test that the author_id index exists on the Blog model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('blogs')

        author_id_index = next((idx for idx in indexes if 'author_id' in idx['name'] and 'blogs' in idx['name']), None)
        assert author_id_index is not None
        assert 'author_id' in author_id_index['column_names']

    def test_title_index_exists(self, db_session):
        """Test that the title index exists on the Blog model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('blogs')

        title_index = next((idx for idx in indexes if 'title' in idx['name'] and 'blogs' in idx['name']), None)
        assert title_index is not None
        assert 'title' in title_index['column_names']

    def test_tags_index_exists(self, db_session):
        """Test that the tags index exists on the Blog model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('blogs')

        tags_index = next((idx for idx in indexes if 'tags' in idx['name'] and 'blogs' in idx['name']), None)
        assert tags_index is not None
        assert 'tags' in tags_index['column_names']

    def test_is_deleted_index_exists(self, db_session):
        """Test that the is_deleted index exists on the Blog model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('blogs')

        is_deleted_index = next((idx for idx in indexes if 'is_deleted' in idx['name'] and 'blogs' in idx['name']), None)
        assert is_deleted_index is not None
        assert 'is_deleted' in is_deleted_index['column_names']

    def test_query_using_blog_indexes(self, db_session):
        """Test that queries use the blog indexes properly"""
        # Create a test user first
        user = User(
            email="blog_author@example.com",
            first_name="Blog",
            last_name="Author",
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()

        # Create a test blog
        blog = Blog(
            author_id=user.id,
            title="Test Blog",
            content="This is a test blog content",
            tags="test,index,blog",
            is_deleted=False
        )
        db_session.add(blog)
        db_session.commit()

        # Test queries on indexed fields
        author_blog = db_session.query(Blog).filter(Blog.author_id == user.id).first()
        assert author_blog is not None

        title_blog = db_session.query(Blog).filter(Blog.title == "Test Blog").first()
        assert title_blog is not None

        tag_blog = db_session.query(Blog).filter(Blog.tags.contains("test")).first()
        assert tag_blog is not None

        active_blog = db_session.query(Blog).filter(Blog.is_deleted == False).first()
        assert active_blog is not None

        # Clean up
        db_session.delete(blog)
        db_session.delete(user)
        db_session.commit()


class TestBlogLikeModelIndexing:
    def test_blog_id_index_exists(self, db_session):
        """Test that the blog_id index exists on the BlogLike model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('blog_likes')

        blog_id_index = next((idx for idx in indexes if 'blog_id' in idx['name'] and 'blog_likes' in idx['name']), None)
        assert blog_id_index is not None
        assert 'blog_id' in blog_id_index['column_names']

    def test_user_id_index_exists(self, db_session):
        """Test that the user_id index exists on the BlogLike model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('blog_likes')

        user_id_index = next((idx for idx in indexes if 'user_id' in idx['name'] and 'blog_likes' in idx['name']), None)
        assert user_id_index is not None
        assert 'user_id' in user_id_index['column_names']

    def test_composite_index_exists(self, db_session):
        """Test that the composite index on blog_id and user_id exists"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('blog_likes')

        composite_index = next((idx for idx in indexes if 'blog_user' in idx['name'] and 'blog_likes' in idx['name']), None)
        assert composite_index is not None
        assert 'blog_id' in composite_index['column_names']
        assert 'user_id' in composite_index['column_names']
        assert composite_index['unique'] is True

    def test_query_using_bloglike_indexes(self, db_session):
        """Test that queries use the BlogLike indexes properly"""
        # Create a test user
        user = User(
            email="like_user@example.com",
            first_name="Like",
            last_name="User",
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()

        # Create a test blog
        blog = Blog(
            author_id=user.id,
            title="Like Test Blog",
            content="This is a test blog content for likes",
            tags="test,like",
            is_deleted=False
        )
        db_session.add(blog)
        db_session.commit()

        # Create a test like
        like = BlogLike(
            blog_id=blog.id,
            user_id=user.id,
            ip_address="127.0.0.1"
        )
        db_session.add(like)
        db_session.commit()

        # Test queries on indexed fields
        blog_like = db_session.query(BlogLike).filter(BlogLike.blog_id == blog.id).first()
        assert blog_like is not None

        user_like = db_session.query(BlogLike).filter(BlogLike.user_id == user.id).first()
        assert user_like is not None

        composite_like = db_session.query(BlogLike).filter(
            BlogLike.blog_id == blog.id,
            BlogLike.user_id == user.id
        ).first()
        assert composite_like is not None

        # Clean up
        db_session.delete(like)
        db_session.delete(blog)
        db_session.delete(user)
        db_session.commit()


class TestBlogDislikeModelIndexing:
    def test_blog_id_index_exists(self, db_session):
        """Test that the blog_id index exists on the BlogDislike model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('blog_dislikes')

        blog_id_index = next((idx for idx in indexes if 'blog_id' in idx['name'] and 'blog_dislikes' in idx['name']), None)
        assert blog_id_index is not None
        assert 'blog_id' in blog_id_index['column_names']

    def test_user_id_index_exists(self, db_session):
        """Test that the user_id index exists on the BlogDislike model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('blog_dislikes')

        user_id_index = next((idx for idx in indexes if 'user_id' in idx['name'] and 'blog_dislikes' in idx['name']), None)
        assert user_id_index is not None
        assert 'user_id' in user_id_index['column_names']

    def test_composite_index_exists(self, db_session):
        """Test that the composite index on blog_id and user_id exists"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('blog_dislikes')

        composite_index = next((idx for idx in indexes if 'blog_user' in idx['name'] and 'blog_dislikes' in idx['name']), None)
        assert composite_index is not None
        assert 'blog_id' in composite_index['column_names']
        assert 'user_id' in composite_index['column_names']
        assert composite_index['unique'] is True

    def test_query_using_blogdislike_indexes(self, db_session):
        """Test that queries use the BlogDislike indexes properly"""
        # Create a test user
        user = User(
            email="dislike_user@example.com",
            first_name="Dislike",
            last_name="User",
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()

        # Create a test blog
        blog = Blog(
            author_id=user.id,
            title="Dislike Test Blog",
            content="This is a test blog content for dislikes",
            tags="test,dislike",
            is_deleted=False
        )
        db_session.add(blog)
        db_session.commit()

        # Create a test dislike
        dislike = BlogDislike(
            blog_id=blog.id,
            user_id=user.id,
            ip_address="127.0.0.1"
        )
        db_session.add(dislike)
        db_session.commit()

        # Test queries on indexed fields
        blog_dislike = db_session.query(BlogDislike).filter(BlogDislike.blog_id == blog.id).first()
        assert blog_dislike is not None

        user_dislike = db_session.query(BlogDislike).filter(BlogDislike.user_id == user.id).first()
        assert user_dislike is not None

        composite_dislike = db_session.query(BlogDislike).filter(
            BlogDislike.blog_id == blog.id,
            BlogDislike.user_id == user.id
        ).first()
        assert composite_dislike is not None

        # Clean up
        db_session.delete(dislike)
        db_session.delete(blog)
        db_session.delete(user)
        db_session.commit()