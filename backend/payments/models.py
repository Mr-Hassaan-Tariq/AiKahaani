import uuid
from decimal import Decimal
from typing import Dict, Any

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver


class SubscriptionPlan(TimeStampedModel):
    """
    Subscription plans model to store plan information
    """
    PLAN_TYPES = [
        ('trial', 'Trial Plan'),
        ('basic', 'Basic Plan'),
        ('pro', 'Pro Plan'),
    ]
    
    BILLING_CYCLES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    features = models.JSONField(default=dict, help_text="Plan features as JSON")
    is_active = models.BooleanField(default=True)
    trial_days = models.PositiveIntegerField(default=0, help_text="Number of trial days")
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'subscription_plans'
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')
        ordering = ['sort_order', 'name']
        unique_together = ['plan_type', 'billing_cycle']
    
    def __str__(self):
        return f"{self.name} - {self.get_billing_cycle_display()}"
    
    @property
    def display_price(self) -> str:
        if self.plan_type == 'trial':
            return f"${self.price} / {self.trial_days} days"
        return f"${self.price}/{self.get_billing_cycle_display().lower()}"
    
    @property
    def yearly_price(self) -> Decimal:
        if self.billing_cycle == 'yearly':
            return self.price
        return self.price * 12
    
    @property
    def monthly_price(self) -> Decimal:
        if self.billing_cycle == 'monthly':
            return self.price
        return self.price / 12


class UserSubscription(TimeStampedModel):
    """
    User subscription model to track user's subscription status
    """
    SUBSCRIPTION_STATUS = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
        ('incomplete_expired', 'Incomplete Expired'),
        ('trialing', 'Trialing'),
        ('unpaid', 'Unpaid'),
        ('paused', 'Paused'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='user_subscriptions')
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='trial')
    current_period_start = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
    trial_start = models.DateTimeField(blank=True, null=True)
    trial_end = models.DateTimeField(blank=True, null=True)
    canceled_at = models.DateTimeField(blank=True, null=True)
    cancel_at_period_end = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'user_subscriptions'
        verbose_name = _('User Subscription')
        verbose_name_plural = _('User Subscriptions')
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
    
    @property
    def is_active(self) -> bool:
        return self.status in ['active', 'trialing', 'trial']
    
    @property
    def is_trial(self) -> bool:
        return self.status in ['trial', 'trialing']
    
    @property
    def days_until_expiry(self) -> int:
        if self.current_period_end:
            delta = self.current_period_end - timezone.now()
            return max(0, delta.days)
        return 0
    
    @property
    def trial_days_remaining(self) -> int:
        if self.trial_end and self.is_trial:
            delta = self.trial_end - timezone.now()
            return max(0, delta.days)
        return 0
    
    @property
    def trial_expiration_date(self) -> str:
        """Return trial expiration date in ISO format"""
        if self.trial_end:
            return self.trial_end.isoformat()
        return None


class PaymentHistory(TimeStampedModel):
    """
    Payment history model to track all payment transactions
    """
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_invoice_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'payment_history'
        verbose_name = _('Payment History')
        verbose_name_plural = _('Payment History')
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.user.email} - ${self.amount} - {self.status}"


# Signal to auto-assign trial plan to new users
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_trial_subscription(sender, instance, created, **kwargs):
    """Auto-assign trial plan to new users"""
    if created:
        try:
            # Get the trial plan
            trial_plan = SubscriptionPlan.objects.filter(
                plan_type='trial',
                is_active=True
            ).first()
            
            if trial_plan:
                # Calculate trial end date
                trial_start = timezone.now()
                trial_end = trial_start + timezone.timedelta(days=trial_plan.trial_days)
                
                # Create user subscription
                UserSubscription.objects.create(
                    user=instance,
                    plan=trial_plan,
                    status='trial',
                    trial_start=trial_start,
                    trial_end=trial_end,
                    current_period_start=trial_start,
                    current_period_end=trial_end
                )
        except Exception as e:
            # Log error but don't fail user creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create trial subscription for user {instance.email}: {str(e)}")
