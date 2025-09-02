from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from decimal import Decimal

from .models import SubscriptionPlan, UserSubscription, PaymentHistory


@extend_schema_field(OpenApiTypes.STR)
class DisplayPriceField(serializers.ReadOnlyField):
    """Custom field for display_price with proper type hint"""
    pass


@extend_schema_field(OpenApiTypes.DECIMAL)
class YearlyPriceField(serializers.ReadOnlyField):
    """Custom field for yearly_price with proper type hint"""
    pass


@extend_schema_field(OpenApiTypes.DECIMAL)
class MonthlyPriceField(serializers.ReadOnlyField):
    """Custom field for monthly_price with proper type hint"""
    pass


@extend_schema_field(OpenApiTypes.BOOL)
class IsActiveField(serializers.ReadOnlyField):
    """Custom field for is_active with proper type hint"""
    pass


@extend_schema_field(OpenApiTypes.BOOL)
class IsTrialField(serializers.ReadOnlyField):
    """Custom field for is_trial with proper type hint"""
    pass


@extend_schema_field(OpenApiTypes.INT)
class DaysUntilExpiryField(serializers.ReadOnlyField):
    """Custom field for days_until_expiry with proper type hint"""
    pass


@extend_schema_field(OpenApiTypes.INT)
class TrialDaysRemainingField(serializers.ReadOnlyField):
    """Custom field for trial_days_remaining with proper type hint"""
    pass


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""
    display_price = DisplayPriceField()
    yearly_price = YearlyPriceField()
    monthly_price = MonthlyPriceField()
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'billing_cycle', 'price', 
            'display_price', 'yearly_price', 'monthly_price',
            'features', 'is_active', 'trial_days', 'description', 
            'sort_order', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions"""
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.UUIDField(write_only=True)
    is_active = IsActiveField()
    is_trial = IsTrialField()
    days_until_expiry = DaysUntilExpiryField()
    trial_days_remaining = TrialDaysRemainingField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'plan', 'plan_id', 'stripe_subscription_id',
            'stripe_customer_id', 'status', 'current_period_start',
            'current_period_end', 'trial_start', 'trial_end',
            'canceled_at', 'cancel_at_period_end', 'is_active',
            'is_trial', 'days_until_expiry', 'trial_days_remaining',
            'created', 'modified'
        ]
        read_only_fields = [
            'id', 'user', 'stripe_subscription_id', 'stripe_customer_id',
            'current_period_start', 'current_period_end', 'trial_start',
            'trial_end', 'canceled_at', 'created', 'modified'
        ]


class PaymentHistorySerializer(serializers.ModelSerializer):
    """Serializer for payment history"""
    subscription = UserSubscriptionSerializer(read_only=True)
    
    class Meta:
        model = PaymentHistory
        fields = [
            'id', 'user', 'subscription', 'amount', 'currency',
            'stripe_payment_intent_id', 'stripe_invoice_id', 'status',
            'description', 'metadata', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer for creating a new subscription"""
    plan_id = serializers.UUIDField()
    billing_cycle = serializers.ChoiceField(choices=SubscriptionPlan.BILLING_CYCLES)
    payment_method_id = serializers.CharField(required=False, help_text="Stripe payment method ID")
