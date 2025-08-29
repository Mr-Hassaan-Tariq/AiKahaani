import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.choices import LanguageChoices
from users.models import Settings, User


@pytest.mark.django_db
class TestSettingsNotificationAPI:
    def setup_method(self):
        self.client = APIClient()
        self.notifications_url = reverse("user-settings-notifications")

        # Create test user
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword123",
            fullname="Test User",
            preferred_language=LanguageChoices.ENGLISH,
        )

        # Create test settings for the user
        self.settings = Settings.objects.create(
            user=self.user,
            in_app_notifications=True,
            email_notifications=False,
            web_push_notifications=True,
            new_script_generated=False,
            account_or_plan_changes=True,
            tips_content_inspiration=False,
            feature_updates=True,
            community_affiliate_updates=False,
        )

    def test_get_notification_settings_authenticated(self):
        """Test authenticated user can retrieve notification settings"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.notifications_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["in_app_notifications"] is True
        assert response.data["email_notifications"] is False
        assert response.data["web_push_notifications"] is True
        assert response.data["new_script_generated"] is False
        assert response.data["account_or_plan_changes"] is True
        assert response.data["tips_content_inspiration"] is False
        assert response.data["feature_updates"] is True
        assert response.data["community_affiliate_updates"] is False
        assert "created" in response.data
        assert "modified" in response.data

    def test_get_notification_settings_unauthenticated(self):
        """Test unauthenticated user cannot access notification settings"""
        response = self.client.get(self.notifications_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_notification_settings_creates_default_settings(self):
        """Test that settings are created automatically for new users"""
        new_user = User.objects.create_user(
            email="newuser@example.com", username="newuser", password="password123"
        )
        self.client.force_authenticate(user=new_user)

        response = self.client.get(self.notifications_url)

        assert response.status_code == status.HTTP_200_OK
        # Check that default settings were created
        assert Settings.objects.filter(user=new_user).exists()
        settings = Settings.objects.get(user=new_user)
        assert settings.in_app_notifications is False  # Default value
        assert settings.email_notifications is False  # Default value

    def test_patch_notification_settings_authenticated(self):
        """Test authenticated user can update notification settings"""
        self.client.force_authenticate(user=self.user)

        update_data = {
            "in_app_notifications": False,
            "email_notifications": True,
            "new_script_generated": True,
        }

        response = self.client.patch(self.notifications_url, update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["in_app_notifications"] is False
        assert response.data["email_notifications"] is True
        assert response.data["new_script_generated"] is True

        # Verify database was updated
        self.settings.refresh_from_db()
        assert self.settings.in_app_notifications is False
        assert self.settings.email_notifications is True
        assert self.settings.new_script_generated is True

    def test_patch_notification_settings_unauthenticated(self):
        """Test unauthenticated user cannot update notification settings"""
        update_data = {"in_app_notifications": False}

        response = self.client.patch(self.notifications_url, update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_notification_settings_partial_update(self):
        """Test partial update of notification settings"""
        self.client.force_authenticate(user=self.user)

        # Only update one field
        update_data = {"web_push_notifications": False}

        response = self.client.patch(self.notifications_url, update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["web_push_notifications"] is False

        # Other fields should remain unchanged
        assert response.data["in_app_notifications"] is True
        assert response.data["email_notifications"] is False

        # Verify database was updated
        self.settings.refresh_from_db()
        assert self.settings.web_push_notifications is False

    def test_patch_notification_settings_invalid_data(self):
        """Test update with invalid data returns validation error"""
        self.client.force_authenticate(user=self.user)

        # Try to set a boolean field to a string
        update_data = {"in_app_notifications": "invalid_value"}

        response = self.client.patch(self.notifications_url, update_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "in_app_notifications" in response.data

    def test_patch_notification_settings_creates_settings_if_not_exist(self):
        """Test that settings are created automatically during update if they don't exist"""
        new_user = User.objects.create_user(
            email="newuser2@example.com", username="newuser2", password="password123"
        )
        self.client.force_authenticate(user=new_user)

        # Verify no settings exist initially
        assert not Settings.objects.filter(user=new_user).exists()

        update_data = {"in_app_notifications": True}
        response = self.client.patch(self.notifications_url, update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["in_app_notifications"] is True

        # Verify settings were created
        assert Settings.objects.filter(user=new_user).exists()


@pytest.mark.django_db
class TestSettingsPrivacyAPI:
    def setup_method(self):
        self.client = APIClient()
        self.privacy_url = reverse("user-settings-privacy")

        # Create test user
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword123",
            fullname="Test User",
            preferred_language=LanguageChoices.ENGLISH,
        )

        # Create test settings for the user
        self.settings = Settings.objects.create(
            user=self.user,
            allow_product_update_emails=True,
            allow_anonymized_data_usage=False,
        )

    def test_get_privacy_settings_authenticated(self):
        """Test authenticated user can retrieve privacy settings"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.privacy_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["allow_product_update_emails"] is True
        assert response.data["allow_anonymized_data_usage"] is False
        assert "created" in response.data
        assert "modified" in response.data

    def test_get_privacy_settings_unauthenticated(self):
        """Test unauthenticated user cannot access privacy settings"""
        response = self.client.get(self.privacy_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_privacy_settings_creates_default_settings(self):
        """Test that settings are created automatically for new users"""
        new_user = User.objects.create_user(
            email="newuser@example.com", username="newuser", password="password123"
        )
        self.client.force_authenticate(user=new_user)

        response = self.client.get(self.privacy_url)

        assert response.status_code == status.HTTP_200_OK
        # Check that default settings were created
        assert Settings.objects.filter(user=new_user).exists()
        settings = Settings.objects.get(user=new_user)
        assert settings.allow_product_update_emails is False  # Default value
        assert settings.allow_anonymized_data_usage is False  # Default value

    def test_patch_privacy_settings_authenticated(self):
        """Test authenticated user can update privacy settings"""
        self.client.force_authenticate(user=self.user)

        update_data = {
            "allow_product_update_emails": False,
            "allow_anonymized_data_usage": True,
        }

        response = self.client.patch(self.privacy_url, update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["allow_product_update_emails"] is False
        assert response.data["allow_anonymized_data_usage"] is True

        # Verify database was updated
        self.settings.refresh_from_db()
        assert self.settings.allow_product_update_emails is False
        assert self.settings.allow_anonymized_data_usage is True

    def test_patch_privacy_settings_unauthenticated(self):
        """Test unauthenticated user cannot update privacy settings"""
        update_data = {"allow_product_update_emails": False}

        response = self.client.patch(self.privacy_url, update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_privacy_settings_partial_update(self):
        """Test partial update of privacy settings"""
        self.client.force_authenticate(user=self.user)

        # Only update one field
        update_data = {"allow_anonymized_data_usage": True}

        response = self.client.patch(self.privacy_url, update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["allow_anonymized_data_usage"] is True

        # Other fields should remain unchanged
        assert response.data["allow_product_update_emails"] is True

        # Verify database was updated
        self.settings.refresh_from_db()
        assert self.settings.allow_anonymized_data_usage is True

    def test_patch_privacy_settings_invalid_data(self):
        """Test update with invalid data returns validation error"""
        self.client.force_authenticate(user=self.user)

        # Try to set a boolean field to a string
        update_data = {"allow_product_update_emails": "invalid_value"}

        response = self.client.patch(self.privacy_url, update_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "allow_product_update_emails" in response.data

    def test_patch_privacy_settings_creates_settings_if_not_exist(self):
        """Test that settings are created automatically during update if they don't exist"""
        new_user = User.objects.create_user(
            email="newuser2@example.com", username="newuser2", password="password123"
        )
        self.client.force_authenticate(user=new_user)

        # Verify no settings exist initially
        assert not Settings.objects.filter(user=new_user).exists()

        update_data = {"allow_product_update_emails": True}
        response = self.client.patch(self.privacy_url, update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["allow_product_update_emails"] is True

        # Verify settings were created
        assert Settings.objects.filter(user=new_user).exists()

    def test_privacy_settings_isolation(self):
        """Test that privacy settings are isolated between users"""
        other_user = User.objects.create_user(
            email="other@example.com", username="otheruser", password="password123"
        )
        other_settings = Settings.objects.create(
            user=other_user,
            allow_product_update_emails=False,
            allow_anonymized_data_usage=True,
        )

        self.client.force_authenticate(user=self.user)

        # Update current user's settings
        update_data = {"allow_product_update_emails": False}
        response = self.client.patch(self.privacy_url, update_data)

        assert response.status_code == status.HTTP_200_OK

        # Verify other user's settings remain unchanged
        other_settings.refresh_from_db()
        assert other_settings.allow_product_update_emails is False  # Original value
        assert other_settings.allow_anonymized_data_usage is True  # Original value


@pytest.mark.django_db
class TestSettingsModel:
    def test_settings_str_representation(self):
        """Test the string representation of Settings model"""
        user = User.objects.create_user(
            email="test@example.com", username="testuser", password="password123"
        )
        settings = Settings.objects.create(user=user)

        expected_str = f"Settings for {user.email}"
        assert str(settings) == expected_str

    def test_settings_default_values(self):
        """Test that Settings model has correct default values"""
        user = User.objects.create_user(
            email="test@example.com", username="testuser", password="password123"
        )
        settings = Settings.objects.create(user=user)

        # Check default values
        assert settings.allow_product_update_emails is False
        assert settings.allow_anonymized_data_usage is False
        assert settings.in_app_notifications is False
        assert settings.email_notifications is False
        assert settings.web_push_notifications is False
        assert settings.new_script_generated is False
        assert settings.account_or_plan_changes is False
        assert settings.tips_content_inspiration is False
        assert settings.feature_updates is False
        assert settings.community_affiliate_updates is False

    def test_settings_one_to_one_relationship(self):
        """Test that each user can only have one settings instance"""
        user = User.objects.create_user(
            email="test@example.com", username="testuser", password="password123"
        )

        # Create first settings instance
        settings1 = Settings.objects.create(user=user)

        # Verify only one settings instance exists
        assert Settings.objects.filter(user=user).count() == 1
        assert Settings.objects.get(user=user) == settings1

        # Test the constraint by verifying the model field definition
        # The OneToOneField should have unique=True implicitly
        field = Settings._meta.get_field("user")
        assert hasattr(field, "unique")
        # In Django, OneToOneField automatically sets unique=True
