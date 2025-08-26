from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import MagicLinkToken, User


@pytest.mark.django_db
class TestSignupAPI:
    def setup_method(self):
        self.client = APIClient()
        self.signup_url = reverse("signup")

    def test_successful_signup(self):
        """Test successful user signup"""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "fullname": "Test User",
            "password": "testpassword123",
            "password_confirm": "testpassword123",
        }

        response = self.client.post(self.signup_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "User created successfully"
        assert "user" in response.data
        assert response.data["user"]["email"] == "test@example.com"
        assert response.data["user"]["username"] == "testuser"
        assert response.data["user"]["fullname"] == "Test User"

        # Verify user was created in database
        user = User.objects.get(email="test@example.com")
        assert user.username == "testuser"
        assert user.fullname == "Test User"

    def test_signup_password_mismatch(self):
        """Test signup fails when passwords don't match"""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "password_confirm": "differentpassword",
        }

        response = self.client.post(self.signup_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Passwords don't match" in str(response.data)

    def test_signup_missing_required_fields(self):
        """Test signup fails when required fields are missing"""
        data = {
            "email": "test@example.com",
            # missing username, password, password_confirm
        }

        response = self.client.post(self.signup_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_duplicate_email(self):
        """Test signup fails with duplicate email"""
        # Create a user first
        User.objects.create_user(
            email="test@example.com", username="existinguser", password="password123"
        )

        data = {
            "email": "test@example.com",  # Same email
            "username": "newuser",
            "password": "testpassword123",
            "password_confirm": "testpassword123",
        }

        response = self.client.post(self.signup_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_duplicate_username(self):
        """Test signup fails with duplicate username"""
        # Create a user first
        User.objects.create_user(
            email="existing@example.com", username="testuser", password="password123"
        )

        data = {
            "email": "new@example.com",
            "username": "testuser",  # Same username
            "password": "testpassword123",
            "password_confirm": "testpassword123",
        }

        response = self.client.post(self.signup_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestMagicLinkLoginAPI:
    def setup_method(self):
        self.client = APIClient()
        self.magic_link_url = reverse("magic-link-login")

    def test_magic_link_missing_email(self):
        """Test magic link fails when email is not provided"""
        data = {}

        response = self.client.post(self.magic_link_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_magic_link_invalid_email_format(self):
        """Test magic link fails with invalid email format"""
        data = {"email": "invalid-email"}

        response = self.client.post(self.magic_link_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    @patch("users.views.send_mail")
    def test_magic_link_existing_user_success(self, mock_send_mail):
        """Test magic link success for existing user"""
        # Create an existing user
        existing_user = User.objects.create_user(
            email="existing@example.com", username="existing", password="password123"
        )

        data = {"email": "existing@example.com"}

        response = self.client.post(self.magic_link_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Magic link sent to your email"

        # Verify email was sent
        mock_send_mail.assert_called_once()

        # Verify token was created
        token = MagicLinkToken.objects.get(user=existing_user)
        assert token.user == existing_user
        assert token.expires_at > timezone.now()

    @patch("users.views.send_mail")
    def test_magic_link_new_user_creation(self, mock_send_mail):
        """Test magic link creates new user when doesn't exist"""
        data = {"email": "newuser@example.com"}

        # Verify user doesn't exist
        assert not User.objects.filter(email="newuser@example.com").exists()

        response = self.client.post(self.magic_link_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Magic link sent to your email"

        # Verify new user was created
        new_user = User.objects.get(email="newuser@example.com")
        assert new_user.username == "newuser"  # Username extracted from email

        # Verify email was sent
        mock_send_mail.assert_called_once()

        # Verify token was created
        token = MagicLinkToken.objects.get(user=new_user)
        assert token.user == new_user

    @patch("users.views.send_mail")
    def test_magic_link_username_extraction(self, mock_send_mail):
        """Test username is correctly extracted from email"""
        data = {"email": "john.doe+test@example.com"}

        response = self.client.post(self.magic_link_url, data)

        assert response.status_code == status.HTTP_200_OK

        # Verify username extraction
        user = User.objects.get(email="john.doe+test@example.com")
        assert user.username == "john.doe+test"

    @patch("users.views.send_mail", side_effect=Exception("Email service down"))
    def test_magic_link_email_service_failure(self, mock_send_mail):
        """Test magic link handles email service failures"""
        data = {"email": "test@example.com"}

        response = self.client.post(self.magic_link_url, data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["error"] == "Failed to send magic link email"


@pytest.mark.django_db
class TestMagicLinkVerifyAPI:
    def setup_method(self):
        self.client = APIClient()
        self.verify_url = reverse("magic-link-verify")
        self.test_user = User.objects.create_user(
            email="test@example.com", username="testuser", fullname="Test User"
        )

    def test_verify_missing_token(self):
        """Test verify fails when token is not provided"""
        data = {}

        response = self.client.post(self.verify_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" in response.data

    def test_verify_empty_token(self):
        """Test verify fails when token is empty"""
        data = {"token": ""}

        response = self.client.post(self.verify_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" in response.data

    def test_verify_invalid_token(self):
        """Test verify fails with non-existent token"""
        # Use a properly formatted UUID that doesn't exist in database
        data = {"token": "12345678-1234-5678-9abc-123456789abc"}

        response = self.client.post(self.verify_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid or expired magic link."

    def test_verify_invalid_uuid_format(self):
        """Test verify fails with invalid UUID format"""
        data = {"token": "invalid-token-12345"}

        response = self.client.post(self.verify_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" in response.data
        assert "Invalid token format" in str(response.data["token"])

    def test_verify_expired_token(self):
        """Test verify fails with expired token"""
        # Create an expired token
        expired_token = MagicLinkToken.objects.create(
            user=self.test_user,
            expires_at=timezone.now() - timedelta(minutes=5),  # Expired 5 minutes ago
        )

        data = {"token": str(expired_token.token)}

        response = self.client.post(self.verify_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid or expired magic link."

        # Verify token still exists (not deleted for expired tokens)
        assert MagicLinkToken.objects.filter(id=expired_token.id).exists()

    def test_verify_valid_token_success(self):
        """Test verify succeeds with valid token"""
        # Create a valid token
        valid_token = MagicLinkToken.objects.create(
            user=self.test_user, expires_at=timezone.now() + timedelta(minutes=15)
        )

        data = {"token": str(valid_token.token)}

        response = self.client.post(self.verify_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "refresh" in response.data
        assert "access" in response.data
        assert "user" in response.data

        # Verify user data in response
        user_data = response.data["user"]
        assert user_data["id"] == str(self.test_user.pk)
        assert user_data["email"] == self.test_user.email
        assert user_data["username"] == self.test_user.username
        assert user_data["fullname"] == self.test_user.fullname

        # Verify token was deleted (single-use)
        assert not MagicLinkToken.objects.filter(id=valid_token.id).exists()

    def test_verify_token_single_use(self):
        """Test token can only be used once"""
        # Create a valid token
        valid_token = MagicLinkToken.objects.create(
            user=self.test_user, expires_at=timezone.now() + timedelta(minutes=15)
        )

        data = {"token": str(valid_token.token)}

        # First request should succeed
        response1 = self.client.post(self.verify_url, data)
        assert response1.status_code == status.HTTP_200_OK

        # Second request with same token should fail
        response2 = self.client.post(self.verify_url, data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert response2.data["detail"] == "Invalid or expired magic link."

    def test_verify_jwt_tokens_validity(self):
        """Test that returned JWT tokens are valid"""
        # Create a valid token
        valid_token = MagicLinkToken.objects.create(
            user=self.test_user, expires_at=timezone.now() + timedelta(minutes=15)
        )

        data = {"token": str(valid_token.token)}

        response = self.client.post(self.verify_url, data)

        assert response.status_code == status.HTTP_200_OK

        # Verify JWT tokens are not empty and have expected format
        refresh_token = response.data["refresh"]
        access_token = response.data["access"]

        assert len(refresh_token) > 50  # JWT tokens are typically long
        assert len(access_token) > 50
        assert refresh_token.count(".") == 2  # JWT format: header.payload.signature
        assert access_token.count(".") == 2
