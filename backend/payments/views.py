import logging
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SubscriptionPlan, UserSubscription, PaymentHistory
from .serializers import (
    SubscriptionPlanSerializer, UserSubscriptionSerializer,
    CreateSubscriptionSerializer, PaymentHistorySerializer
)

logger = logging.getLogger(__name__)


def sync_plans_from_djstripe():
    """Sync plans from DJ-Stripe to our local SubscriptionPlan model"""
    try:
        from djstripe.models import Product, Price
        
        # Get all products from DJ-Stripe
        products = Product.objects.all()
        
        for product in products:
            # Get prices for this product
            prices = Price.objects.filter(product=product)
            
            for price in prices:
                if price.recurring:  # Only process recurring prices
                    # Map plan type from metadata or default to 'pro'
                    plan_type = product.metadata.get('plan_type', 'pro')
                    
                    # Fix plan type mapping
                    if plan_type == 'free_trial':
                        plan_type = 'trial'
                    
                    # Map billing cycle
                    billing_cycle = price.recurring.get('interval', 'month')
                    if billing_cycle == 'month':
                        billing_cycle = 'monthly'
                    elif billing_cycle == 'year':
                        billing_cycle = 'yearly'
                    elif billing_cycle == 'week':
                        billing_cycle = 'weekly'
                    
                    # Calculate price in dollars
                    price_amount = Decimal(price.unit_amount) / 100
                    
                    # Create or update plan
                    plan, created = SubscriptionPlan.objects.update_or_create(
                        plan_type=plan_type,
                        billing_cycle=billing_cycle,
                        defaults={
                            'name': product.name,
                            'price': price_amount,
                            'description': product.description or '',
                            'stripe_product_id': product.id,
                            'stripe_price_id': price.id,
                            'is_active': product.active,
                            'features': product.metadata.get('features', {}),
                            'trial_days': int(product.metadata.get('trial_days', 0)),
                            'sort_order': int(product.metadata.get('sort_order', 0))
                        }
                    )
                    
                    if created:
                        logger.info(f"Created new plan: {plan.name}")
                    else:
                        logger.info(f"Updated existing plan: {plan.name}")
                        
    except Exception as e:
        logger.error(f"Error syncing plans from DJ-Stripe: {str(e)}")
        raise


logger = logging.getLogger(__name__)


class SubscriptionPlansView(APIView):
    """View to fetch all available subscription plans"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Get all subscription plans",
        description="Retrieve all active subscription plans with their features and pricing",
        responses={
            200: OpenApiResponse(
                description="List of subscription plans",
                response=SubscriptionPlanSerializer(many=True)
            )
        },
        tags=["Subscription Plans"]
    )
    def get(self, request):
        """GET /api/plans - Fetch all active subscription plans"""
        try:
            # Sync plans from DJ-Stripe first
            sync_plans_from_djstripe()
            
            plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'name')
            serializer = SubscriptionPlanSerializer(plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching subscription plans: {str(e)}")
            return Response(
                {"error": "Failed to fetch subscription plans"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSubscriptionView(APIView):
    """View to manage user subscriptions"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get user subscription",
        description="Retrieve the current user's subscription details",
        responses={
            200: OpenApiResponse(
                description="User subscription details",
                response=UserSubscriptionSerializer
            ),
            404: OpenApiResponse(description="No subscription found")
        },
        tags=["User Subscriptions"]
    )
    def get(self, request):
        """GET /api/subscription - Get current user's subscription"""
        try:
            subscription = UserSubscription.objects.filter(user=request.user).first()
            if not subscription:
                return Response(
                    {"error": "No subscription found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = UserSubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching user subscription: {str(e)}")
            return Response(
                {"error": "Failed to fetch subscription"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Create user subscription",
        description="Create a new subscription for the current user",
        request=CreateSubscriptionSerializer,
        responses={
            201: OpenApiResponse(
                description="Subscription created successfully",
                response=UserSubscriptionSerializer
            ),
            400: OpenApiResponse(description="Invalid data provided")
        },
        tags=["User Subscriptions"]
    )
    def post(self, request):
        """POST /api/subscription - Create a new subscription"""
        try:
            serializer = CreateSubscriptionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            plan_id = serializer.validated_data['plan_id']
            billing_cycle = serializer.validated_data['billing_cycle']
            
            # Get the plan
            try:
                plan = SubscriptionPlan.objects.get(
                    id=plan_id,
                    billing_cycle=billing_cycle,
                    is_active=True
                )
            except SubscriptionPlan.DoesNotExist:
                return Response(
                    {"error": "Invalid plan or billing cycle"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user already has a subscription
            existing_subscription = UserSubscription.objects.filter(user=request.user).first()
            if existing_subscription:
                return Response(
                    {"error": "User already has a subscription"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Import DJ-Stripe models
            from djstripe.models import Customer, Session
            
            # Create Stripe customer using DJ-Stripe
            customer, created = Customer.get_or_create(
                subscriber=request.user,
                defaults={
                    'email': request.user.email,
                    'name': request.user.fullname or request.user.username,
                    'metadata': {
                        'user_id': str(request.user.id),
                        'username': request.user.username
                    }
                }
            )
            
            # Create subscription
            subscription = UserSubscription.objects.create(
                user=request.user,
                plan=plan,
                stripe_customer_id=customer.id,
                status='trial' if plan.plan_type == 'trial' else 'incomplete'
            )
            
            # Set trial dates if it's a trial plan
            if plan.plan_type == 'trial' and plan.trial_days > 0:
                subscription.trial_start = timezone.now()
                subscription.trial_end = timezone.now() + timedelta(days=plan.trial_days)
                subscription.save()
            
            # Create Stripe checkout session using DJ-Stripe
            checkout_session = Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': plan.name,
                            'description': plan.description,
                        },
                        'unit_amount': int(plan.price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/dashboard?success=true",
                cancel_url=f"{settings.FRONTEND_URL}/dashboard?canceled=true",
                metadata={
                    'user_id': str(request.user.id),
                    'plan_id': str(plan.id),
                    'subscription_id': str(subscription.id)
                }
            )
            
            subscription.stripe_subscription_id = checkout_session.id
            subscription.save()
            
            return Response({
                "message": "Subscription created successfully",
                "checkout_url": checkout_session.url,
                "subscription": UserSubscriptionSerializer(subscription).data
            }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return Response(
                {"error": "Failed to create subscription"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentHistoryView(APIView):
    """View to fetch user payment history"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get payment history",
        description="Retrieve the current user's payment history",
        responses={
            200: OpenApiResponse(
                description="Payment history",
                response=PaymentHistorySerializer(many=True)
            )
        },
        tags=["Payment History"]
    )
    def get(self, request):
        """GET /api/payments/history - Get user's payment history"""
        try:
            payments = PaymentHistory.objects.filter(user=request.user).order_by('-created')
            serializer = PaymentHistorySerializer(payments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching payment history: {str(e)}")
            return Response(
                {"error": "Failed to fetch payment history"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # Use DJ-Stripe webhook handling
        from djstripe.webhooks import construct_event_from_request
        event = construct_event_from_request(request)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        handle_checkout_session_completed(event['data']['object'])
    elif event['type'] == 'invoice.payment_succeeded':
        handle_invoice_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_invoice_payment_failed(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    elif event['type'] == 'product.created':
        handle_product_created(event['data']['object'])
    elif event['type'] == 'product.updated':
        handle_product_updated(event['data']['object'])
    elif event['type'] == 'price.created':
        handle_price_created(event['data']['object'])
    elif event['type'] == 'price.updated':
        handle_price_updated(event['data']['object'])
    
    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """Handle successful checkout completion"""
    try:
        user_id = session.metadata.get('user_id')
        subscription_id = session.metadata.get('subscription_id')
        
        if user_id and subscription_id:
            subscription = UserSubscription.objects.get(id=subscription_id)
            subscription.status = 'active'
            subscription.current_period_start = timezone.now()
            
            if subscription.plan.billing_cycle == 'monthly':
                subscription.current_period_end = timezone.now() + timedelta(days=30)
            elif subscription.plan.billing_cycle == 'weekly':
                subscription.current_period_end = timezone.now() + timedelta(days=7)
            else:
                subscription.current_period_end = timezone.now() + timedelta(days=365)
            
            subscription.save()
            
            PaymentHistory.objects.create(
                user=subscription.user,
                subscription=subscription,
                amount=subscription.plan.price,
                currency='usd',
                stripe_payment_intent_id=session.payment_intent,
                status='succeeded',
                description=f"Payment for {subscription.plan.name}",
                metadata={'checkout_session_id': session.id}
            )
            
            logger.info(f"Subscription {subscription_id} activated successfully")
            
    except Exception as e:
        logger.error(f"Error handling checkout session completed: {str(e)}")


def handle_invoice_payment_succeeded(invoice):
    """Handle successful invoice payment"""
    try:
        subscription_id = invoice.subscription
        if subscription_id:
            subscription = UserSubscription.objects.filter(
                stripe_subscription_id=subscription_id
            ).first()
            
            if subscription:
                subscription.status = 'active'
                subscription.current_period_start = timezone.now()
                
                if subscription.plan.billing_cycle == 'monthly':
                    subscription.current_period_end = timezone.now() + timedelta(days=30)
                elif subscription.plan.billing_cycle == 'weekly':
                    subscription.current_period_end = timezone.now() + timedelta(days=7)
                else:
                    subscription.current_period_end = timezone.now() + timedelta(days=365)
                
                subscription.save()
                
                PaymentHistory.objects.create(
                    user=subscription.user,
                    subscription=subscription,
                    amount=invoice.amount_paid / 100,
                    currency=invoice.currency,
                    stripe_invoice_id=invoice.id,
                    status='succeeded',
                    description=f"Recurring payment for {subscription.plan.name}",
                    metadata={'invoice_id': invoice.id}
                )
                
                logger.info(f"Recurring payment succeeded for subscription {subscription.id}")
                
    except Exception as e:
        logger.error(f"Error handling invoice payment succeeded: {str(e)}")


def handle_invoice_payment_failed(invoice):
    """Handle failed invoice payment"""
    try:
        subscription_id = invoice.subscription
        if subscription_id:
            subscription = UserSubscription.objects.filter(
                stripe_subscription_id=subscription_id
            ).first()
            
            if subscription:
                subscription.status = 'past_due'
                subscription.save()
                
                logger.info(f"Payment failed for subscription {subscription.id}")
                
    except Exception as e:
        logger.error(f"Error handling invoice payment failed: {str(e)}")


def handle_subscription_updated(subscription_data):
    """Handle subscription updates"""
    try:
        subscription = UserSubscription.objects.filter(
            stripe_subscription_id=subscription_data.id
        ).first()
        
        if subscription:
            if subscription_data.status in ['active', 'trialing']:
                subscription.status = subscription_data.status
            elif subscription_data.status == 'canceled':
                subscription.status = 'canceled'
                subscription.canceled_at = timezone.now()
                subscription.cancel_at_period_end = subscription_data.cancel_at_period_end
            
            if subscription_data.current_period_start:
                subscription.current_period_start = datetime.fromtimestamp(
                    subscription_data.current_period_start, tz=timezone.utc
                )
            if subscription_data.current_period_end:
                subscription.current_period_end = datetime.fromtimestamp(
                    subscription_data.current_period_end, tz=timezone.utc
                )
            
            subscription.save()
            logger.info(f"Subscription {subscription.id} updated successfully")
            
    except Exception as e:
        logger.error(f"Error handling subscription updated: {str(e)}")


def handle_subscription_deleted(subscription_data):
    """Handle subscription deletion"""
    try:
        subscription = UserSubscription.objects.filter(
            stripe_subscription_id=subscription_data.id
        ).first()
        
        if subscription:
            subscription.status = 'canceled'
            subscription.canceled_at = timezone.now()
            subscription.save()
            
            logger.info(f"Subscription {subscription.id} deleted")
            
    except Exception as e:
        logger.error(f"Error handling subscription deleted: {str(e)}")


def handle_product_created(product):
    """Handle product creation in Stripe"""
    try:
        plan_type = product.metadata.get('plan_type', 'pro')
        billing_cycle = product.metadata.get('billing_cycle', 'monthly')
        
        # Create or update plan in database
        plan, created = SubscriptionPlan.objects.update_or_create(
            plan_type=plan_type,
            billing_cycle=billing_cycle,
            defaults={
                'name': product.name,
                'description': product.description or '',
                'stripe_product_id': product.id,
                'is_active': product.active,
                'features': product.metadata.get('features', {}),
                'trial_days': int(product.metadata.get('trial_days', 0)),
                'sort_order': int(product.metadata.get('sort_order', 0))
            }
        )
        
        if created:
            logger.info(f"Created plan from Stripe product: {plan.name}")
        else:
            logger.info(f"Updated plan from Stripe product: {plan.name}")
            
    except Exception as e:
        logger.error(f"Error handling product created: {str(e)}")


def handle_product_updated(product):
    """Handle product updates in Stripe"""
    try:
        plan = SubscriptionPlan.objects.filter(stripe_product_id=product.id).first()
        if plan:
            plan.name = product.name
            plan.description = product.description or plan.description
            plan.is_active = product.active
            plan.features = product.metadata.get('features', plan.features)
            plan.trial_days = int(product.metadata.get('trial_days', plan.trial_days))
            plan.sort_order = int(product.metadata.get('sort_order', plan.sort_order))
            plan.save()
            
            logger.info(f"Updated plan from Stripe product: {plan.name}")
            
    except Exception as e:
        logger.error(f"Error handling product updated: {str(e)}")


def handle_price_created(price):
    """Handle price creation in Stripe"""
    try:
        if not price.recurring:
            return
            
        plan_type = price.metadata.get('plan_type', 'pro')
        billing_cycle = price.recurring.interval
        
        if billing_cycle == 'month':
            billing_cycle = 'monthly'
        elif billing_cycle == 'year':
            billing_cycle = 'yearly'
        elif billing_cycle == 'week':
            billing_cycle = 'weekly'
        
        price_amount = price.unit_amount / 100
        
        # Update plan with price information
        plan = SubscriptionPlan.objects.filter(
            plan_type=plan_type,
            billing_cycle=billing_cycle
        ).first()
        
        if plan:
            plan.price = price_amount
            plan.stripe_price_id = price.id
            plan.save()
            
            logger.info(f"Updated plan price from Stripe: {plan.name} - ${plan.price}")
            
    except Exception as e:
        logger.error(f"Error handling price created: {str(e)}")


def handle_price_updated(price):
    """Handle price updates in Stripe"""
    try:
        if not price.recurring:
            return
            
        plan = SubscriptionPlan.objects.filter(stripe_price_id=price.id).first()
        if plan:
            plan.price = price.unit_amount / 100
            plan.save()
            
            logger.info(f"Updated plan price from Stripe: {plan.name} - ${plan.price}")
            
    except Exception as e:
        logger.error(f"Error handling price updated: {str(e)}")
