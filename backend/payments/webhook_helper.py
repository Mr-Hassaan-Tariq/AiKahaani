import json
import logging
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from djstripe.models import Price, Product

from .models import PaymentHistory, SubscriptionPlan, UserSubscription

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


def _norm_cycle(val: str | None) -> str:
    if not val:
        return "monthly"
    val = str(val).lower()
    return {
        "month": "monthly",
        "year": "yearly",
        "week": "weekly",
        "monthly": "monthly",
        "yearly": "yearly",
        "weekly": "weekly",
    }.get(val, "monthly")


def _resolve_plan_from_meta(meta):
    """
    Try several hints to find a SubscriptionPlan:
    - plan_type + billing_cycle
    - stripe_price_id
    - stripe_product_id (+ optional billing_cycle)
    - fallback to active pro/monthly
    """
    plan = None
    plan_type = meta.get("plan_type")
    billing_cycle = _norm_cycle(meta.get("billing_cycle"))

    if plan_type:
        qs = SubscriptionPlan.objects.filter(
            plan_type=plan_type, billing_cycle=billing_cycle, is_active=True
        )
        plan = qs.order_by("sort_order", "name").first()
        if plan:
            return plan

    price_id = meta.get("stripe_price_id")
    if price_id:
        plan = SubscriptionPlan.objects.filter(
            stripe_price_id=price_id, is_active=True
        ).first()
        if plan:
            return plan

    product_id = meta.get("stripe_product_id")
    if product_id:
        qs = SubscriptionPlan.objects.filter(
            stripe_product_id=product_id, is_active=True
        )
        # If caller provided a cycle hint, use it
        if billing_cycle:
            qs = qs.filter(billing_cycle=billing_cycle)
        plan = qs.order_by("sort_order", "name").first()
        if plan:
            return plan

    # Sensible default fallback
    plan = (
        SubscriptionPlan.objects.filter(
            plan_type="pro", billing_cycle="monthly", is_active=True
        )
        .order_by("sort_order", "name")
        .first()
    )
    if plan:
        return plan

    # Last resort: any active plan
    return (
        SubscriptionPlan.objects.filter(is_active=True)
        .order_by("sort_order", "name")
        .first()
    )


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


def handle_checkout_session_completed(session):
    """
    Handle Stripe `checkout.session.completed`.
    Creates a UserSubscription if it doesn't exist yet.
    """
    try:
        meta = _get(session, "metadata") or {}

        # Prefer canonical Stripe IDs
        stripe_subscription_id = _get(session, "subscription") or meta.get(
            "stripe_subscription_id"
        )
        stripe_customer_id = _get(session, "customer") or meta.get("stripe_customer_id")
        checkout_session_id = _get(session, "id") or meta.get("checkout_session_id")
        payment_intent_id = _get(session, "payment_intent")
        amount_total = _amount_to_decimal(
            _get(session, "amount_total")
        )  # may be 0 on trials
        currency = (_get(session, "currency") or "usd").lower()

        # Your app identifiers (optional)
        user_id = meta.get("user_id")
        local_subscription_uuid = meta.get("subscription_id")

        # Try to find an existing subscription
        sub = None
        if local_subscription_uuid:
            sub = (
                UserSubscription.objects.select_related("plan", "user")
                .filter(id=local_subscription_uuid)
                .first()
            )
        if not sub and stripe_subscription_id:
            sub = (
                UserSubscription.objects.select_related("plan", "user")
                .filter(stripe_subscription_id=stripe_subscription_id)
                .first()
            )
        if not sub and stripe_customer_id:
            sub = (
                UserSubscription.objects.select_related("plan", "user")
                .filter(stripe_customer_id=stripe_customer_id)
                .first()
            )
        if not sub and user_id:
            sub = (
                UserSubscription.objects.select_related("plan", "user")
                .filter(user_id=user_id)
                .first()
            )

        # If still not found, CREATE it
        if not sub:
            if not user_id:
                logger.warning(
                    "checkout.session.completed: cannot create UserSubscription without user_id. "
                    "(sub_id=%s, customer_id=%s, local_id=%s)",
                    stripe_subscription_id,
                    stripe_customer_id,
                    local_subscription_uuid,
                )
                return None

            plan = _resolve_plan_from_meta(meta)
            if not plan:
                logger.warning(
                    "checkout.session.completed: no plan could be resolved from metadata; aborting create. "
                    "(sub_id=%s, customer_id=%s, meta=%s)",
                    stripe_subscription_id,
                    stripe_customer_id,
                    meta,
                )
                return None

            # Determine initial status/periods
            period_start = timezone.now()
            bc = (plan.billing_cycle or "monthly").lower()
            if bc == "weekly":
                period_end = period_start + timedelta(days=7)
            elif bc == "yearly":
                period_end = period_start + timedelta(days=365)
            else:
                period_end = period_start + timedelta(days=30)

            is_trial_like = (
                amount_total == Decimal("0.00") and (plan.trial_days or 0) > 0
            )
            status = "trialing" if is_trial_like else "active"

            sub = UserSubscription.objects.create(
                user_id=user_id,
                plan=plan,
                stripe_subscription_id=stripe_subscription_id,
                stripe_customer_id=stripe_customer_id,
                status=status,
                current_period_start=period_start,
                current_period_end=period_end,
                trial_start=period_start if is_trial_like else None,
                trial_end=(period_start + timedelta(days=plan.trial_days or 0))
                if is_trial_like
                else None,
                cancel_at_period_end=False,
            )
            logger.info("Created UserSubscription %s for user %s.", sub.id, user_id)

        # Update Stripe IDs on existing sub if missing/different
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

        # If sub was pre-created without periods/status, set them now
        if (
            not sub.current_period_start
            or not sub.current_period_end
            or sub.status in ("incomplete", "incomplete_expired")
        ):
            period_start = timezone.now()
            bc = (sub.plan.billing_cycle or "monthly").lower()
            if bc == "weekly":
                period_end = period_start + timedelta(days=7)
            elif bc == "yearly":
                period_end = period_start + timedelta(days=365)
            else:
                period_end = period_start + timedelta(days=30)

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
            defaults["stripe_invoice_id"] = None
            defaults["stripe_payment_intent_id"] = payment_intent_id
            PaymentHistory.objects.update_or_create(
                stripe_payment_intent_id=payment_intent_id,
                defaults=defaults,
            )
        elif checkout_session_id:
            PaymentHistory.objects.get_or_create(
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
            PaymentHistory.objects.create(**defaults)

        logger.info(
            "Checkout session completed for sub %s (status=%s, updated=%s)",
            sub.id,
            sub.status,
            ", ".join(f for f in dirty if f != "modified") if dirty else "none",
        )
        return sub

    except Exception as e:
        logger.exception("Error handling checkout.session.completed: %s", e)
        return None


def _resolve_plan_from_invoice(invoice):
    """
    Try to resolve a SubscriptionPlan from the invoice's first line (price/product/interval).
    Fallback to an active pro/monthly plan.
    """
    # Try via price on first line
    lines = _get(invoice, "lines") or {}
    data = lines.get("data") if isinstance(lines, dict) else None
    price_obj = None
    if data and isinstance(data, list) and data:
        first = data[0]
        price_obj = first.get("price")

    if isinstance(price_obj, dict):
        price_id = price_obj.get("id")
        if price_id:
            plan = SubscriptionPlan.objects.filter(
                stripe_price_id=price_id, is_active=True
            ).first()
            if plan:
                return plan

        product_id = price_obj.get("product")
        interval = (price_obj.get("recurring") or {}).get("interval")
        cycle = _interval_to_cycle(interval)
        if product_id:
            plan = (
                SubscriptionPlan.objects.filter(
                    stripe_product_id=product_id,
                    billing_cycle=cycle,
                    is_active=True,
                )
                .order_by("sort_order", "name")
                .first()
            )
            if plan:
                return plan

    # Fallbacks
    plan = (
        SubscriptionPlan.objects.filter(
            plan_type="pro", billing_cycle="monthly", is_active=True
        )
        .order_by("sort_order", "name")
        .first()
    )
    if plan:
        return plan
    return (
        SubscriptionPlan.objects.filter(is_active=True)
        .order_by("sort_order", "name")
        .first()
    )


def handle_invoice_payment_succeeded(invoice):
    """Handle Stripe `invoice.payment_succeeded` with auto-create of UserSubscription if missing."""
    try:
        subscription_id = _get(invoice, "subscription")
        if not subscription_id:
            logger.warning(
                "invoice.payment_succeeded without subscription id; skipping."
            )
            return None

        customer_id = _get(invoice, "customer")
        meta = _get(invoice, "metadata") or {}
        user_id = meta.get("user_id")
        customer_email = _get(invoice, "customer_email")

        # Try to find an existing subscription
        subscription = (
            UserSubscription.objects.select_related("plan", "user")
            .filter(stripe_subscription_id=subscription_id)
            .first()
        )

        if not subscription and customer_id:
            subscription = (
                UserSubscription.objects.select_related("plan", "user")
                .filter(stripe_customer_id=customer_id)
                .first()
            )

        # Auto-create if still not found
        if not subscription:
            # Resolve user
            user = None
            if user_id:
                user = get_user_model().objects.filter(pk=user_id).first()
            if not user and customer_email:
                user = (
                    get_user_model()
                    .objects.filter(email__iexact=customer_email)
                    .first()
                )
            if not user and customer_id:
                # As a last resort, borrow user from any prior sub with same customer
                prior = (
                    UserSubscription.objects.select_related("user")
                    .filter(stripe_customer_id=customer_id)
                    .first()
                )
                if prior:
                    user = prior.user

            if not user:
                logger.warning(
                    "invoice.payment_succeeded: cannot auto-create UserSubscription (no user). "
                    "subscription_id=%s customer_id=%s user_id=%s customer_email=%s",
                    subscription_id,
                    customer_id,
                    user_id,
                    customer_email,
                )
                return None

            # Resolve plan from invoice
            plan = _resolve_plan_from_invoice(invoice)
            if not plan:
                logger.warning(
                    "invoice.payment_succeeded: cannot auto-create UserSubscription (no plan). "
                    "subscription_id=%s customer_id=%s",
                    subscription_id,
                    customer_id,
                )
                return None

            # Periods (prefer invoice line period)
            period_start, period_end = _first_line_period(invoice)
            if not period_start:
                period_start = timezone.now()
            if not period_end:
                bc = (plan.billing_cycle or "monthly").lower()
                period_end = period_start + (
                    timedelta(days=7)
                    if bc == "weekly"
                    else timedelta(days=365)
                    if bc == "yearly"
                    else timedelta(days=30)
                )

            subscription = UserSubscription.objects.create(
                user=user,
                plan=plan,
                stripe_subscription_id=subscription_id,
                stripe_customer_id=customer_id,
                status="active",
                current_period_start=period_start,
                current_period_end=period_end,
                cancel_at_period_end=False,
            )
            logger.info(
                "Created UserSubscription %s during invoice.payment_succeeded.",
                subscription.id,
            )

        # Derive/normalize periods
        period_start, period_end = _first_line_period(invoice)
        if not period_start:
            period_start = subscription.current_period_start or timezone.now()
        if not period_end:
            bc = (subscription.plan.billing_cycle or "monthly").lower()
            period_end = period_start + (
                timedelta(days=7)
                if bc == "weekly"
                else timedelta(days=365)
                if bc == "yearly"
                else timedelta(days=30)
            )

        # Prepare updates
        new_status = "active"
        dirty = []
        if subscription.status != new_status:
            subscription.status = new_status
            dirty.append("status")
        if subscription.current_period_start != period_start:
            subscription.current_period_start = period_start
            dirty.append("current_period_start")
        if subscription.current_period_end != period_end:
            subscription.current_period_end = period_end
            dirty.append("current_period_end")
        if customer_id and subscription.stripe_customer_id != customer_id:
            subscription.stripe_customer_id = customer_id
            dirty.append("stripe_customer_id")

        if dirty:
            dirty.append("modified")
            subscription.save(update_fields=dirty)

        # Idempotent PaymentHistory
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

        PaymentHistory.objects.update_or_create(
            stripe_invoice_id=invoice_id,
            defaults=ph_defaults,
        )

        logger.info(
            "Invoice payment succeeded for sub %s (updated fields: %s)",
            subscription.id,
            ", ".join(f for f in dirty if f != "modified") if dirty else "none",
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
