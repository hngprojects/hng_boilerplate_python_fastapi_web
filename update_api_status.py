import requests
import json

# Define the API endpoint
BASE_URL = "https://staging.api-python.boilerplate.hng.tech"
API_ENDPOINT = f"{BASE_URL}/api/v1/api-status"


# Function to parse result.json and post the data to the endpoint
def parse_and_post_results():
    try:
        with open('result.json') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading result.json: {e}")
        return

    for item in data.get('run', {}).get('executions', []):
        api_group = item.get('item', {}).get('name')
        status_code = item.get('response', {}).get('code')
        response_time = item.get('item', {}).get('responseTime')

        if isinstance(status_code, int) and status_code >= 500:
            status = 'Down'
            details = item.get('response', {}).get('status', 'No status available')
        else:
            assertions = item.get('assertions', [])
            status = "Operational"
            details = "All tests passed"

            for assertion in assertions:
                if assertion.get('error'):
                    status = "Degraded"
                    if 'Response time' in assertion.get('assertion', ''):
                        details = 'High response time detected'
                    elif 'available' in assertion.get('assertion', ''):
                        details = 'API is not available'
                    else:
                        details = f"Test failed: {assertion.get('error').get('message', 'No error message')}"
                    break

        payload = {
            "api_group": api_group,
            "status": status,
            "response_time": response_time,
            "details": details,
        }

        try:
        # send a POST request to create
            response = requests.post(API_ENDPOINT, json=payload)

            # Check response status
            if response.status_code in (200, 201):
                print(f"Successfully updated/created record for {api_group}.")
            else:
                print(f"Failed to update/create record for {api_group}: {response.content}")
        except requests.RequestException as e:
            print(f"Error posting data to API: {e}")

# Run the function
parse_and_post_results()
