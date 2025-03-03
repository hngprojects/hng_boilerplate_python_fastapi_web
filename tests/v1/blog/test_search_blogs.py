import pytest
from fastapi.testclient import TestClient
from main import app  

client = TestClient(app)

def test_search_blogs():
    response = client.get("/api/v1/blogs/search", params={
        "keyword": "test",
        "category": "technology",
        "author": "John Doe",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "tags": "AI,Machine Learning",
        "page": 1,
        "per_page": 5
    })
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status_code"] == 200
    assert "blogs" in json_response
    assert isinstance(json_response["blogs"], list)

def test_search_blogs_no_results():
    response = client.get("/api/v1/blogs/search", params={"keyword": "nonexistentkeyword"})
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status_code"] == 200
    assert "blogs" in json_response
    assert len(json_response["blogs"]) == 0

def test_search_blogs_invalid_date_format():
    response = client.get("/api/v1/blogs/search", params={"start_date": "invalid-date"})
    assert response.status_code == 400
    json_response = response.json()
    assert "message" in json_response
    assert json_response["message"] == "Invalid start_date format. Use YYYY-MM-DD."

def test_search_blogs_negative_pagination():
    response = client.get("/api/v1/blogs/search", params={"page": -1, "per_page": 5})
    assert response.status_code == 422
    json_response = response.json()
    assert "errors" in json_response
    assert any(error["loc"] == ["query", "page"] and error["msg"] == "Input should be greater than or equal to 1"
               for error in json_response["errors"])

def test_search_blogs_exceed_max_per_page():
    response = client.get("/api/v1/blogs/search", params={"per_page": 200})
    assert response.status_code == 422
    json_response = response.json()
    assert "errors" in json_response
    assert any(error["loc"] == ["query", "per_page"] and error["msg"] == "Input should be less than or equal to 100"
               for error in json_response["errors"])
