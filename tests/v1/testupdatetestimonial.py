import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from main import app
from api.db.database import get_db, get_db_engine, Base

client = TestClient(app)

# 

def test_update_testimonial_with_id(testimonial_id):
    login =  client.post('/auth/login', data={
        "username": "testuser",
        "password": "Testpassword@123"
    })
    access_token = login.json()['access_token']
  
    headers = {
        'Authorization' : f'Bearer {access_token}'
    }
    testimonial_data = {
        "content_data" : "I love testimonials"
    }
    response = client.put(f'/api/v1/testimonials/{testimonial_id}', json=testimonial_data, headers=headers)

    assert response.status_code == 200
    assert response.json() == {
          'status' : 200,
          'message' : 'Testimonial Updated Successfully',
          'data': {
               'user_id' : 'random_id',
               'content' : 'I love testimonials',
               'updated_at' : 'cureent_time'
          }
    }


    not_owner =  client.post('/auth/login', data={
        "username": "anothertestuser",
        "password": "anotherTestpassword@123"
    })
    
    headers = {
        'Authorization' : f'Bearer {access_token}'
    }
    testimonial_data = {
        "content_data" : "I love testimonials"
    }



    not_authorized = client.put(f'/api/v1/testimonials/{testimonial_id}', json=testimonial_data, headers=headers)

    assert response.status_code == 401
    assert response.json() == {
        "status":  "Forbidden",
        "message":  "Only owners of testimonial can update",
        "status_code": 403
    }

    
 




 
  