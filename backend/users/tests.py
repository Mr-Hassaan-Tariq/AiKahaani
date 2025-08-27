from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import EmailVerificationToken, MagicLinkToken, User


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


@pytest.mark.django_db
class TestUserDetailsUpdateAPI:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("user-details-update")
        self.user = User.objects.create_user(
            email="user@example.com", username="user", password="password123"
        )

    def test_requires_authentication(self):
        unauth_client = APIClient()
        response = unauth_client.put(self.url, {"fullName": "New Name"}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_requires_authentication(self):
        unauth_client = APIClient()
        response = unauth_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_fullname_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"fullName": "Jane Doe"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.fullname == "Jane Doe"

    def test_get_user_details_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == self.user.email
        assert response.data["username"] == self.user.username

    def test_update_username_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"username": "newusername"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.username == "newusername"

    def test_username_uniqueness_validation(self):
        # Another user with target username
        User.objects.create_user(
            email="other@example.com", username="taken", password="password123"
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"username": "taken"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    def test_email_invalid_format(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            self.url, {"emailAddress": "not-an-email"}, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "emailAddress" in response.data

    def test_email_uniqueness_validation(self):
        User.objects.create_user(
            email="taken@example.com", username="someone", password="password123"
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            self.url, {"emailAddress": "taken@example.com"}, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "emailAddress" in response.data

    def test_preferred_language_invalid(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"preferredLanguage": "xx"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "preferredLanguage" in response.data

    def test_preferred_language_update_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"preferredLanguage": "es"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.preferred_language == "es"

    def test_idempotent_username_update_same_value(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"username": "user"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.username == "user"

    def test_update_fullname_to_blank(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"fullName": ""}, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.fullname == ""

    @patch("users.views.send_mail")
    def test_email_update_triggers_verification(self, mock_send_mail):
        self.client.force_authenticate(user=self.user)
        old_email = self.user.email
        new_email = "new@example.com"
        response = self.client.put(self.url, {"emailAddress": new_email}, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        # Email should not change immediately; remains the old email
        assert self.user.email == old_email

        # Token created
        token_obj = EmailVerificationToken.objects.get(user=self.user)
        # Token currently stores the existing user email
        assert token_obj.email == old_email

        # Email sent and contains verification URL with token
        assert mock_send_mail.called
        args, kwargs = mock_send_mail.call_args
        assert "email-verification?token=" in args[1]
        assert str(token_obj.token) in args[1]

    @patch("users.views.send_mail")
    def test_email_update_clears_previous_tokens(self, mock_send_mail):
        # Existing token for user
        EmailVerificationToken.objects.create(
            user=self.user,
            email="old@example.com",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        self.client.force_authenticate(user=self.user)
        old_email = self.user.email
        response = self.client.put(
            self.url, {"emailAddress": "brandnew@example.com"}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK

        tokens = EmailVerificationToken.objects.filter(user=self.user)
        assert tokens.count() == 1
        # Token stores the current user email (email is not updated yet)
        assert tokens.first().email == old_email

    @patch("users.views.send_mail", side_effect=Exception("SMTP down"))
    def test_email_update_send_mail_failure(self, mock_send_mail):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            self.url, {"emailAddress": "fail@example.com"}, format="json"
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        # Token likely exists since it's created before sending
        assert EmailVerificationToken.objects.filter(user=self.user).exists()


@pytest.mark.django_db
class TestEmailVerificationAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="old@example.com", username="verifyuser", password="password123"
        )

    def _verify_url(self, token):
        return reverse("verify-email", args=[str(token)])

    def test_verify_valid_token_sets_verified(self):
        token_obj = EmailVerificationToken.objects.create(
            user=self.user,
            email="new@example.com",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        response = self.client.get(self._verify_url(token_obj.token))
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.is_email_verified is True
        assert self.user.email == "new@example.com"
        # Token deleted
        assert not EmailVerificationToken.objects.filter(id=token_obj.id).exists()

    def test_verify_nonexistent_token(self):
        response = self.client.get(
            self._verify_url("12345678-1234-5678-9abc-123456789abc")
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired" in response.data.get("detail", "")

    def test_verify_expired_token(self):
        token_obj = EmailVerificationToken.objects.create(
            user=self.user,
            email="new@example.com",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        response = self.client.get(self._verify_url(token_obj.token))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Token remains (optional, but current implementation only rejects)
        assert EmailVerificationToken.objects.filter(id=token_obj.id).exists()

    def test_verify_token_single_use(self):
        token_obj = EmailVerificationToken.objects.create(
            user=self.user,
            email="new@example.com",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        # First use
        response1 = self.client.get(self._verify_url(token_obj.token))
        assert response1.status_code == status.HTTP_200_OK
        # Second use should fail
        response2 = self.client.get(self._verify_url(token_obj.token))
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_applies_token_email_if_user_changed_again(self):
        token_obj = EmailVerificationToken.objects.create(
            user=self.user,
            email="token@example.com",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        # User email changed after token creation
        self.user.email = "changed-later@example.com"
        self.user.save()

        response = self.client.get(self._verify_url(token_obj.token))
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.email == "token@example.com"
        assert self.user.is_email_verified is True
