"""
Affiliate tracking views for Tolt integration.

ULTRA-MINIMAL IMPLEMENTATION:
- No database saves, just API calls to Tolt
- All data stored in User model (tolt_customer_id, tolt_partner_id)
- Stripe webhook calls report_transaction directly
- If Tolt API fails, Stripe will retry the webhook (Stripe's responsibility)

Endpoints:
1. POST /track-referral-click/ - Track referral clicks from landing page
2. POST /create-customer/ - Create Tolt customer when user signs up
3. report_transaction_to_tolt() - Helper function called from Stripe webhook (not an endpoint)
"""

import logging

from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import (
    TrackClickRequestSerializer,
    TrackClickResponseSerializer,
    CreateCustomerRequestSerializer,
    CreateCustomerResponseSerializer,
)
from .services import ToltAPIClient

logger = logging.getLogger(__name__)


@extend_schema(
    summary="Track referral click",
    description="Track when a user clicks a referral link. Returns partner_id to store in frontend.",
    request=TrackClickRequestSerializer,
    responses={
        200: TrackClickResponseSerializer,
        400: OpenApiResponse(description="Invalid request data"),
        503: OpenApiResponse(description="Tolt API unavailable"),
    },
    tags=["Affiliates"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def track_referral_click(request: Request) -> Response:
    """
    Track a referral link click.
    
    POST /api/v1/affiliates/click/
    
    Frontend calls this when user lands on site with ?ref=ABC123
    Returns partner_id which frontend stores in localStorage.
    
    No database save - just API call to Tolt.
    """
    serializer = TrackClickRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    referral_code = serializer.validated_data["referral_code"]
    page_url = serializer.validated_data["page_url"]
    device_type = serializer.validated_data.get("device_type", "desktop")
    
    try:
        # Initialize Tolt client
        tolt_client = ToltAPIClient(
            api_key=settings.TOLT_API_KEY,
            base_url=settings.TOLT_API_BASE_URL
        )
        
        # Call Tolt API
        tolt_response = tolt_client.track_click(
            referral_code=referral_code,
            page_url=page_url,
            device_type=device_type
        )
        
        partner_id = tolt_response.get("partner_id")
        
        if not partner_id:
            logger.error("[AFFILIATES] No partner_id in Tolt response")
            return Response(
                {"error": "Invalid referral code"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"[AFFILIATES] Click tracked: {referral_code} → {partner_id}")
        
        return Response({
            "partner_id": partner_id,
            "referral_code": referral_code,
            "message": "Click tracked successfully"
        })
        
    except Exception as e:
        logger.error(f"[AFFILIATES] Error tracking click: {str(e)}")
        return Response(
            {"error": "Failed to track referral click"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


def create_tolt_customer(user, partner_id: str) -> dict:
    """
    Create a Tolt customer (link user to referrer) - INTERNAL HELPER FUNCTION.
    
    This is called from the user signup flow in users app.
    NOT an API endpoint - just a utility function.
    
    Args:
        user: Django User instance
        partner_id: Tolt partner ID from referral click
    
    Returns:
        dict: {
            "success": bool,
            "tolt_customer_id": str (if success),
            "error": str (if failed)
        }
    
    Usage in users/views.py signup:
    ```python
    from affiliates.views import create_tolt_customer
    
    # After user is created
    partner_id = request.data.get("partner_id")  # From frontend
    if partner_id:
        result = create_tolt_customer(user, partner_id)
        if result["success"]:
            # tolt_customer_id and partner_id already saved to user
            logger.info(f"Tolt customer created: {result['tolt_customer_id']}")
    ```
    """
    try:
        # Check if user already has Tolt customer ID
        if user.tolt_customer_id:
            return {
                "success": False,
                "error": "Customer already exists"
            }
        
        # Initialize Tolt client
        tolt_client = ToltAPIClient(
            api_key=settings.TOLT_API_KEY,
            base_url=settings.TOLT_API_BASE_URL
        )
        
        # Call Tolt API to create customer
        tolt_response = tolt_client.create_customer(
            email=user.email,
            partner_id=partner_id,
            customer_id=str(user.id)  # Use Django user ID
        )
        
        # Tolt returns: { "id": "cust_...", "email": "...", ... }
        tolt_customer_id = tolt_response.get("id")
        
        if not tolt_customer_id:
            logger.error(f"[AFFILIATES] No customer id in Tolt response: {tolt_response}")
            return {
                "success": False,
                "error": "Failed to create customer in Tolt"
            }
        
        # Save to User model
        user.tolt_customer_id = tolt_customer_id
        user.tolt_partner_id = partner_id
        user.save(update_fields=["tolt_customer_id", "tolt_partner_id"])
        
        logger.info(f"[AFFILIATES] Customer created: {user.email} → {tolt_customer_id}")
        
        return {
            "success": True,
            "tolt_customer_id": tolt_customer_id,
            "partner_id": partner_id
        }
        
    except Exception as e:
        logger.error(f"[AFFILIATES] Error creating customer: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def report_transaction_to_tolt(
    user,
    charge_id: str,
    amount: int,
    product_name: str,
    billing_type: str = "subscription",
    interval: str = "month"
) -> bool:
    """
    Report a transaction to Tolt (internal helper function).
    
    This is called from Stripe webhook handler in payments app.
    NOT an API endpoint - just a utility function.
    
    Args:
        user: Django User instance
        charge_id: Stripe charge/payment intent ID
        amount: Amount in cents
        product_name: Product/plan name
        billing_type: "subscription" or "one_time"
        interval: "month", "year", "week", etc.
    
    Returns:
        bool: True if successful, False otherwise
    
    Usage in Stripe webhook:
    ```python
    from affiliates.views import report_transaction_to_tolt
    
    # After successful payment
    success = report_transaction_to_tolt(
        user=user,
        charge_id="ch_123",
        amount=9999,
        product_name="Pro Plan"
    )
    ```
    """
    try:
        # Check if user has Tolt customer ID
        if not user.tolt_customer_id:
            logger.info(f"[AFFILIATES] User {user.email} has no referrer, skipping Tolt")
            return False
        
        # Initialize Tolt client
        tolt_client = ToltAPIClient(
            api_key=settings.TOLT_API_KEY,
            base_url=settings.TOLT_API_BASE_URL
        )
        
        # Call Tolt API
        tolt_response = tolt_client.report_transaction(
            customer_id=user.tolt_customer_id,
            amount=amount,
            charge_id=charge_id,
            billing_type=billing_type,
            product_name=product_name,
            interval=interval
        )
        
        logger.info(
            f"[AFFILIATES] ✅ Transaction reported to Tolt: "
            f"ID: {tolt_response.get('id')} - "
            f"Status: {tolt_response.get('status')} - "
            f"Amount: ${amount/100:.2f} - "
            f"Partner: {tolt_response.get('partner_id')}"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"[AFFILIATES] Failed to report transaction: {str(e)}")
        # Stripe will retry the webhook, so Tolt will get another chance
        return False
