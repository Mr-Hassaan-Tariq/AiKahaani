import json
import logging
from datetime import timedelta
from decimal import Decimal

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from djstripe.models import Price, Product
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

logger = logging.getLogger(__name__)


def _to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _interval_to_cycle(interval: str) -> str:
    mapping = {"week": "weekly", "month": "monthly", "year": "yearly"}
    return mapping.get((interval or "").lower(), "monthly")


def _parse_features(meta_val):
    """
    Stripe metadata values are strings. If you stored JSON in `features`,
    parse it; otherwise fall back to {}.
    """
    if isinstance(meta_val, dict):
        return meta_val
    if isinstance(meta_val, str):
        try:
            return json.loads(meta_val)
        except json.JSONDecodeError:
            return {}
    return {}


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _ts_to_dt(ts):
    if not ts:
        return None
    try:
        return timezone.datetime.fromtimestamp(int(ts), tz=timezone.utc)
    except Exception:
        return None


def _first_line_period(invoice):
    """
    Try to pull current period start/end from the first invoice line.
    """
    lines = _get(invoice, "lines") or {}
    data = lines.get("data") if isinstance(lines, dict) else None
    if not data or not isinstance(data, list):
        return None, None
    period = data[0].get("period", {})
    return _ts_to_dt(period.get("start")), _ts_to_dt(period.get("end"))


def _amount_to_decimal(unit_amount):
    # Stripe sends amounts in the smallest unit (e.g., cents)
    if unit_amount is None:
        return Decimal("0.00")
    return (Decimal(unit_amount) / Decimal("100")).quantize(Decimal("0.01"))


def sync_plans_from_djstripe():
    """Sync plans from DJ-Stripe to our local SubscriptionPlan model"""
    try:
        # Get all products from DJ-Stripe
        products = Product.objects.all()

        for product in products:
            # Get prices for this product
            prices = Price.objects.filter(product=product)

            for price in prices:
                if price.recurring:  # Only process recurring prices
                    # Map plan type from metadata or default to 'pro'
                    plan_type = product.metadata.get("plan_type", "pro")

                    # Fix plan type mapping
                    if plan_type == "free_trial":
                        plan_type = "trial"

                    # Map billing cycle
                    billing_cycle = price.recurring.get("interval", "month")
                    if billing_cycle == "month":
                        billing_cycle = "monthly"
                    elif billing_cycle == "year":
                        billing_cycle = "yearly"
                    elif billing_cycle == "week":
                        billing_cycle = "weekly"

                    # Calculate price in dollars
                    price_amount = Decimal(price.unit_amount) / 100

                    # Create or update plan
                    plan, created = SubscriptionPlan.objects.update_or_create(
                        plan_type=plan_type,
                        billing_cycle=billing_cycle,
                        defaults={
                            "name": product.name,
                            "price": price_amount,
                            "description": product.description or "",
                            "stripe_product_id": product.id,
                            "stripe_price_id": price.id,
                            "is_active": product.active,
                            "features": product.metadata.get("features", {}),
                            "trial_days": int(product.metadata.get("trial_days", 0)),
                            "sort_order": int(product.metadata.get("sort_order", 0)),
                        },
                    )

                    if created:
                        logger.info(f"Created new plan: {plan.name}")
                    else:
                        logger.info(f"Updated existing plan: {plan.name}")

    except Exception as e:
        logger.error(f"Error syncing plans from DJ-Stripe: {str(e)}")
        raise


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


def handle_checkout_session_completed(session):
    """
    Handle Stripe `checkout.session.completed`.
    Prefers Stripe-provided IDs (session.subscription, session.customer).
    Falls back to metadata fields if you send custom ones.
    """
    try:
        meta = _get(session, "metadata") or {}
        # Prefer canonical Stripe IDs from the session
        stripe_subscription_id = _get(session, "subscription") or meta.get(
            "stripe_subscription_id"
        )
        stripe_customer_id = _get(session, "customer") or meta.get("stripe_customer_id")
        checkout_session_id = _get(session, "id") or meta.get("checkout_session_id")
        payment_intent_id = _get(session, "payment_intent")
        amount_total = _amount_to_decimal(
            _get(session, "amount_total")
        )  # may be 0 on free trial
        currency = (_get(session, "currency") or "usd").lower()

        # Your own identifiers (optional; useful if you created the UserSubscription ahead of time)
        user_id = meta.get("user_id")
        local_subscription_uuid = meta.get("subscription_id")  # your UUID

        # Resolve the local subscription record
        sub = None
        if local_subscription_uuid:
            sub = (
                UserSubscription.objects.filter(id=local_subscription_uuid)
                .select_related("plan", "user")
                .first()
            )
        if not sub and stripe_subscription_id:
            sub = (
                UserSubscription.objects.filter(
                    stripe_subscription_id=stripe_subscription_id
                )
                .select_related("plan", "user")
                .first()
            )
        if not sub and stripe_customer_id:
            sub = (
                UserSubscription.objects.filter(stripe_customer_id=stripe_customer_id)
                .select_related("plan", "user")
                .first()
            )
        if not sub and user_id:
            sub = (
                UserSubscription.objects.filter(user_id=user_id)
                .select_related("plan", "user")
                .first()
            )

        if not sub:
            logger.warning(
                "checkout.session.completed: no matching UserSubscription "
                "(stripe_subscription_id=%s, stripe_customer_id=%s, local_id=%s, user_id=%s)",
                stripe_subscription_id,
                stripe_customer_id,
                local_subscription_uuid,
                user_id,
            )
            return None

        # Update Stripe IDs if missing
        dirty = []
        if (
            stripe_subscription_id
            and sub.stripe_subscription_id != stripe_subscription_id
        ):
            sub.stripe_subscription_id = stripe_subscription_id
            dirty.append("stripe_subscription_id")
        if stripe_customer_id and sub.stripe_customer_id != stripe_customer_id:
            sub.stripe_customer_id = stripe_customer_id
            dirty.append("stripe_customer_id")

        # Derive the period:
        # We usually don’t have the full Stripe subscription payload here; fall back by plan cycle.
        period_start = timezone.now()
        bc = (sub.plan.billing_cycle or "monthly").lower()
        if bc == "weekly":
            period_end = period_start + timedelta(days=7)
        elif bc == "yearly":
            period_end = period_start + timedelta(days=365)
        else:
            period_end = period_start + timedelta(days=30)

        # Status: if first charge was $0 and plan has trial days, mark trialing; else active
        is_trial_like = (
            amount_total == Decimal("0.00") and (sub.plan.trial_days or 0) > 0
        )
        new_status = "trialing" if is_trial_like else "active"

        if sub.status != new_status:
            sub.status = new_status
            dirty.append("status")
        if sub.current_period_start != period_start:
            sub.current_period_start = period_start
            dirty.append("current_period_start")
        if sub.current_period_end != period_end:
            sub.current_period_end = period_end
            dirty.append("current_period_end")

        # If we’re starting a trial, also set trial dates
        if is_trial_like:
            trial_end = period_start + timedelta(days=sub.plan.trial_days or 0)
            if sub.trial_start != period_start:
                sub.trial_start = period_start
                dirty.append("trial_start")
            if sub.trial_end != trial_end:
                sub.trial_end = trial_end
                dirty.append("trial_end")

        if dirty:
            dirty.append("modified")
            sub.save(update_fields=dirty)

        # Record payment (idempotent)
        # Prefer payment_intent (unique). If absent (free trial), key by checkout_session_id.
        description = f"Checkout for {sub.plan.name}"
        defaults = {
            "user": sub.user,
            "subscription": sub,
            "amount": (amount_total if amount_total is not None else sub.plan.price),
            "currency": currency,
            "status": "succeeded",
            "description": description,
            "metadata": {"checkout_session_id": checkout_session_id}
            if checkout_session_id
            else {},
        }

        if payment_intent_id:
            defaults["stripe_invoice_id"] = None  # not known here
            defaults["stripe_payment_intent_id"] = payment_intent_id
            _, created = PaymentHistory.objects.update_or_create(
                stripe_payment_intent_id=payment_intent_id,
                defaults=defaults,
            )
        elif checkout_session_id:
            # Last-resort idempotency key when there's no PI (e.g., $0 trial)
            # Not a strict uniqueness in the model, but good enough to avoid dupes on retries.
            _, created = PaymentHistory.objects.get_or_create(
                subscription=sub,
                user=sub.user,
                description=description,
                metadata={"checkout_session_id": checkout_session_id},
                defaults={
                    k: v
                    for k, v in defaults.items()
                    if k not in ("metadata", "description")
                },
            )
        else:
            # If neither PI nor session id is available, just create a record (can duplicate on retries).
            PaymentHistory.objects.create(**defaults)
            created = True

        logger.info(
            "Checkout session completed for sub %s (status=%s, fields=%s) | Payment %s",
            sub.id,
            sub.status,
            ", ".join(f for f in dirty if f != "modified") if dirty else "none",
            "created" if created else "updated",
        )
        return sub

    except Exception as e:
        logger.exception("Error handling checkout.session.completed: %s", e)
        return None


def handle_invoice_payment_succeeded(invoice):
    """Handle Stripe `invoice.payment_succeeded`."""
    try:
        subscription_id = _get(invoice, "subscription")
        if not subscription_id:
            logger.warning(
                "invoice.payment_succeeded without subscription id; skipping."
            )
            return None

        subscription = (
            UserSubscription.objects.filter(stripe_subscription_id=subscription_id)
            .select_related("plan", "user")
            .first()
        )

        if not subscription:
            logger.warning(
                "UserSubscription not found for stripe_subscription_id=%s",
                subscription_id,
            )
            return None

        # Derive period from invoice where possible
        period_start, period_end = _first_line_period(invoice)
        if not period_start:
            # Fallback to now-based estimation by plan cycle
            period_start = timezone.now()
        if not period_end:
            bc = (subscription.plan.billing_cycle or "monthly").lower()
            if bc == "weekly":
                period_end = period_start + timedelta(days=7)
            elif bc == "yearly":
                period_end = period_start + timedelta(days=365)
            else:
                period_end = period_start + timedelta(days=30)

        # Prepare subscription field updates
        new_status = "active"
        new_current_period_start = period_start
        new_current_period_end = period_end

        dirty = []
        if subscription.status != new_status:
            subscription.status = new_status
            dirty.append("status")
        if subscription.current_period_start != new_current_period_start:
            subscription.current_period_start = new_current_period_start
            dirty.append("current_period_start")
        if subscription.current_period_end != new_current_period_end:
            subscription.current_period_end = new_current_period_end
            dirty.append("current_period_end")

        # If Stripe customer is known on invoice and we don't have it, set it
        stripe_customer_id = _get(invoice, "customer")
        if stripe_customer_id and subscription.stripe_customer_id != stripe_customer_id:
            subscription.stripe_customer_id = stripe_customer_id
            dirty.append("stripe_customer_id")

        if dirty:
            dirty.append("modified")
            subscription.save(update_fields=dirty)

        # Upsert payment record by invoice id to stay idempotent
        amount_paid = _amount_to_decimal(_get(invoice, "amount_paid"))
        currency = (_get(invoice, "currency") or "usd").lower()
        invoice_id = _get(invoice, "id")
        payment_intent_id = _get(invoice, "payment_intent")
        description = f"Recurring payment for {subscription.plan.name}"

        ph_defaults = {
            "user": subscription.user,
            "subscription": subscription,
            "amount": amount_paid,
            "currency": currency,
            "stripe_payment_intent_id": payment_intent_id,
            "status": "succeeded",
            "description": description,
            "metadata": {"invoice_id": invoice_id},
        }

        payment, created = PaymentHistory.objects.update_or_create(
            stripe_invoice_id=invoice_id,
            defaults=ph_defaults,
        )

        logger.info(
            "Invoice payment succeeded for sub %s (updated sub fields: %s) | Payment %s",
            subscription.id,
            ", ".join(f for f in dirty if f != "modified") if dirty else "none",
            "created" if created else "updated",
        )

        return subscription

    except Exception as e:
        logger.exception("Error handling invoice payment succeeded: %s", e)
        return None


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _ts_to_dt(ts):
    if not ts:
        return None
    try:
        return timezone.datetime.fromtimestamp(int(ts), tz=timezone.utc)
    except Exception:
        return None


def _amount_to_decimal(unit_amount):
    if unit_amount is None:
        return Decimal("0.00")
    return (Decimal(unit_amount) / Decimal("100")).quantize(Decimal("0.01"))


def handle_invoice_payment_failed(invoice):
    """Handle Stripe `invoice.payment_failed`."""
    try:
        subscription_id = _get(invoice, "subscription")
        if not subscription_id:
            logger.warning("invoice.payment_failed without subscription id; skipping.")
            return None

        sub = (
            UserSubscription.objects.filter(stripe_subscription_id=subscription_id)
            .select_related("plan", "user")
            .first()
        )

        if not sub:
            logger.warning(
                "UserSubscription not found for stripe_subscription_id=%s",
                subscription_id,
            )
            return None

        # Stripe sometimes sets status="unpaid" after retries; prefer Stripe status if provided.
        stripe_status = (_get(invoice, "status") or "").lower()
        new_status = "unpaid" if stripe_status == "unpaid" else "past_due"

        dirty = []
        if sub.status != new_status:
            sub.status = new_status
            dirty.append("status")

        # If Stripe customer present and missing locally, set it
        stripe_customer_id = _get(invoice, "customer")
        if stripe_customer_id and sub.stripe_customer_id != stripe_customer_id:
            sub.stripe_customer_id = stripe_customer_id
            dirty.append("stripe_customer_id")

        # Optional: update next payment attempt time if present
        next_attempt = _ts_to_dt(_get(invoice, "next_payment_attempt"))
        if next_attempt and getattr(sub, "next_payment_attempt", None) != next_attempt:
            # Only if you have such a field; otherwise remove this block.
            try:
                sub.next_payment_attempt = next_attempt  # type: ignore[attr-defined]
                dirty.append("next_payment_attempt")
            except Exception:
                pass  # field may not exist; ignore

        if dirty:
            dirty.append("modified")
            sub.save(update_fields=dirty)

        # Build failure details for PaymentHistory
        invoice_id = _get(invoice, "id")
        amount_due = _amount_to_decimal(_get(invoice, "amount_due"))
        currency = (_get(invoice, "currency") or "usd").lower()
        payment_intent_id = _get(invoice, "payment_intent")

        last_payment_error = None
        if isinstance(invoice, dict):
            last_payment_error = (invoice.get("last_finalization_error")) or (
                invoice.get("last_payment_error")
            )
        else:
            last_payment_error = getattr(
                invoice, "last_finalization_error", None
            ) or getattr(invoice, "last_payment_error", None)

        failure_info = {}
        if last_payment_error:
            failure_info = {
                "code": last_payment_error.get("code")
                if isinstance(last_payment_error, dict)
                else getattr(last_payment_error, "code", None),
                "decline_code": last_payment_error.get("decline_code")
                if isinstance(last_payment_error, dict)
                else getattr(last_payment_error, "decline_code", None),
                "message": last_payment_error.get("message")
                if isinstance(last_payment_error, dict)
                else getattr(last_payment_error, "message", None),
                "type": last_payment_error.get("type")
                if isinstance(last_payment_error, dict)
                else getattr(last_payment_error, "type", None),
            }

        # Idempotent payment record keyed by invoice id
        ph_defaults = {
            "user": sub.user,
            "subscription": sub,
            "amount": amount_due,
            "currency": currency,
            "stripe_payment_intent_id": payment_intent_id,
            "status": "failed",
            "description": f"Invoice payment failed for {sub.plan.name}",
            "metadata": {
                "invoice_id": invoice_id,
                **({"failure": failure_info} if failure_info else {}),
            },
        }

        payment, created = PaymentHistory.objects.update_or_create(
            stripe_invoice_id=invoice_id,
            defaults=ph_defaults,
        )

        logger.info(
            "Invoice payment failed for sub %s (new status=%s; updated fields: %s) | Payment %s",
            sub.id,
            new_status,
            ", ".join(f for f in dirty if f != "modified") if dirty else "none",
            "created" if created else "updated",
        )
        return sub

    except Exception as e:
        logger.exception("Error handling invoice payment failed: %s", e)
        return None


def handle_product_updated(product):
    """Handle product updates from Stripe (accepts dict or Stripe object)."""
    try:
        # Support dict or StripeObject
        if isinstance(product, dict):
            getv = product.get
        else:

            def getv(k, d=None):
                return getattr(product, k, d)

        product_id = getv("id")
        if not product_id:
            logger.warning("product.updated missing product id; skipping.")
            return None

        plan = SubscriptionPlan.objects.filter(stripe_product_id=product_id).first()
        if not plan:
            logger.warning(
                "No SubscriptionPlan found with stripe_product_id=%s; skipping update.",
                product_id,
            )
            return None

        meta = getv("metadata") or {}

        # Prepare new values but fall back to current plan values when missing
        new_name = getv("name") or plan.name
        new_desc = getv("description") or plan.description

        # 'active' could be True/False/None; only update if not None
        active_val = getv("active")
        new_active = plan.is_active if active_val is None else bool(active_val)

        new_features = _parse_features(meta.get("features"), plan.features)

        td = _to_int(meta.get("trial_days"), plan.trial_days)
        so = _to_int(meta.get("sort_order"), plan.sort_order)

        # Apply only dirty fields
        dirty = []
        for field, value in [
            ("name", new_name),
            ("description", new_desc),
            ("is_active", new_active),
            ("features", new_features),
            ("trial_days", td),
            ("sort_order", so),
        ]:
            if getattr(plan, field) != value:
                setattr(plan, field, value)
                dirty.append(field)

        if dirty:
            # model_utils TimeStampedModel: include "modified" for partial saves
            dirty.append("modified")
            plan.save(update_fields=dirty)
            logger.info(
                "Updated plan from Stripe product: %s (fields: %s)",
                plan.name,
                ", ".join(d for d in dirty if d != "modified"),
            )
        else:
            logger.info("No changes detected for plan %s; skipping save.", plan.name)

        return plan

    except Exception as e:
        logger.exception("Error handling product updated: %s", e)
        return None


def handle_subscription_deleted(subscription_data):
    """Handle `customer.subscription.deleted` from Stripe."""
    try:
        stripe_sub_id = _get(subscription_data, "id")
        stripe_customer_id = _get(subscription_data, "customer")

        if not stripe_sub_id and not stripe_customer_id:
            logger.warning("subscription.deleted missing id/customer; skipping.")
            return None

        sub = None
        if stripe_sub_id:
            sub = UserSubscription.objects.filter(
                stripe_subscription_id=stripe_sub_id
            ).first()

        if not sub and stripe_customer_id:
            sub = UserSubscription.objects.filter(
                stripe_customer_id=stripe_customer_id
            ).first()

        if not sub:
            logger.warning(
                "UserSubscription not found for subscription=%s customer=%s",
                stripe_sub_id,
                stripe_customer_id,
            )
            return None

        # Pull Stripe times if present
        canceled_at_ts = _get(subscription_data, "canceled_at")
        ended_at_ts = _get(subscription_data, "ended_at")
        current_period_end_ts = _get(subscription_data, "current_period_end")
        cancel_at_period_end_val = _get(subscription_data, "cancel_at_period_end")

        new_status = "canceled"
        new_canceled_at = (
            _ts_to_dt(canceled_at_ts) or _ts_to_dt(ended_at_ts) or timezone.now()
        )
        new_current_period_end = _ts_to_dt(current_period_end_ts)
        # Since it's deleted, we typically consider cancel_at_period_end False now.
        new_cancel_at_period_end = (
            bool(cancel_at_period_end_val)
            if cancel_at_period_end_val is not None
            else False
        )

        dirty = []

        if sub.status != new_status:
            sub.status = new_status
            dirty.append("status")

        if sub.canceled_at != new_canceled_at:
            sub.canceled_at = new_canceled_at
            dirty.append("canceled_at")

        if new_current_period_end and sub.current_period_end != new_current_period_end:
            sub.current_period_end = new_current_period_end
            dirty.append("current_period_end")

        if sub.cancel_at_period_end != new_cancel_at_period_end:
            sub.cancel_at_period_end = new_cancel_at_period_end
            dirty.append("cancel_at_period_end")

        # Optional: clear trial fields if they linger after deletion
        if sub.trial_end or sub.trial_start:
            sub.trial_start = None
            sub.trial_end = None
            dirty.extend(["trial_start", "trial_end"])

        if dirty:
            dirty.append("modified")  # from TimeStampedModel
            sub.save(update_fields=dirty)
            logger.info(
                "Subscription %s marked canceled (fields: %s)",
                sub.id,
                ", ".join(f for f in dirty if f != "modified"),
            )
        else:
            logger.info("Subscription %s already canceled; no changes.", sub.id)

        return sub

    except Exception as e:
        logger.exception("Error handling subscription deleted: %s", e)
        return None


def handle_product_created(event):
    """Handle product creation in Stripe"""
    try:
        meta = event.get("metadata", {}) or {}

        plan_type = meta.get("plan_type", "pro")
        billing_cycle = meta.get("billing_cycle", "monthly")  # optional on product
        features = _parse_features(meta.get("features", {}))
        trial_days = _to_int(meta.get("trial_days", 0))
        sort_order = _to_int(meta.get("sort_order", 0))

        plan, created = SubscriptionPlan.objects.update_or_create(
            plan_type=plan_type,
            billing_cycle=billing_cycle,
            defaults={
                "name": event.get("name") or "",
                "description": event.get("description") or "",
                "stripe_product_id": event.get("id"),
                "is_active": bool(event.get("active", True)),
                "features": features,
                "trial_days": trial_days,
                "sort_order": sort_order,
            },
        )
        return plan

    except Exception as e:
        logger.error(f"Error handling product created: {str(e)}")


def handle_price_created(price):
    """Handle Stripe `price.created`."""
    try:
        recurring = _get(price, "recurring") or {}
        if not recurring:
            # one-time price; nothing to do for subscriptions
            return None

        interval = recurring.get("interval")
        billing_cycle = _interval_to_cycle(interval)

        product_id = _get(price, "product")
        price_id = _get(price, "id")
        unit_amount = _get(price, "unit_amount")
        currency = (_get(price, "currency") or "usd").lower()
        price_amount = _amount_to_decimal(unit_amount)

        # Prefer plan_type from price metadata; else we'll rely on product-linked plan
        meta = _get(price, "metadata") or {}
        plan_type = meta.get("plan_type")

        # 1) Try to find plan by product + cycle (best)
        qs = SubscriptionPlan.objects.filter(
            stripe_product_id=product_id, billing_cycle=billing_cycle
        )
        if plan_type:
            qs = qs.filter(plan_type=plan_type)

        plan = qs.first()

        # 2) Fallback: if we already stored this price once, update by price_id
        if not plan and price_id:
            plan = SubscriptionPlan.objects.filter(stripe_price_id=price_id).first()

        if not plan:
            logger.warning(
                "price.created: No matching SubscriptionPlan found "
                "(product=%s, billing_cycle=%s, plan_type=%s). Did product.created run?",
                product_id,
                billing_cycle,
                plan_type,
            )
            return None

        dirty = []
        if plan.price != price_amount:
            plan.price = price_amount
            dirty.append("price")
        if plan.stripe_price_id != price_id:
            plan.stripe_price_id = price_id
            dirty.append("stripe_price_id")

        if dirty:
            dirty.append("modified")
            plan.save(update_fields=dirty)
            logger.info(
                "Updated plan price from Stripe: %s | %s %s (fields: %s)",
                plan.name,
                price_amount,
                currency.upper(),
                ", ".join(f for f in dirty if f != "modified"),
            )
        else:
            logger.info("price.created: No changes for plan %s.", plan.name)

        return plan

    except Exception as e:
        logger.exception("Error handling price.created: %s", e)
        return None


def handle_price_updated(price):
    """Handle Stripe `price.updated`."""
    try:
        recurring = _get(price, "recurring") or {}
        if not recurring:
            return None

        price_id = _get(price, "id")
        unit_amount = _get(price, "unit_amount")
        currency = (_get(price, "currency") or "usd").lower()
        price_amount = _amount_to_decimal(unit_amount)

        # First try by price_id
        plan = SubscriptionPlan.objects.filter(stripe_price_id=price_id).first()

        # Fallback: locate by product + cycle (in case we hadn’t set stripe_price_id yet)
        if not plan:
            product_id = _get(price, "product")
            interval = recurring.get("interval")
            billing_cycle = _interval_to_cycle(interval)
            meta = _get(price, "metadata") or {}
            plan_type = meta.get("plan_type")

            qs = SubscriptionPlan.objects.filter(
                stripe_product_id=product_id, billing_cycle=billing_cycle
            )
            if plan_type:
                qs = qs.filter(plan_type=plan_type)
            plan = qs.first()

        if not plan:
            logger.warning(
                "price.updated: No matching SubscriptionPlan found (price_id=%s).",
                price_id,
            )
            return None

        dirty = []
        if plan.price != price_amount:
            plan.price = price_amount
            dirty.append("price")
        # Ensure we store stripe_price_id if missing
        if plan.stripe_price_id != price_id:
            plan.stripe_price_id = price_id
            dirty.append("stripe_price_id")

        if dirty:
            dirty.append("modified")
            plan.save(update_fields=dirty)
            logger.info(
                "Updated plan price from Stripe: %s | %s %s (fields: %s)",
                plan.name,
                price_amount,
                currency.upper(),
                ", ".join(f for f in dirty if f != "modified"),
            )
        else:
            logger.info("price.updated: No changes for plan %s.", plan.name)

        return plan

    except Exception as e:
        logger.exception("Error handling price.updated: %s", e)
        return None


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
