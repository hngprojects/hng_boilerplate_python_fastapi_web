import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from main import app
from api.db.database import get_db, get_db_engine, Base

client = TestClient(app)

# 

def test_update_testimonial_with_id():
    #Testing the owner of the Content

    login =  client.post('/auth/login', data={
        "username": "Marvelous", #Should be changed Depending on the user
        "password": "Winner174" #should be changed Depending on the user
    })
    access_token = login.json()['access_token']
    test_id = "0669d371-6d2d-7009-8000-f3f59d4f854b" #id should be changed just for testing no creation endpoint
    headers = {
        'Authorization' : f'Bearer {access_token}'
    }
    testimonial_data = {
        "content" : "I love testimonials"
    }
    response = client.put(f'/api/v1/testimonials/{test_id}', json=testimonial_data, headers=headers) #id should be changed 

    assert response.status_code == 200
    assert "data" in response.json()
   
   #Testing another user with the same Contnet

    not_owner =  client.post('/auth/login', data={
        "username": "Marveld",
        "password": "Doyin123"
    })
    access_token = not_owner.json()['access_token']
    headers = {
        'Authorization' : f'Bearer {access_token}'
    }
    testimonial_data = {
        "content" : "I hate testimonials"
    }



    not_authorized = client.put(f'/api/v1/testimonials/{test_id}', json=testimonial_data, headers=headers) 

    assert not_authorized.status_code == 403
    

    
 




 
  