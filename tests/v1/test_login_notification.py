import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
import requests
from fastapi import Request
from api.v1.models import User
from api.v1.services.login_notification import send_login_notification


@pytest.mark.asyncio
class TestSendLoginNotification:

    @patch('api.v1.services.login_notification.send_email', new_callable=AsyncMock)
    @patch('api.v1.services.login_notification.requests.get')
    async def test_send_login_notification_successful(self, mock_request_get, mock_send_email):
        """Test successful login notification email with correct IP geolocation data."""

        # Mock user
        user = MagicMock(spec=User)
        user.email = "test@example.com"
        user.first_name = "Test"
        user.last_name = "User"

        # Mock request with headers
        request = MagicMock(spec=Request)
        request.client.host = "8.8.8.8"
        request.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Mock IP location API response
        mock_request_get.return_value.json.return_value = {
            "city": "Mountain View",
            "country": "United States"
        }

        # Call the function
        await send_login_notification(user, request)

        # Fix: Ensure the request mock includes the timeout argument
        mock_request_get.assert_called_once_with("http://ip-api.com/json/8.8.8.8", timeout=5)
        mock_send_email.assert_called_once()

        # Validate email context
        context = mock_send_email.call_args[1]['context']
        assert context['location'] == "Mountain View, United States"

    @patch('api.v1.services.login_notification.send_email', new_callable=AsyncMock)
    @patch('api.v1.services.login_notification.requests.get')
    async def test_send_login_notification_api_error(self, mock_request_get, mock_send_email):
        """Test login notification when the IP geolocation API fails."""

        # Mock user
        user = MagicMock(spec=User)
        user.email = "test@example.com"
        user.first_name = "Test"
        user.last_name = "User"

        # Mock request
        request = MagicMock(spec=Request)
        request.client.host = "1.2.3.4"
        request.headers = {
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        }

        # Mock API error
        mock_request_get.side_effect = requests.RequestException("API Error")

        # Call the function
        await send_login_notification(user, request)

        # Fix: Ensure the function handles the failure without crashing
        mock_request_get.assert_called_once_with("http://ip-api.com/json/1.2.3.4", timeout=5)
        mock_send_email.assert_called_once()

        # Validate fallback location
        context = mock_send_email.call_args[1]['context']
        assert context['location'] == "Unknown Location"  # Ensure fallback works