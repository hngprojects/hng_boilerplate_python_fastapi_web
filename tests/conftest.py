import sys, os
import warnings
from unittest.mock import patch
import pytest

 
warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope='module')
def mock_send_email():
    with patch("api.core.dependencies.email_sender.send_email") as mock_email_sending:
        with patch("fastapi.BackgroundTasks.add_task") as add_task_mock:
            add_task_mock.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)
            
            yield mock_email_sending
