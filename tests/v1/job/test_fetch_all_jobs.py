import pytest
from fastapi.testclient import TestClient
from main import app
from api.db.database import get_db
from unittest.mock import MagicMock

client = TestClient(app)

"""Mock data"""
data = [
	{
		"author_id": "066aa37c-9469-7bd6-8000-9284f18cb106",
		"company_name": "Key-Dunn",
		"created_at": "2024-08-01T14:13:29.267336+01:00",
		"department": "Sales",
		"description": "Around time material pass to everybody public. However try think worker. Example structure sit word remain.",
		"id": "066ab89f-94c0-713b-8002-503c9491d2a2",
		"job_type": "Part-time",
		"location": "Woodwardview",
		"salary": "$80,000 - $100,000",
		"title": "Therapist, nutritional",
		"updated_at": "2024-08-01T14:13:29.267336+01:00"
	},
	{
		"author_id": "066aa37c-9469-7bd6-8000-9284f18cb106",
		"company_name": "Campbell-Thompson",
		"created_at": "2024-08-01T14:13:29.267336+01:00",
		"department": "Engineering",
		"description": "Father something certainly also well together never. Near hear senior church personal method. Suggest firm big no.",
		"id": "066ab89f-94c0-713b-8003-51b4113034a5",
		"job_type": "Part-time",
		"location": "North Kenneth",
		"salary": "$80,000 - $100,000",
		"title": "Chief Financial Officer",
		"updated_at": "2024-08-01T14:13:29.267336+01:00"
	},
	{
		"author_id": "066aa37c-9469-7bd6-8000-9284f18cb106",
		"company_name": "Garcia-Perez",
		"created_at": "2024-08-01T14:13:29.267336+01:00",
		"department": "Marketing",
		"description": "Make performance low good wall thank us her.",
		"id": "066ab89f-94c0-713b-8004-eddae1b482fc",
		"job_type": "Part-time",
		"location": "New Benjamin",
		"salary": "$80,000 - $100,000",
		"title": "Field trials officer",
		"updated_at": "2024-08-01T14:13:29.267336+01:00"
	},
	{
		"author_id": "066aa37c-9469-7bd6-8000-9284f18cb106",
		"company_name": "Young, Torres and Williams",
		"created_at": "2024-08-01T14:13:29.267336+01:00",
		"department": "Engineering",
		"description": "General section enough out. Administration become ready without determine affect follow.",
		"id": "066ab89f-94c0-713b-8005-ee39b4f5e4e5",
		"job_type": "Part-time",
		"location": "Jenniferborough",
		"salary": "$60,000 - $80,000",
		"title": "Osteopath",
		"updated_at": "2024-08-01T14:13:29.267336+01:00"
	},
	{
		"author_id": "066aa37c-9469-7bd6-8000-9284f18cb106",
		"company_name": "French, Moore and Lewis",
		"created_at": "2024-08-01T14:13:29.267336+01:00",
		"department": "Engineering",
		"description": "Mind fill over break heart.",
		"id": "066ab89f-94c0-713b-8006-657065761ab2",
		"job_type": "Part-time",
		"location": "Kennethchester",
		"salary": "$80,000 - $100,000",
		"title": "Nurse, adult",
		"updated_at": "2024-08-01T14:13:29.267336+01:00"
	},
	{
		"author_id": "066aa37c-9469-7bd6-8000-9284f18cb106",
		"company_name": "Boyd-Garrett",
		"created_at": "2024-08-01T14:13:29.267336+01:00",
		"department": "Sales",
		"description": "High simply test traditional. Only term most become.",
		"id": "066ab89f-94c0-713b-8007-96a61105c06d",
		"job_type": "Contract",
		"location": "Stephaniebury",
		"salary": "$60,000 - $80,000",
		"title": "Tree surgeon",
		"updated_at": "2024-08-01T14:13:29.267336+01:00"
	},
	{
		"author_id": "066aa37c-9469-7bd6-8000-9284f18cb106",
		"company_name": "Oneal-Herrera",
		"created_at": "2024-08-01T14:13:29.267336+01:00",
		"department": "Engineering",
		"description": "Population nothing require discussion contain international enjoy. Age pull machine nothing.",
		"id": "066ab89f-94c0-713b-8008-43eac2ca22d7",
		"job_type": "Full-time",
		"location": "Millertown",
		"salary": "$60,000 - $80,000",
		"title": "Bookseller",
		"updated_at": "2024-08-01T14:13:29.267336+01:00"
	},
	{
		"author_id": "066aa37c-9469-7bd6-8000-9284f18cb106",
		"company_name": "Carroll, Hernandez and Cook",
		"created_at": "2024-08-01T14:13:29.267336+01:00",
		"department": "Sales",
		"description": "Difficult full them town technology wall edge. Finally understand positive forward. Put nature top. Opportunity small expert better fill health common.",
		"id": "066ab89f-94c0-713b-8009-dee22578b6b5",
		"job_type": "Contract",
		"location": "East Elizabeth",
		"salary": "$80,000 - $100,000",
		"title": "Ranger/warden",
		"updated_at": "2024-08-01T14:13:29.267336+01:00"
	},
	{
		"author_id": "066aa37c-9469-7bd6-8000-9284f18cb106",
		"company_name": "Walker-Bishop",
		"created_at": "2024-08-01T14:13:29.267336+01:00",
		"department": "Marketing",
		"description": "Follow recent owner ever. Agreement former nor I care.",
		"id": "066ab89f-94c0-713b-800a-63f998335489",
		"job_type": "Part-time",
		"location": "South Kimberlyland",
		"salary": "$60,000 - $80,000",
		"title": "Manufacturing engineer",
		"updated_at": "2024-08-01T14:13:29.267336+01:00"
	},
	{
		"author_id": "066aa37c-9469-7bd6-8000-9284f18cb106",
		"company_name": "Johnson Group",
		"created_at": "2024-08-01T14:13:29.267336+01:00",
		"department": "Sales",
		"description": "Dark scene begin figure director police. Edge number though.",
		"id": "066ab89f-94c0-713b-800b-9431b71926c1",
		"job_type": "Full-time",
		"location": "North Anthony",
		"salary": "$60,000 - $80,000",
		"title": "Diagnostic radiographer",
		"updated_at": "2024-08-01T14:13:29.267336+01:00"
	}
]

"""Mocking The database"""
@pytest.fixture
def db_session_mock():
	db_session = MagicMock()
	yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
	def get_db_override():
		yield db_session_mock
	
	app.dependency_overrides[get_db] = get_db_override
	yield
	# Clean up after the test by removing the override
	app.dependency_overrides = {}

"""Testing the database"""
def test_get_testimonials(db_session_mock):
	db_session_mock.query().offset().limit().all.return_value = data

	url = 'api/v1/jobs'
	mock_query = MagicMock()
	mock_query.count.return_value = 3
	db_session_mock.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = data

	db_session_mock.query.return_value = mock_query
	response = client.get(url, params={'page_size': 2, 'page': 1})
	assert len(response.json()['data']) == 5
	assert response.status_code == 200
	assert response.json()['message'] == 'Successfully fetched items'
	assert response.json()['data']['total'] == 3
 
