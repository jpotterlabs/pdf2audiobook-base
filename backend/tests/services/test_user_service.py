import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.services.user import UserService
from app.schemas import UserUpdate


class TestUserService:
    def setup_method(self):
        self.db = MagicMock()
        self.user_service = UserService(self.db)

    def test_get_user_by_id_found(self):
        """Test getting user by ID when user exists"""
        # Arrange
        user_id = 1
        mock_user = MagicMock()
        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        # Act
        result = self.user_service.get_user_by_id(user_id)

        # Assert
        assert result == mock_user
        self.db.query.assert_called_once()
        self.db.query.return_value.filter.assert_called_once()

    def test_get_user_by_id_not_found(self):
        """Test getting user by ID when user doesn't exist"""
        # Arrange
        user_id = 1
        self.db.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.user_service.get_user_by_id(user_id)

        # Assert
        assert result is None

    def test_get_user_by_email_found(self):
        """Test getting user by email when user exists"""
        # Arrange
        email = "test@example.com"
        mock_user = MagicMock()
        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        # Act
        result = self.user_service.get_user_by_email(email)

        # Assert
        assert result == mock_user

    def test_get_user_by_email_not_found(self):
        """Test getting user by email when user doesn't exist"""
        # Arrange
        email = "test@example.com"
        self.db.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.user_service.get_user_by_email(email)

        # Assert
        assert result is None

    def test_get_or_create_user_existing_user_no_update(self):
        """Test get_or_create_user when user exists and no update needed"""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
        mock_user = MagicMock()
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"

        with patch.object(self.user_service, 'get_user_by_email', return_value=mock_user):
            # Act
            result = self.user_service.get_or_create_user(user_data)

            # Assert
            assert result == mock_user
            self.db.commit.assert_not_called()

    def test_get_or_create_user_existing_user_with_update(self):
        """Test get_or_create_user when user exists and needs update"""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "first_name": "Jane",
            "last_name": "Smith"
        }
        mock_user = MagicMock()
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"

        with patch.object(self.user_service, 'get_user_by_email', return_value=mock_user):
            # Act
            result = self.user_service.get_or_create_user(user_data)

            # Assert
            assert result == mock_user
            assert mock_user.first_name == "Jane"
            assert mock_user.last_name == "Smith"
            self.db.commit.assert_called_once()
            self.db.refresh.assert_called_once_with(mock_user)

    def test_get_or_create_user_new_user(self):
        """Test get_or_create_user when creating new user"""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
        mock_user = MagicMock()

        with patch.object(self.user_service, 'get_user_by_email', return_value=None), \
             patch('app.services.user.User', return_value=mock_user):
            # Act
            result = self.user_service.get_or_create_user(user_data)

            # Assert
            assert result == mock_user
            self.db.add.assert_called_once_with(mock_user)
            self.db.commit.assert_called_once()
            self.db.refresh.assert_called_once_with(mock_user)

    def test_update_user_success(self):
        """Test successful user update"""
        # Arrange
        user_id = 1
        user_update = UserUpdate(first_name="Jane", last_name="Smith")
        mock_user = MagicMock()

        with patch.object(self.user_service, 'get_user_by_id', return_value=mock_user):
            # Act
            result = self.user_service.update_user(user_id, user_update)

            # Assert
            assert result == mock_user
            assert mock_user.first_name == "Jane"
            assert mock_user.last_name == "Smith"
            self.db.commit.assert_called_once()
            self.db.refresh.assert_called_once_with(mock_user)