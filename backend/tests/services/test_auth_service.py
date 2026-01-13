import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.services.auth import verify_clerk_token, get_current_user, get_optional_current_user
from app.schemas import User as UserSchema


from app.services.auth import verify_clerk_token, get_current_user, get_optional_current_user
from app.schemas import User as UserSchema

class TestAuthService:
    def test_verify_clerk_token(self):
        """Test the mocked token verification"""
        result = verify_clerk_token("any-token")
        assert result["email"] == "base@example.com"
        assert result["first_name"] == "Base"

    @patch("app.services.auth.UserService")
    def test_get_current_user(self, mock_user_service_class):
        """Test get_current_user returns a user"""
        db = MagicMock()
        mock_user = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_or_create_user.return_value = mock_user
        mock_user_service_class.return_value = mock_user_service
        
        result = get_current_user(None, db)
        assert result == mock_user
        mock_user_service.get_or_create_user.assert_called_once()

    @patch("app.services.auth.UserService")
    def test_get_optional_current_user(self, mock_user_service_class):
        """Test get_optional_current_user returns a user"""
        db = MagicMock()
        mock_user = MagicMock()
        mock_user_service = MagicMock()
        mock_user_service.get_or_create_user.return_value = mock_user
        mock_user_service_class.return_value = mock_user_service
        
        result = get_optional_current_user(None, db)
        assert result == mock_user