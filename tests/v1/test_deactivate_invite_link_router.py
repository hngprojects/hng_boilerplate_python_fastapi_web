
# Dependencies:
# pip install pytest-mock
# pip install pytest-asyncio

import pytest
from unittest.mock import MagicMock, patch

from api.v1.models.user import User, WaitlistUser
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product
from api.v1.models.base import Base
from api.v1.models.subscription import Subscription
from api.v1.models.blog import Blog
from api.v1.models.job import Job
from api.v1.models.invitation import Invitation
from api.v1.models.role import Role
from api.v1.models.permission import Permission
from api.db.database import Base, get_db

from api.v1.routes.deactivate_invite_link_router import deactivate_invite_link
from api.v1.routes.deactivate_invite_link_router import CustomInviteDeactivateException
from api.v1.models.org import Organization



from api.v1.schemas.auth import UserBase
from api.v1.schemas.invitation import DeactivateInviteBody
from uuid_extensions import uuid7
from datetime import datetime, timedelta


@pytest.fixture
def setups():
    data = {}

    data['user_id'] = uuid7()
    data['inv_id'] = uuid7()
    data['org_id'] = uuid7()
    data['mock_invite'] = Invitation(
        id=data['inv_id'], user_id=data['user_id'], organization_id=data['org_id'], is_valid=True
        )
        
    data['mock_query'] = MagicMock()
    data['mock_where'] = MagicMock()

    data['pyd_user'] = UserBase(
        id=data['user_id'],
        first_name="Bob",
        last_name="Lash",
        email="bob@example.com",
        created_at = datetime.now()
        )

    yield data

    data.clear()



class TestCodeUnderTest:

    # Deactivating a valid invitation link with correct user authorization
    @patch('api.v1.routes.deactivate_invite_link_router.db')
    def test_deactivate_valid_invitation_link(self, mocker, setups):
        mock_invite = Invitation(
            id=setups['inv_id'], user_id=setups['user_id'], organization_id=setups['org_id'], is_valid=True,
            expires_at=(datetime.now() + timedelta(hours=2)))
    
        mocker.query.return_value = setups['mock_query']
        setups['mock_query'].where.return_value = setups['mock_where']
        setups['mock_where'].first.return_value = mock_invite

        pyd_user = setups['pyd_user']
        mocker.patch('api.utils.dependencies.get_current_user', return_value=pyd_user)

        response = deactivate_invite_link(
            DeactivateInviteBody(invitation_link=f'invite_{str(setups["inv_id"])}'),
            user=pyd_user
        )

        assert response.status_code == 200
        assert response.message == "Invitation link has been deactivated"

    # Handling a valid invitation link and marking it as invalid
    @patch('api.v1.routes.deactivate_invite_link_router.db')
    def test_handle_valid_invitation_link_mark_invalid(self, mocker, setups):

        mock_invite = Invitation(id=setups['inv_id'], user_id=setups['user_id'], organization_id=setups['org_id'], is_valid=True,
        expires_at=(datetime.now() + timedelta(hours=2)))
    
        mocker.query.return_value = setups['mock_query']
        setups['mock_query'].where.return_value = setups['mock_where']
        setups['mock_where'].first.return_value = mock_invite

        pyd_user = setups['pyd_user']
        mocker.patch('api.utils.dependencies.get_current_user', return_value=pyd_user)
        
        response =  deactivate_invite_link(
            DeactivateInviteBody(invitation_link=f'invite_{str(setups["inv_id"])}'),
            user=pyd_user
        )
    
        assert not mock_invite.is_valid

    # # Handling an invitation link with incorrect format
    # @pytest.mark.asyncio
    def test_handle_incorrect_format_invitation_link(self, mocker, setups):
        
        pyd_user = setups['pyd_user']
        mocker.patch('api.utils.dependencies.get_current_user', return_value=pyd_user)
    
        with pytest.raises(CustomInviteDeactivateException) as exc_info:
            deactivate_invite_link(
                DeactivateInviteBody(invitation_link='invalid_format'),
                user=pyd_user
            )
    
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail['error'] == "Invalid or expired invitation link"

    # # Handling a non-existent invitation link
    @patch('api.v1.routes.deactivate_invite_link_router.db')
    def test_handle_non_existent_invitation_link(self, mocker, setups):

        mock_invite = Invitation(id=setups['inv_id'], user_id=setups['user_id'], organization_id=setups['org_id'], is_valid=True,
        expires_at=(datetime.now() + timedelta(hours=2)))
    
        mocker.query.return_value = setups['mock_query']
        setups['mock_query'].where.return_value = setups['mock_where']
        setups['mock_where'].first.return_value = mock_invite

        pyd_user = setups['pyd_user']
        mocker.patch('api.utils.dependencies.get_current_user', return_value=pyd_user)
        
        with pytest.raises(CustomInviteDeactivateException) as exc_info:
            deactivate_invite_link(
                DeactivateInviteBody(invitation_link='invite_9999'),
                user=pyd_user
            )
    
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail['error'] == "Invalid or expired invitation link"

    # # Handling an expired or already deactivated invitation link
    
    @patch('api.v1.routes.deactivate_invite_link_router.db')
    def test_handle_expired_or_deactivated_invitation_link(self, mocker, setups):
        
        mock_invite = Invitation(id=setups['inv_id'], user_id=setups['user_id'], organization_id=setups['org_id'], is_valid=True, expires_at=(datetime.now() - timedelta(hours=2)))
    
        mocker.query.return_value = setups['mock_query']
        setups['mock_query'].where.return_value = setups['mock_where']
        setups['mock_where'].first.return_value = mock_invite

        pyd_user = setups['pyd_user']
        mocker.patch('api.utils.dependencies.get_current_user', return_value=pyd_user)
    

        with pytest.raises(CustomInviteDeactivateException) as exc_info:
         deactivate_invite_link(
             DeactivateInviteBody(invitation_link=f'invite_{str(setups["inv_id"])}'),
            user=pyd_user
        )
    
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail['error'] == "Invalid or expired invitation link"