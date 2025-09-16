import logging

import stripe
from django.conf import settings
from djstripe.models import Subscription
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.mixins import MethodSpecificThrottleMixin

from .models import SubscriptionPlan
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    TrialStatusSerializer,
)
from .utils import (
    # resolve_price,
    VALID_SUB_STATUSES,
    ensure_single_active_subscription,
    get_or_create_customer,
)
from .webhooks import sync_plans_from_djstripe

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


class SubscriptionPlansView(MethodSpecificThrottleMixin, APIView):
    """View to fetch all available subscription plans"""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Get all subscription plans",
        description="Retrieve all active subscription plans with their features and pricing",
        responses={
            200: OpenApiResponse(
                description="List of subscription plans",
                response=SubscriptionPlanSerializer(many=True),
            )
        },
        tags=["Subscription Plans"],
    )
    def get(self, request):
        """GET /api/plans - Fetch all active subscription plans"""
        try:
            sync_plans_from_djstripe()
            plans = SubscriptionPlan.objects.filter(is_active=True).order_by(
                "sort_order", "name"
            )
            serializer = SubscriptionPlanSerializer(plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching subscription plans: {str(e)}")
            return Response(
                {"error": "Failed to fetch subscription plans"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserSubscriptionView(MethodSpecificThrottleMixin, APIView):
    """View to manage user subscriptions"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user subscription",
        description="Retrieve the current user's subscription details",
        responses={
            200: OpenApiResponse(
                description="User subscription details",
                response=SubscriptionSerializer,
            ),
            404: OpenApiResponse(description="No subscription found"),
        },
        tags=["User Subscriptions"],
    )
    def get(self, request):
        customer = get_or_create_customer(request.user)
        sub = (
            Subscription.objects.filter(
                customer=customer, status__in=VALID_SUB_STATUSES
            )
            .order_by("-created")
            .first()
        )
        if not sub:
            return Response({"subscription": None})

        return Response(SubscriptionSerializer(sub).data)


class CreateCheckoutSessionView(MethodSpecificThrottleMixin, APIView):
    """Create a Stripe Checkout Session using dj-stripe."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create Stripe Checkout Session",
        description=(
            "Create a subscription Checkout Session for the given Plan ID. "
            "Uses the local SubscriptionPlan model to find the associated Stripe Price and create the Session."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The UUID of the subscription plan",
                        "example": "7ca467f6-ac3d-4580-996a-a79c8756b2d1",
                    }
                },
                "required": ["plan_id"],
            }
        },
        responses={
            200: OpenApiResponse(description="Checkout session created"),
            400: OpenApiResponse(
                description="Invalid request, plan id, or user has active subscription"
            ),
        },
        tags=["Stripe Checkout"],
    )
    def post(self, request):
        plan_id = request.data.get("plan_id")
        if not plan_id:
            return Response(
                {"error": "Plan ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        customer = get_or_create_customer(request.user)

        # Enforce "one active subscription per user"
        active_sub = ensure_single_active_subscription(customer)
        if active_sub:
            # You can either block or auto-upgrade by updating items.
            return Response(
                {"detail": "Customer already has an active subscription."},
                status=status.HTTP_409_CONFLICT,
            )
        plan = self._get_and_validate_plan(plan_id)
        if isinstance(plan, Response):
            return plan
        success_url = (
            f"{settings.FRONTEND_URL.rstrip('/')}/settings/subscription-plan/success"
        )
        cancel_url = f"{settings.FRONTEND_URL.rstrip('/')}/settings/subscription-plan/"
        session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": plan.stripe_price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": str(request.user.id),
                "plan_id": str(plan.id),
                "plan_name": plan.name,
            },
        )
        return Response(
            {"session_id": session.id, "url": session.url},
            status=status.HTTP_200_OK,
        )

    def _get_and_validate_plan(self, plan_id):
        """Get and validate subscription plan."""
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"error": "Invalid plan ID or plan is not active"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not plan.stripe_price_id:
            return Response(
                {"error": "Plan does not have an associated Stripe price"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user is trying to checkout a trial plan but has already used trial
        if plan.plan_type == "trial" and self.request.user.has_used_trial:
            return Response(
                {
                    "error": "You have already used your trial subscription and cannot subscribe to another trial plan"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return plan


class CreateBillingPortalSessionView(MethodSpecificThrottleMixin, APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create Stripe Billing Portal Session",
        description=(
            "Create a Stripe Billing Portal session for the authenticated user. "
            "This allows users to manage their subscription, update payment methods, "
            "view invoices, and cancel their subscription through Stripe's hosted portal."
        ),
        responses={
            201: OpenApiResponse(
                description="Billing portal session created successfully",
                response={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "format": "uri",
                            "description": "The URL to redirect the user to for the billing portal",
                            "example": "https://billing.stripe.com/p/session_1234567890",
                        }
                    },
                },
            ),
            400: OpenApiResponse(
                description="Bad request - No Stripe customer found or Stripe error",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Error message",
                            "example": "No Stripe customer on file for this user.",
                        },
                        "type": {
                            "type": "string",
                            "description": "Stripe error type (only for Stripe errors)",
                            "example": "InvalidRequestError",
                        },
                    },
                },
            ),
            401: OpenApiResponse(description="Authentication required"),
        },
        tags=["Stripe Billing Portal"],
    )
    def post(self, request):
        # Get the Stripe customer id for the logged-in user
        return_url = settings.FRONTEND_URL.rstrip("/") + "/settings/subscription-plan/"
        customer = get_or_create_customer(request.user)

        portal = stripe.billing_portal.Session.create(
            customer=customer.id,
            return_url=return_url,
        )
        return Response({"url": portal.url})


class TrialStatusView(MethodSpecificThrottleMixin, APIView):
    """View to check user's trial subscription status"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user trial status",
        description="Check if the authenticated user has a trial plan subscription and return trial details",
        responses={
            200: OpenApiResponse(
                description="Trial status information",
                response=TrialStatusSerializer,
            ),
            404: OpenApiResponse(description="No trial subscription found"),
        },
        tags=["Trial Status"],
    )
    def get(self, request):
        """GET /api/v1/payments/user/trial-status/ - Check user's trial subscription status"""
        try:
            user = request.user
            customer = get_or_create_customer(user)

            # Get user's active subscription
            subscription = (
                Subscription.objects.filter(
                    customer=customer, status__in=VALID_SUB_STATUSES
                )
                .order_by("-created")
                .first()
            )

            # Default response for users without subscription
            default_response = {
                "is_trial": False,
                "trial_days_remaining": 0,
                "trial_expiration_date": None,
                "trial_start_date": None,
                "plan_name": None,
                "plan_type": None,
                "status": None,
            }

            if not subscription:
                return Response(default_response, status=status.HTTP_200_OK)

            # Get the subscription plan details
            plan_name = None
            plan_type = None

            try:
                if subscription.items.exists():
                    first_item = subscription.items.first()
                    if first_item and first_item.price:
                        # Try to get local subscription plan
                        try:
                            local_plan = SubscriptionPlan.objects.get(
                                stripe_price_id=first_item.price.id
                            )
                            plan_name = local_plan.name
                            plan_type = local_plan.plan_type
                        except SubscriptionPlan.DoesNotExist:
                            # Fallback to djstripe data
                            if first_item.price.product:
                                plan_name = first_item.price.product.name
                                plan_type = first_item.price.product.metadata.get(
                                    "plan_type", "unknown"
                                )
            except Exception as e:
                logger.warning(
                    f"Error getting plan details for subscription {subscription.id}: {e}"
                )

            # Check if this is a trial subscription
            is_trial = plan_type == "trial" if plan_type else False
            if is_trial and (not user.has_used_trial):
                user.has_used_trial = True
                user.save()
            # Calculate trial days remaining (if applicable)
            trial_days_remaining = 0
            trial_expiration_date = None
            trial_start_date = None

            if is_trial and subscription.trial_end:
                from django.utils import timezone

                now = timezone.now()
                if subscription.trial_end > now:
                    trial_days_remaining = (subscription.trial_end - now).days
                trial_expiration_date = subscription.trial_end.isoformat()
                trial_start_date = subscription.trial_start

            response_data = {
                "is_trial": is_trial,
                "trial_days_remaining": trial_days_remaining,
                "trial_expiration_date": trial_expiration_date,
                "trial_start_date": trial_start_date,
                "plan_name": plan_name,
                "plan_type": plan_type,
                "status": subscription.status,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"Error checking trial status for user {request.user.email}: {str(e)}"
            )
            return Response(
                {"error": "Failed to check trial status"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
