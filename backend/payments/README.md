# Payments App

This Django app handles subscription plans, user subscriptions, and payment processing using Stripe with DJ-Stripe integration.

## Features

- **Subscription Plans**: Manage different subscription tiers with features and pricing
- **User Subscriptions**: Track user subscription status and billing cycles
- **Payment History**: Record all payment transactions
- **Stripe Integration**: Seamless integration with Stripe using DJ-Stripe
- **Webhook Handling**: Process Stripe webhooks for real-time updates and plan synchronization

## Models

### SubscriptionPlan
- Stores plan information (name, type, billing cycle, price, features)
- Links to Stripe products and prices via DJ-Stripe
- Supports weekly, monthly and yearly billing cycles
- Includes trial period configuration

### UserSubscription
- Tracks user's subscription status
- Links to Stripe customer and subscription IDs via DJ-Stripe
- Manages trial periods and billing cycles
- Automatic status updates via webhooks

### PaymentHistory
- Records all payment transactions
- Links to Stripe payment intents and invoices
- Tracks payment status and metadata

## API Endpoints

### Public Endpoints
- `GET /api/v1/payments/plans/` - List all active subscription plans

### Protected Endpoints
- `GET /api/v1/payments/subscription/` - Get current user's subscription
- `POST /api/v1/payments/subscription/` - Create new subscription
- `GET /api/v1/payments/history/` - Get user's payment history

### Webhook Endpoints
- `POST /api/v1/payments/webhook/stripe/` - Handle Stripe webhooks

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Add the following to your `.env` file:
```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Stripe Test Keys (for development)
STRIPE_TEST_SECRET_KEY=sk_test_your_test_secret_key_here
STRIPE_TEST_PUBLISHABLE_KEY=pk_test_your_test_publishable_key_here

# Stripe Live Mode (set to True for production)
STRIPE_LIVE_MODE=False

# Frontend URL for redirects
FRONTEND_URL=http://localhost:3000
```

### 3. Database Migrations
```bash
python manage.py makemigrations payments
python manage.py migrate
```

### 4. Create Plans in Stripe Dashboard

**IMPORTANT**: Plans must be created in Stripe Dashboard, not in the database. The app syncs plans from Stripe via webhooks using DJ-Stripe.

#### Create Products in Stripe:

1. **Trial Plan Product**
   - Name: "Trial Plan"
   - Description: "Start with a $1 trial to experience TubeGenius for 7 days"
   - Metadata:
     ```
     plan_type: trial
     billing_cycle: weekly
     trial_days: 7
     sort_order: 1
     features: {"script_generator": true, "title_niche_tools": true, "saved_scripts": true}
     ```

2. **Basic Plan Product**
   - Name: "Basic Plan"
   - Description: "Perfect for beginners with essential tools"
   - Metadata:
     ```
     plan_type: basic
     billing_cycle: monthly
     trial_days: 0
     sort_order: 2
     features: {"script_generator": true, "title_niche_tools": true, "saved_scripts": true, "ai_title_optimizer": true, "personal_niche_recommendations": true, "script_limit": 20}
     ```

3. **Pro Plan Product**
   - Name: "Pro Plan"
   - Description: "Ideal for advanced creators with analytics and affiliate tools"
   - Metadata:
     ```
     plan_type: pro
     billing_cycle: monthly
     trial_days: 0
     sort_order: 3
     features: {"script_generator": true, "title_niche_tools": true, "saved_scripts": true, "ai_title_optimizer": true, "personal_niche_recommendations": true, "advanced_analytics": true, "affiliate_tracking": true, "priority_support": true, "unlimited_scripts": true}
     ```

#### Create Prices for Each Product:

1. **Trial Plan Price**: $1.00, Weekly recurring
2. **Basic Plan Price**: $29.00, Monthly recurring  
3. **Pro Plan Price**: $29.00, Monthly recurring

### 5. Configure Stripe Webhook
In your Stripe dashboard, create a webhook endpoint pointing to:
```
https://yourdomain.com/api/v1/payments/webhook/stripe/
```

Add these events:
- `checkout.session.completed`
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `product.created`
- `product.updated`
- `price.created`
- `price.updated`

### 6. Sync Plans from Stripe
```bash
python manage.py sync_stripe_plans
```

## Usage

### Creating a Subscription
```python
from payments.models import SubscriptionPlan, UserSubscription

# Get a plan
plan = SubscriptionPlan.objects.get(plan_type='basic', billing_cycle='monthly')

# Create subscription for user
subscription = UserSubscription.objects.create(
    user=user,
    plan=plan,
    status='trial'
)
```

### Checking Subscription Status
```python
# Check if user has active subscription
if user.subscription.is_active:
    # User can access premium features
    pass

# Check trial status
if user.subscription.is_trial:
    days_remaining = user.subscription.trial_days_remaining
```

### Managing Plans
```python
# Get all active plans
active_plans = SubscriptionPlan.objects.filter(is_active=True)

# Get plans by type
basic_plans = SubscriptionPlan.objects.filter(plan_type='basic')

# Get plans by billing cycle
monthly_plans = SubscriptionPlan.objects.filter(billing_cycle='monthly')
```

## Workflow

### 1. User Signup
- User creates account
- Redirected to onboarding with plan selection

### 2. Plan Selection
- User chooses between trial ($1) or basic/pro plan
- Redirected to Stripe checkout

### 3. Payment Processing
- Stripe handles payment via DJ-Stripe
- Webhook updates subscription status
- User gains access to app features

### 4. Trial Management
- Trial automatically ends after 7 days
- User automatically upgraded to basic plan
- Billing continues automatically

### 5. Subscription Management
- Users manage subscriptions through Stripe portal
- Support for upgrades, downgrades, cancellations
- Automatic proration for billing changes

## Webhook Events

The app handles the following Stripe webhook events using DJ-Stripe:

### Subscription Events
- `checkout.session.completed`: Activates subscription after payment
- `invoice.payment_succeeded`: Handles recurring payments
- `invoice.payment_failed`: Updates subscription status
- `customer.subscription.updated`: Syncs subscription changes
- `customer.subscription.deleted`: Marks subscription as canceled

### Product/Price Events
- `product.created`: Creates new plan in database
- `product.updated`: Updates existing plan
- `price.created`: Updates plan pricing
- `price.updated`: Syncs price changes

## DJ-Stripe Integration

This app uses DJ-Stripe for:
- **Customer Management**: Automatic customer creation and linking
- **Webhook Processing**: Secure webhook signature verification
- **API Calls**: Simplified Stripe API interactions
- **Data Synchronization**: Automatic sync between Stripe and local database

## Admin Interface

The app provides a comprehensive admin interface for:
- Managing subscription plans
- Viewing user subscriptions
- Tracking payment history
- Monitoring subscription status

## Testing

Run tests with:
```bash
python manage.py test payments
```

## Security Considerations

- All payment processing handled by Stripe via DJ-Stripe
- Webhook signatures verified by DJ-Stripe
- Sensitive data not stored locally
- HTTPS required for webhooks in production

## Troubleshooting

### Common Issues

1. **Webhook not receiving events**
   - Check webhook endpoint URL
   - Verify webhook secret in environment
   - Check Stripe dashboard for failed deliveries

2. **Plans not syncing**
   - Verify Stripe API keys
   - Check plan metadata in Stripe
   - Run sync command with debug output

3. **Subscription status not updating**
   - Check webhook configuration
   - Verify webhook secret
   - Check logs for webhook processing errors

### Debug Mode
Enable debug logging in Django settings:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'payments': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'djstripe': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Contributing

1. Follow existing code patterns
2. Add tests for new functionality
3. Update documentation
4. Use proper error handling and logging

## License

This app is part of the TubeGenius project.
