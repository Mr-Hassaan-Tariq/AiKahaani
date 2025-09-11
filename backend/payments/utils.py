# payments/utils.py
import stripe
from django.conf import settings
import djstripe.models as djm  # <-- use module alias to avoid name collisions
from djstripe.enums import SubscriptionStatus

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

# Define which statuses count as "active enough" for access in your app
VALID_SUB_STATUSES = {
    SubscriptionStatus.active,
    SubscriptionStatus.trialing,
    # SubscriptionStatus.past_due,   # include if you still allow access on past_due
}
if hasattr(SubscriptionStatus, "paused"):
    VALID_SUB_STATUSES.add(SubscriptionStatus.paused)


def get_or_create_customer(user) -> djm.Customer:
    """
    Ensure a Stripe Customer exists for this user.
    """
    customer, _ = djm.Customer.get_or_create(subscriber=user)
    return customer


def get_active_subscription(customer: djm.Customer) -> djm.Subscription | None:
    """
    Return the latest subscription in a 'valid' status for this customer.
    Uses fully-qualified djstripe model to avoid import/name conflicts.
    """
    return (
        djm.Subscription.objects  
        .filter(
            customer=customer,
            status__in=VALID_SUB_STATUSES, 
        )
        .order_by("-created")
        .first()
    )


def ensure_single_active_subscription(customer: djm.Customer) -> djm.Subscription | None:
    """
    Your policy hook. For now just returns if there already is one.
    """
    return get_active_subscription(customer)


def resolve_price(price_id: str) -> djm.Price:
    """
    Ensure the Price exists locally in dj-stripe (lazy sync if missing).
    """
    try:
        return djm.Price.objects.get(id=price_id)
    except djm.Price.DoesNotExist:
        sp = stripe.Price.retrieve(price_id)
        return djm.Price.sync_from_stripe_data(sp)
