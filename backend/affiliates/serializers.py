"""
Serializers for affiliate/Tolt API endpoints.

In Node.js/Express, this is like using Joi or Zod for validation:
```javascript
const trackClickSchema = z.object({
    referralCode: z.string(),
    pageUrl: z.string().url(),
    deviceType: z.enum(['desktop', 'mobile', 'tablet'])
});
```
"""

from rest_framework import serializers


class TrackClickRequestSerializer(serializers.Serializer):
    """
    Request body for tracking a referral click.
    
    POST /api/v1/affiliates/click
    """
    referral_code = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Referral code from URL (e.g., ?ref=ABC123)"
    )
    page_url = serializers.URLField(
        required=True,
        help_text="Full URL where click occurred"
    )
    device_type = serializers.ChoiceField(
        choices=["desktop", "mobile", "tablet"],
        default="desktop",
        required=False
    )


class TrackClickResponseSerializer(serializers.Serializer):
    """Response from affiliate click endpoint"""
    partner_id = serializers.CharField(help_text="Tolt partner ID")
    referral_code = serializers.CharField()
    message = serializers.CharField()


class CreateCustomerRequestSerializer(serializers.Serializer):
    """
    Request body for creating a Tolt customer.
    
    Called during user signup if they came from a referral.
    """
    partner_id = serializers.CharField(
        required=True,
        help_text="Tolt partner ID from affiliate click response"
    )


class CreateCustomerResponseSerializer(serializers.Serializer):
    """Response from create-customer endpoint"""
    tolt_customer_id = serializers.CharField(help_text="Tolt's customer ID")
    partner_id = serializers.CharField()
    message = serializers.CharField()


class ReportTransactionRequestSerializer(serializers.Serializer):
    """
    Request body for reporting a transaction.
    
    Usually called internally from Stripe webhook, not directly by frontend.
    """
    charge_id = serializers.CharField(
        required=True,
        help_text="Stripe charge/payment intent ID"
    )
    amount = serializers.IntegerField(
        required=True,
        min_value=0,
        help_text="Amount in cents"
    )
    product_name = serializers.CharField(
        required=True,
        help_text="Product/plan name"
    )
    billing_type = serializers.ChoiceField(
        choices=["subscription", "one_time"],
        default="subscription",
        required=False
    )
    interval = serializers.ChoiceField(
        choices=["month", "year", "week", "one_time"],
        required=False,
        allow_null=True
    )


class ReportTransactionResponseSerializer(serializers.Serializer):
    """Response from report-transaction endpoint"""
    transaction_id = serializers.CharField()
    credits_awarded = serializers.IntegerField(required=False)
    message = serializers.CharField()


class ReferralStatsSerializer(serializers.Serializer):
    """
    User's referral statistics.
    
    Shows how many people they've referred and conversions.
    """
    total_clicks = serializers.IntegerField()
    total_signups = serializers.IntegerField()
    total_transactions = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    conversion_rate = serializers.FloatField()
