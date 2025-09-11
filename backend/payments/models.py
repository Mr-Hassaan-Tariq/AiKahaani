import uuid
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class SubscriptionPlan(TimeStampedModel):
    """
    Subscription plans model to store plan information
    """

    PLAN_TYPES = [
        ("trial", "Trial Plan"),
        ("basic", "Basic Plan"),
        ("pro", "Pro Plan"),
    ]

    BILLING_CYCLES = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    features = models.JSONField(default=dict, help_text="Plan features as JSON")
    is_active = models.BooleanField(default=True)
    trial_days = models.PositiveIntegerField(
        default=0, help_text="Number of trial days"
    )
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "subscription_plans"
        verbose_name = _("Subscription Plan")
        verbose_name_plural = _("Subscription Plans")
        ordering = ["sort_order", "name"]
        unique_together = ["plan_type", "billing_cycle"]

    def __str__(self):
        return f"{self.name} - {self.get_billing_cycle_display()}"

    @property
    def display_price(self) -> str:
        if self.plan_type == "trial":
            return f"${self.price} / {self.trial_days} days"
        return f"${self.price}/{self.get_billing_cycle_display().lower()}"

    @property
    def yearly_price(self) -> Decimal:
        if self.billing_cycle == "yearly":
            return self.price
        return self.price * 12

    @property
    def monthly_price(self) -> Decimal:
        if self.billing_cycle == "monthly":
            return self.price
        return self.price / 12
