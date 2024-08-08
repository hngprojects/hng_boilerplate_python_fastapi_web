import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from api.v1.models import ProductComment, User
from api.v1.services.user import user_service
from api.v1.services.product_comment import product_comment_service

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_get_current_user():
    user = User(id="test_user_id")
    return MagicMock(return_value=user)

def test_delete_product_comment(mock_db, mock_get_current_user):
    with patch("api.db.database.get_db", return_value=mock_db):
        with patch("api.v1.services.user.user_service.get_current_user", mock_get_current_user):
            # Mock data
            product_id = "test_product_id"
            comment_id = "test_comment_id"
            user_id = "test_user_id"
            mock_comment = ProductComment(id=comment_id, product_id=product_id, user_id=user_id, content='some comment')

            # Setup mock return values
            mock_db.query.return_value.filter_by.return_value.first.return_value = mock_comment
            
            # Define the delete method in product_comment_service
            def mock_delete(comment_id, product_id, user, db):
                # Check if the comment to delete matches the mock_comment
                comment_to_delete = db.query(ProductComment).filter_by(id=comment_id, product_id=product_id).first()
                if comment_to_delete:
                    db.delete(comment_to_delete)
                    db.commit()
                    return {
                        "status": "success",
                        "status_code": 200,
                        "message": "comment successfully deleted"
                    }
                return {
                    "status": "error",
                    "status_code": 404,
                    "message": "comment not found"
                }

            # Patch the delete method
            with patch("api.v1.services.product_comment.product_comment_service.delete", side_effect=mock_delete) as mock_delete_service:
                # Call the delete method
                result = product_comment_service.delete(comment_id, product_id, mock_get_current_user(), mock_db)

                # Assertions
                assert result == {
                    "status": "success",
                    "status_code": 200,
                    "message": "comment successfully deleted"
                }

                # Verify that the delete method was called
                mock_db.query.return_value.filter_by.return_value.first.assert_called_once()
                mock_db.delete.assert_called_once_with(mock_comment)
                mock_db.commit.assert_called_once()