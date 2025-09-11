from django.contrib import admin

from .models import SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "plan_type",
        "billing_cycle",
        "price",
        "display_price",
        "is_active",
        "sort_order",
    ]
    list_filter = ["plan_type", "billing_cycle", "is_active"]
    search_fields = ["name", "description"]
    ordering = ["sort_order", "name"]
    readonly_fields = ["display_price", "yearly_price", "monthly_price"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "plan_type", "billing_cycle", "price", "description")},
        ),
        (
            "Stripe Integration",
            {
                "fields": ("stripe_price_id", "stripe_product_id"),
                "classes": ("collapse",),
            },
        ),
        (
            "Features & Settings",
            {"fields": ("features", "trial_days", "is_active", "sort_order")},
        ),
        (
            "Calculated Fields",
            {
                "fields": ("display_price", "yearly_price", "monthly_price"),
                "classes": ("collapse",),
            },
        ),
    )
