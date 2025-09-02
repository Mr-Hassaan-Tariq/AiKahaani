from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    # Subscription Plans
    path('plans/', views.SubscriptionPlansView.as_view(), name='subscription-plans'),
    
    # User Subscriptions
    path('subscription/', views.UserSubscriptionView.as_view(), name='user-subscription'),
    
    # Payment History
    path('history/', views.PaymentHistoryView.as_view(), name='payment-history'),
    
    # Stripe Webhook
    path('webhook/stripe/', views.stripe_webhook, name='stripe-webhook'),
]
