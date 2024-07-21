import pytest
from decouple import config
import requests
import json


@pytest.mark.parametrize("testimonial_id" , ['0669d371-6d2d-7009-8000-f3f59d4f854b','0669d38d-fc74-76fd-8000-eec481440a29','0669d39b-a5a8-7b6d-8000-49b8fefd7287'])
def test_update_testimonial(testimonial_id):
    base_url = 'http://127.0.0.1:7001/'
   
    url = f'{base_url}/api/v1/testimonials/{testimonial_id}'
    headers = {
        'Authorization' : f'Bearer {config("JWT_Token")}'
        
    }
    data = {
        'content': 'I love doyin'
    }

    response = requests.put(url, headers=headers, data=json.dumps(data))

    assert response.status_code == 200

    assert "data" in response.json()