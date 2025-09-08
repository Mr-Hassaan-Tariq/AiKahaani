import logging
from datetime import timedelta

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from djstripe.models import Customer
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PaymentHistory, SubscriptionPlan, UserSubscription
from .serializers import (
    CreateSubscriptionSerializer,
    PaymentHistorySerializer,
    SubscriptionPlanSerializer,
    TrialStatusSerializer,
    UserSubscriptionSerializer,
)
from .webhook_helper import (
    handle_checkout_session_completed,
    handle_invoice_payment_failed,
    handle_invoice_payment_succeeded,
    handle_price_created,
    handle_price_updated,
    handle_product_created,
    handle_product_updated,
    handle_subscription_deleted,
    sync_plans_from_djstripe,
)

logger = logging.getLogger(__name__)


class SubscriptionPlansView(APIView):
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
            # Sync plans from DJ-Stripe first
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


class UserSubscriptionView(APIView):
    """View to manage user subscriptions"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user subscription",
        description="Retrieve the current user's subscription details",
        responses={
            200: OpenApiResponse(
                description="User subscription details",
                response=UserSubscriptionSerializer,
            ),
            404: OpenApiResponse(description="No subscription found"),
        },
        tags=["User Subscriptions"],
    )
    def get(self, request):
        """GET /api/subscription - Get current user's subscription"""
        try:
            subscription = UserSubscription.objects.filter(user=request.user).first()
            if not subscription:
                return Response(
                    {"error": "No subscription found"}, status=status.HTTP_404_NOT_FOUND
                )

            serializer = UserSubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching user subscription: {str(e)}")
            return Response(
                {"error": "Failed to fetch subscription"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Create user subscription",
        description="Create a new subscription for the current user",
        request=CreateSubscriptionSerializer,
        responses={
            201: OpenApiResponse(
                description="Subscription created successfully",
                response=UserSubscriptionSerializer,
            ),
            400: OpenApiResponse(description="Invalid data provided"),
        },
        tags=["User Subscriptions"],
    )
    def post(self, request):
        """POST /api/subscription - Create a new subscription"""
        try:
            serializer = CreateSubscriptionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            plan_id = serializer.validated_data["plan_id"]
            billing_cycle = serializer.validated_data["billing_cycle"]

            # Get the plan
            try:
                plan = SubscriptionPlan.objects.get(
                    id=plan_id, billing_cycle=billing_cycle, is_active=True
                )
            except SubscriptionPlan.DoesNotExist:
                return Response(
                    {"error": "Invalid plan or billing cycle"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if user already has a subscription
            existing_subscription = UserSubscription.objects.filter(
                user=request.user
            ).first()
            if existing_subscription:
                return Response(
                    {"error": "User already has a subscription"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Import DJ-Stripe models and Stripe
            # Set Stripe API key
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Ensure a Stripe Customer exists for this user
            try:
                customer = Customer.objects.get(subscriber=request.user)
            except Customer.DoesNotExist:
                # Create new customer
                customer = Customer.create(
                    subscriber=request.user,
                )

            # Create subscription
            subscription = UserSubscription.objects.create(
                user=request.user,
                plan=plan,
                stripe_customer_id=customer.id,
                status="trial" if plan.plan_type == "trial" else "incomplete",
            )

            # Set trial dates if it's a trial plan
            if plan.plan_type == "trial" and plan.trial_days > 0:
                subscription.trial_start = timezone.now()
                subscription.trial_end = timezone.now() + timedelta(
                    days=plan.trial_days
                )
                subscription.save()

            # Create Stripe Checkout Session using standard Stripe API
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
                success_url=f"{settings.FRONTEND_URL}/dashboard?success=true",
                cancel_url=f"{settings.FRONTEND_URL}/dashboard?canceled=true",
                metadata={
                    "user_id": str(request.user.id),
                    "plan_id": str(plan.id),
                    "subscription_id": str(subscription.id),
                },
            )

            subscription.stripe_subscription_id = session.id
            subscription.save()

            return Response(
                {
                    "message": "Subscription created successfully",
                    "checkout_url": session.url,
                    "subscription": UserSubscriptionSerializer(subscription).data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return Response(
                {"error": "Failed to create subscription"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PaymentHistoryView(APIView):
    """View to fetch user payment history"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get payment history",
        description="Retrieve the current user's payment history",
        responses={
            200: OpenApiResponse(
                description="Payment history",
                response=PaymentHistorySerializer(many=True),
            )
        },
        tags=["Payment History"],
    )
    def get(self, request):
        """GET /api/payments/history - Get user's payment history"""
        try:
            payments = PaymentHistory.objects.filter(user=request.user).order_by(
                "-created"
            )
            serializer = PaymentHistorySerializer(payments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching payment history: {str(e)}")
            return Response(
                {"error": "Failed to fetch payment history"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhooks"""

    # Set Stripe API key
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook secret from settings
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        # Get the raw request body
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        # Construct the event using Stripe's method
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=400)

    # Handle the event
    if event["type"] == "checkout.session.completed":
        handle_checkout_session_completed(event["data"]["object"])
    elif event["type"] == "invoice.payment_succeeded":
        handle_invoice_payment_succeeded(event["data"]["object"])
    elif event["type"] == "invoice.payment_failed":
        handle_invoice_payment_failed(event["data"]["object"])
    elif event["type"] == "customer.subscription.updated":
        handle_product_updated(event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        handle_subscription_deleted(event["data"]["object"])
    elif event["type"] == "product.created":
        handle_product_created(event["data"]["object"])
    elif event["type"] == "product.updated":
        handle_product_updated(event["data"]["object"])
    elif event["type"] == "price.created":
        handle_price_created(event["data"]["object"])
    elif event["type"] == "price.updated":
        handle_price_updated(event["data"]["object"])

    return HttpResponse(status=200)


class TrialStatusView(APIView):
    """View to check user's trial status"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user trial status",
        description="Retrieve the current user's trial status including remaining days and expiration date",
        responses={
            200: OpenApiResponse(
                description="User trial status", response=TrialStatusSerializer
            ),
            404: OpenApiResponse(description="No subscription found"),
        },
        tags=["Trial Status"],
    )
    def get(self, request):
        """GET /api/user/trial-status - Get current user's trial status"""
        try:
            subscription = UserSubscription.objects.filter(user=request.user).first()
            if not subscription:
                return Response(
                    {"error": "No subscription found"}, status=status.HTTP_404_NOT_FOUND
                )

            # Prepare trial status data
            trial_data = {
                "is_trial": subscription.is_trial,
                "trial_days_remaining": subscription.trial_days_remaining,
                "trial_expiration_date": subscription.trial_expiration_date,
                "trial_start_date": subscription.trial_start,
                "plan_name": subscription.plan.name,
                "plan_type": subscription.plan.plan_type,
                "status": subscription.status,
            }

            serializer = TrialStatusSerializer(trial_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching trial status: {str(e)}")
            return Response(
                {"error": "Failed to fetch trial status"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CreateCheckoutSessionView(APIView):
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
            400: OpenApiResponse(description="Invalid request or plan id"),
        },
        tags=["Stripe Checkout"],
    )
    def post(self, request):
        try:
            plan_id = request.data.get("plan_id")
            if not plan_id:
                return Response(
                    {"error": "Plan ID is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Get the plan from local database
            try:
                plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            except SubscriptionPlan.DoesNotExist:
                return Response(
                    {"error": "Invalid plan ID or plan is not active"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate the plan has a Stripe price ID
            if not plan.stripe_price_id:
                return Response(
                    {"error": "Plan does not have an associated Stripe price"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Import DJ-Stripe models and Stripe
            import stripe
            from djstripe.models import Customer

            # Set Stripe API key
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Ensure a Stripe Customer exists for this user
            try:
                customer = Customer.objects.get(subscriber=request.user)
            except Customer.DoesNotExist:
                # Create new customer
                customer = Customer.create(
                    subscriber=request.user,
                )

            # Create Stripe Checkout Session using standard Stripe API
            success_url = f"{settings.FRONTEND_URL.rstrip('/')}/settings/subscription-plan/success"
            cancel_url = (
                f"{settings.FRONTEND_URL.rstrip('/')}/settings/subscription-plan/"
            )

            print("Creating checkout session with URLs:")
            print(f"Success URL: {success_url}")
            print(f"Cancel URL: {cancel_url}")

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
        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
