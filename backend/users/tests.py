import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import User


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
