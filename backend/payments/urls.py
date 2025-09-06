from django.urls import include, path

from . import views

app_name = "payments"

urlpatterns = [
    # Subscription Plans
    path("plans/", views.SubscriptionPlansView.as_view(), name="subscription-plans"),
    # User Subscriptions
    path(
        "subscription/", views.UserSubscriptionView.as_view(), name="user-subscription"
    ),
    # Trial Status
    path("user/trial-status/", views.TrialStatusView.as_view(), name="trial-status"),
    # Payment History
    path("history/", views.PaymentHistoryView.as_view(), name="payment-history"),
    # Create Checkout Session
    path(
        "checkout/session/",
        views.CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    # Stripe Webhook
    path("webhook/stripe/", include("djstripe.urls")),
]
