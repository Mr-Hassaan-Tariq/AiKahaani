import logging
import stripe
from djstripe import webhooks
from djstripe.models import Subscription, Product, Price, Invoice
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


@webhooks.handler("invoice.payment_succeeded")
def handle_payment_succeeded(event, **kwargs):
    """
    Track successful payments to Tolt for affiliate credit.
    
    This webhook fires when:
    - A subscription payment is successful (recurring billing)
    - A one-time payment is successful
    - First payment after trial ends
    """
    try:
        invoice_data = event.data["object"]
        invoice_id = invoice_data["id"]
        
        logger.info(f"[PAYMENT_WEBHOOK] Processing invoice: {invoice_id}")
        
        # Get the invoice from dj-stripe
        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            logger.warning(f"[PAYMENT_WEBHOOK] Invoice {invoice_id} not found in database")
            return
        
        # Get customer and user
        customer = invoice.customer
        if not customer or not customer.subscriber:
            logger.warning(f"[PAYMENT_WEBHOOK] No user found for invoice {invoice_id}")
            return
        
        user = customer.subscriber
        
        # Check if user has Tolt customer ID (was referred)
        if not user.tolt_customer_id:
            logger.info(f"[PAYMENT_WEBHOOK] User {user.email} has no referrer, skipping Tolt")
            return
        
        # Get payment details
        amount = int(invoice.amount_paid)  # Amount in cents
        charge_id = invoice.charge_id or invoice.payment_intent_id or invoice_id
        
        # Get product/plan name
        product_name = "Subscription"
        billing_type = "subscription"
        interval = "month"
        
        if invoice.lines.exists():
            line = invoice.lines.first()
            if line.price and line.price.product:
                product_name = line.price.product.name
                
                # Get billing interval
                if line.price.recurring:
                    interval = line.price.recurring.get("interval", "month")
        
        # Report to Tolt
        try:
            from affiliates.views import report_transaction_to_tolt
            
            success = report_transaction_to_tolt(
                user=user,
                charge_id=charge_id,
                amount=amount,
                product_name=product_name,
                billing_type=billing_type,
                interval=interval
            )
            
            if success:
                logger.info(
                    f"[PAYMENT_WEBHOOK] ✅ Tolt transaction reported for {user.email}: "
                    f"${amount/100:.2f} - {product_name}"
                )
            else:
                logger.warning(
                    f"[PAYMENT_WEBHOOK] ⚠️  Failed to report to Tolt for {user.email}"
                )
                
        except Exception as e:
            logger.error(f"[PAYMENT_WEBHOOK] Error reporting to Tolt: {str(e)}")
            # Don't fail the webhook - payment already succeeded
            
    except Exception as e:
        logger.error(f"[PAYMENT_WEBHOOK] Error processing invoice: {str(e)}")


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
