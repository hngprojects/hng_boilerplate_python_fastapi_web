import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError
from api.v1.services.language import get_unique_languages
from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)

def test_get_unique_languages_success():
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter.return_value.distinct.return_value.all.return_value = [
        ('English',),
        ('Spanish',),
        ('French',),
        ('German',),
        ('Chinese',)
    ]
    mock_db.query.return_value = mock_query

    languages = get_unique_languages(mock_db)
    assert languages == ['English', 'Spanish', 'French', 'German', 'Chinese']

def test_get_unique_languages_error():
    mock_db = MagicMock()
    mock_db.query.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(Exception) as excinfo:
        get_unique_languages(mock_db)
    
    assert "Error retrieving languages" in str(excinfo.value)


