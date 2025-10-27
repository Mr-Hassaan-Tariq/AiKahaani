import logging
import stripe
from djstripe import webhooks
from djstripe.models import Subscription, Product, Price
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


@webhooks.handler("customer.subscription.updated")
def handle_subscription_auto_upgrade(event, **kwargs):
    """
    When a Free Trial subscription ends, upgrade to Basic Monthly automatically.
    """
    data = event.data["object"]
    subscription_id = data["id"]
    trial_end = data.get("trial_end")
    status = data.get("status")

    if not trial_end or status != "active":
        return  # skip if still on trial or inactive

    try:
        # Get the dj-stripe subscription record
        sub = Subscription.objects.get(id=subscription_id)
        item = sub.items.first()
        current_price = item.price

        # Get product metadata
        metadata = current_price.product.metadata or {}
        next_price_id = metadata.get("next_price_id")

        if not next_price_id:
            logger.info(f"No next_price_id found for product {current_price.product.name}")
            return

        # Retrieve next plan from dj-stripe
        try:
            next_price = Price.objects.get(id=next_price_id)
        except Price.DoesNotExist:
            logger.error(f"Next price {next_price_id} not found in dj-stripe database")
            return

        logger.info(f"Upgrading {subscription_id} → {next_price_id}")

        # Switch price on Stripe
        stripe.Subscription.modify(
            subscription_id,
            items=[{"id": item.id, "price": next_price.id}],
            proration_behavior="none",
            metadata={
                **(sub.metadata or {}),
                "upgraded_from_trial": "true",
            },
        )

        # SIMPLIFIED: Skip the sync to avoid database constraint issues
        # The subscription was successfully updated in Stripe
        # DJ-Stripe will sync the changes naturally via webhooks
        logger.info(f"✅ Subscription {subscription_id} upgraded in Stripe successfully!")

    except Subscription.DoesNotExist:
        logger.warning(f"Subscription {subscription_id} not found in local DB")
    except Exception as e:
        logger.exception(f"Error upgrading {subscription_id}: {e}")
