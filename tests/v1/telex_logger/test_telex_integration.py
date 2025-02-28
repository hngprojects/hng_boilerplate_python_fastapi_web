import pytest
import datetime
import json
from unittest.mock import AsyncMock, patch
from api.utils.send_logs import send_error_to_telex
from api.utils.settings import settings
from api.utils.logger import logger

mock_webhook="http://test-webhook.com" or settings.TELEX_WEBHOOK_URL


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
@patch("api.utils.send_logs.TELEX_WEBHOOK_URL", mock_webhook)
async def test_send_error_to_telex_success(mock_post):
    """Test handling failure when sending error log to Telex"""

    # Mock a successful API response
    mock_post.return_value.status_code = 200

    request_method = "GET"
    request_url_path = "/test-endpoint"
    exc = Exception("Test Exception")
    exc.status_code = 500  # Simulating an exception with a status_code attribute

    await send_error_to_telex(request_method, request_url_path, exc)

    # Get the current timestamp in the required format (YYYY-MM-DDTHH:MM)
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M")

    expected_payload = {
        "status": "error",
        "username": "hng_boilerplate",
        "message": json.dumps(  # Ensure message is a JSON string
            {
                "timestamp": timestamp,  # Ensure timestamp matches format
                "event_name": "server_error",
                "request_method": request_method,
                "request_path": request_url_path,
                "status_code": 500,  # Extracted from the exception
                "error_message": "An unexpected error occurred: Test Exception",
            },
            indent=4
        ),
        "event_name": "🚨 Internal Server Error",
    }

    # Ensure that the API call was made once with correct data
    mock_post.assert_awaited_once()
    args, kwargs = mock_post.await_args
    assert args[0] == mock_webhook
    assert kwargs["json"]["username"] == expected_payload["username"]
    assert kwargs["json"]["event_name"] == expected_payload["event_name"]

    # Convert message back to a dictionary to compare fields correctly
    actual_message = json.loads(kwargs["json"]["message"])
    expected_message = json.loads(expected_payload["message"])

    assert actual_message["status_code"] == expected_message["status_code"]
    assert actual_message["error_message"] == expected_message["error_message"]
    assert actual_message["timestamp"] == expected_message["timestamp"].replace("T", " ")  # Allow slight time drift


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
@patch("api.utils.logger.logger.exception")
@patch("api.utils.send_logs.TELEX_WEBHOOK_URL", mock_webhook)
async def test_send_error_to_telex_failure(mock_logger, mock_post):
    """Test handling failure when sending error log to Telex"""

    # Simulate an exception being raised during the HTTP request
    mock_post.side_effect = Exception("HTTP error")

    request_method = "POST"
    request_url_path = "/fail-endpoint"
    exc = Exception("Another Test Exception")

    await send_error_to_telex(request_method, request_url_path, exc)

    # Ensure that the exception logger was called with the correct message
    mock_logger.assert_called_once_with("Failed to send error log to Telex: HTTP error")

    # Ensure the API was still attempted
    mock_post.assert_awaited_once()

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
@patch("api.utils.logger.logger.error")  # Mock logger.warning
@patch("api.utils.send_logs.TELEX_WEBHOOK_URL", None)
async def test_send_error_to_telex_missing_webhook(mock_logger, mock_post):
    """Test that function does nothing if TELEX_WEBHOOK_URL is missing"""
    # Temporarily remove the webhook URL
    request_method = "GET"
    request_url_path = "/test-endpoint"
    exc = Exception("Test Exception")

    await send_error_to_telex(request_method, request_url_path, exc)

    # Ensure no API call was made
    mock_post.assert_not_awaited()

    # Ensure the logger warning was called
    mock_logger.assert_called_once_with("TELEX_WEBHOOK_URL is not set")
