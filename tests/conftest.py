import itertools
import sys, os
import warnings
from unittest.mock import patch
import pytest



# Global IP generator (supports 16 million+ unique IPs)
IP_GENERATOR = itertools.cycle(
    (f"127.{i//65536}.{(i//256)%256}.{i%256}" for i in itertools.count())
)

@pytest.fixture(autouse=True)
def auto_mock_client_ip():
    """Automatically mock client IP for all tests"""
    with patch("fastapi.Request.client") as mock_client:
        mock_client.host = next(IP_GENERATOR)
        yield

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope='module')
def mock_send_email():
    with patch("api.core.dependencies.email_sender.send_email") as mock_email_sending:
        with patch("fastapi.BackgroundTasks.add_task") as add_task_mock:
            add_task_mock.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)
            yield mock_email_sending
