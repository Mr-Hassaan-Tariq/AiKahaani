from djstripe.models import Plan, Product, Subscription
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import SubscriptionPlan


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


@extend_schema_field(OpenApiTypes.STR)
class TrialExpirationDateField(serializers.ReadOnlyField):
    """Custom field for trial_expiration_date with proper type hint"""

    pass


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""

    display_price = DisplayPriceField()
    yearly_price = YearlyPriceField()
    monthly_price = MonthlyPriceField()

    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "plan_type",
            "billing_cycle",
            "price",
            "display_price",
            "yearly_price",
            "monthly_price",
            "features",
            "is_active",
            "trial_days",
            "description",
            "sort_order",
            "created",
            "modified",
        ]
        read_only_fields = ["id", "created", "modified"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class PlanSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Plan
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()

    class Meta:
        model = Subscription
        fields = "__all__"


class TrialStatusSerializer(serializers.Serializer):
    """Serializer for trial status endpoint"""

    is_trial = serializers.BooleanField(
        help_text="Whether user has an active trial subscription"
    )
    trial_days_remaining = serializers.IntegerField(
        help_text="Number of trial days remaining"
    )
    trial_expiration_date = serializers.CharField(
        allow_null=True, help_text="Trial expiration date in ISO format"
    )
    trial_start_date = serializers.DateTimeField(
        allow_null=True, help_text="Trial start date"
    )
    plan_name = serializers.CharField(
        allow_null=True, help_text="Name of the trial plan"
    )
    plan_type = serializers.CharField(
        allow_null=True, help_text="Type of the plan (trial, basic, pro)"
    )
    status = serializers.CharField(allow_null=True, help_text="Subscription status")
