import logging
from decimal import Decimal

from djstripe.models import Price, Product

from payments.models import SubscriptionPlan

log = logging.getLogger(__name__)


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
                        log.info(f"Created new plan: {plan.name}")
                    else:
                        log.info(f"Updated existing plan: {plan.name}")

    except Exception as e:
        log.error(f"Error syncing plans from DJ-Stripe: {str(e)}")
        raise
