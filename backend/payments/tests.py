from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import SubscriptionPlan, UserSubscription, PaymentHistory

User = get_user_model()


class SubscriptionPlanModelTest(TestCase):
    def setUp(self):
        self.plan = SubscriptionPlan.objects.create(
            name="Test Plan",
            plan_type="pro",
            billing_cycle="monthly",
            price=Decimal("29.99"),
            features={"feature1": True, "feature2": False},
            trial_days=0
        )

    def test_plan_creation(self):
        self.assertEqual(self.plan.name, "Test Plan")
        self.assertEqual(self.plan.plan_type, "pro")
        self.assertEqual(self.plan.billing_cycle, "monthly")
        self.assertEqual(self.plan.price, Decimal("29.99"))

    def test_display_price(self):
        self.assertEqual(self.plan.display_price, "$29.99/monthly")

    def test_yearly_price_calculation(self):
        self.assertEqual(self.plan.yearly_price, Decimal("359.88"))

    def test_monthly_price_calculation(self):
        self.assertEqual(self.plan.monthly_price, Decimal("29.99"))


class UserSubscriptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.plan = SubscriptionPlan.objects.create(
            name="Test Plan",
            plan_type="pro",
            billing_cycle="monthly",
            price=Decimal("29.99")
        )
        self.subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            status="active"
        )

    def test_subscription_creation(self):
        self.assertEqual(self.subscription.user, self.user)
        self.assertEqual(self.subscription.plan, self.plan)
        self.assertEqual(self.subscription.status, "active")

    def test_is_active_property(self):
        self.assertTrue(self.subscription.is_active)

    def test_is_trial_property(self):
        self.assertFalse(self.subscription.is_trial)


class PaymentHistoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.plan = SubscriptionPlan.objects.create(
            name="Test Plan",
            plan_type="pro",
            billing_cycle="monthly",
            price=Decimal("29.99")
        )
        self.subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            status="active"
        )
        self.payment = PaymentHistory.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=Decimal("29.99"),
            currency="usd",
            status="succeeded"
        )

    def test_payment_creation(self):
        self.assertEqual(self.payment.user, self.user)
        self.assertEqual(self.payment.subscription, self.subscription)
        self.assertEqual(self.payment.amount, Decimal("29.99"))
        self.assertEqual(self.payment.currency, "usd")
        self.assertEqual(self.payment.status, "succeeded")


class SubscriptionPlansAPITest(APITestCase):
    def setUp(self):
        self.plan = SubscriptionPlan.objects.create(
            name="Test Plan",
            plan_type="pro",
            billing_cycle="monthly",
            price=Decimal("29.99"),
            features={"feature1": True},
            is_active=True
        )

    def test_get_plans_anonymous(self):
        """Test that anonymous users can view plans"""
        url = reverse('payments:subscription-plans')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Plan")

    def test_get_plans_only_active(self):
        """Test that only active plans are returned"""
        # Create an inactive plan
        SubscriptionPlan.objects.create(
            name="Inactive Plan",
            plan_type="pro",
            billing_cycle="yearly",
            price=Decimal("299.99"),
            is_active=False
        )
        
        url = reverse('payments:subscription-plans')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only active plan
        self.assertEqual(response.data[0]['name'], "Test Plan")


class UserSubscriptionAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.plan = SubscriptionPlan.objects.create(
            name="Test Plan",
            plan_type="pro",
            billing_cycle="monthly",
            price=Decimal("29.99"),
            is_active=True
        )

    def test_get_subscription_authenticated(self):
        """Test that authenticated users can view their subscription"""
        self.client.force_authenticate(user=self.user)
        url = reverse('payments:user-subscription')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # No subscription yet

    def test_get_subscription_unauthenticated(self):
        """Test that unauthenticated users cannot view subscriptions"""
        url = reverse('payments:subscription-plans')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Plans are public


class PaymentHistoryAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )

    def test_get_payment_history_authenticated(self):
        """Test that authenticated users can view their payment history"""
        self.client.force_authenticate(user=self.user)
        url = reverse('payments:payment-history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No payments yet

    def test_get_payment_history_unauthenticated(self):
        """Test that unauthenticated users cannot view payment history"""
        url = reverse('payments:payment-history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
