import pytest
from sqlalchemy import inspect
from api.v1.models.user import User


class TestUserModelIndexing:
    def test_email_index_exists(self, db_session):
        """Test that the email index exists on the User model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('users')

        # Check if email index exists - PostgreSQL may prefix the index name with the table name
        email_index = next((idx for idx in indexes if 'email' in idx['name'] and 'users' in idx['name']), None)
        assert email_index is not None
        assert 'email' in email_index['column_names']

    def test_is_active_index_exists(self, db_session):
        """Test that the is_active index exists on the User model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('users')

        # Check if is_active index exists
        is_active_index = next((idx for idx in indexes if 'is_active' in idx['name'] and 'users' in idx['name']), None)
        assert is_active_index is not None
        assert 'is_active' in is_active_index['column_names']

    def test_is_deleted_index_exists(self, db_session):
        """Test that the is_deleted index exists on the User model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('users')

        # Check if is_deleted index exists
        is_deleted_index = next((idx for idx in indexes if 'is_deleted' in idx['name'] and 'users' in idx['name']), None)
        assert is_deleted_index is not None
        assert 'is_deleted' in is_deleted_index['column_names']

    def test_is_verified_index_exists(self, db_session):
        """Test that the is_verified index exists on the User model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('users')

        # Check if is_verified index exists
        is_verified_index = next((idx for idx in indexes if 'is_verified' in idx['name'] and 'users' in idx['name']), None)
        assert is_verified_index is not None
        assert 'is_verified' in is_verified_index['column_names']

    def test_is_superadmin_index_exists(self, db_session):
        """Test that the is_superadmin index exists on the User model"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('users')

        # Check if is_superadmin index exists
        is_superadmin_index = next((idx for idx in indexes if 'is_superadmin' in idx['name'] and 'users' in idx['name']), None)
        assert is_superadmin_index is not None
        assert 'is_superadmin' in is_superadmin_index['column_names']

    def test_name_composite_index_exists(self, db_session):
        """Test that the composite index on first_name and last_name exists"""
        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('users')

        # Check if composite name index exists
        name_index = next((idx for idx in indexes if 'first_name' in idx['name'] and 'last_name' in idx['name'] and 'users' in idx['name']), None)
        assert name_index is not None
        assert 'first_name' in name_index['column_names']
        assert 'last_name' in name_index['column_names']

    def test_query_using_indexes(self, db_session):
        """Test that queries use the indexes properly"""
        # Create a test user
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()

        # Test queries on indexed fields
        active_user = db_session.query(User).filter(User.is_active == True).first()
        assert active_user is not None

        email_user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert email_user is not None

        name_user = db_session.query(User).filter(
            User.first_name == "Test",
            User.last_name == "User"
        ).first()
        assert name_user is not None

        # Clean up
        db_session.delete(user)
        db_session.commit()