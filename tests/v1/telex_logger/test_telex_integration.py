import pytest
import datetime
import json
from unittest.mock import AsyncMock, patch
from api.utils.send_logs import send_error_to_telex
from api.utils.settings import settings
from api.utils.logger import logger

mock_webhook = "http://test-webhook.com" or settings.TELEX_WEBHOOK_URL


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
@patch("api.utils.send_logs.TELEX_WEBHOOK_URL", mock_webhook)
async def test_send_error_to_telex_success(mock_post):
    """Test handling failure when sending error log to Telex"""

    mock_post.return_value.status_code = 200

    request_method = "GET"
    request_url_path = "/test-endpoint"
    exc = Exception("Test Exception")
    exc.status_code = 500

    await send_error_to_telex(request_method, request_url_path, exc)

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    expected_payload = {
        "status": "error",
        "username": "hng_boilerplate",
        "message": json.dumps(
            {
                "timestamp": timestamp,
                "event_name": "server_error",
                "request_method": request_method,
                "request_path": request_url_path,
                "status_code": 500,
                "error_message": "An unexpected error occurred: Test Exception",
            },
            indent=4,
        ),
        "event_name": "🚨 Internal Server Error",
    }

    mock_post.assert_awaited_once()
    args, kwargs = mock_post.await_args
    assert args[0] == mock_webhook
    assert kwargs["json"]["username"] == expected_payload["username"]
    assert kwargs["json"]["event_name"] == expected_payload["event_name"]

    actual_message = json.loads(kwargs["json"]["message"])
    expected_message = json.loads(expected_payload["message"])

    assert actual_message["status_code"] == expected_message["status_code"]
    assert actual_message["error_message"] == expected_message["error_message"]
    assert actual_message["timestamp"] == expected_message["timestamp"]


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
@patch("api.utils.logger.logger.exception")
@patch("api.utils.send_logs.TELEX_WEBHOOK_URL", mock_webhook)
async def test_send_error_to_telex_failure(mock_logger, mock_post):
    """Test handling failure when sending error log to Telex"""

    mock_post.side_effect = Exception("HTTP error")

    request_method = "POST"
    request_url_path = "/fail-endpoint"
    exc = Exception("Another Test Exception")

    await send_error_to_telex(request_method, request_url_path, exc)

    mock_logger.assert_called_once_with("Failed to send error log to Telex: HTTP error")

    mock_post.assert_awaited_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
@patch("api.utils.logger.logger.error")
@patch("api.utils.send_logs.TELEX_WEBHOOK_URL", None)
async def test_send_error_to_telex_missing_webhook(mock_logger, mock_post):
    """Test that function does nothing if TELEX_WEBHOOK_URL is missing"""

    request_method = "GET"
    request_url_path = "/test-endpoint"
    exc = Exception("Test Exception")

    await send_error_to_telex(request_method, request_url_path, exc)

    mock_post.assert_not_awaited()

    mock_logger.assert_called_once_with("TELEX_WEBHOOK_URL is not set")
