from django.urls import path

from payments.sync_views import StripeProductPriceSyncView

from . import views

app_name = "payments"

urlpatterns = [
    # Subscription Plans
    path("plans/", views.SubscriptionPlansView.as_view(), name="subscription-plans"),
    # User Subscriptions
    path(
        "subscription/", views.UserSubscriptionView.as_view(), name="user-subscription"
    ),
    path(
        "checkout/session/",
        views.CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path(
        "billing-portal/",
        views.CreateBillingPortalSessionView.as_view(),
        name="create-billing-portal",
    ),
    # Trial Status
    path(
        "user/trial-status/",
        views.TrialStatusView.as_view(),
        name="trial-status",
    ),
    path(
        "admin/sync-prices/", StripeProductPriceSyncView.as_view(), name="sync-prices"
    ),
]
