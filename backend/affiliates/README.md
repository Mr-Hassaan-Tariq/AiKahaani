# Tolt Affiliate Integration - ULTRA MINIMAL

This Django app handles Tolt affiliate tracking with **zero database tables**.

## Architecture Philosophy

**Why minimal?**
- Tolt already handles tracking, auditing, and analytics
- No need to duplicate data in our database
- Simpler code = fewer bugs
- If Tolt API fails, Stripe webhook retry handles it

## What We Store

**In User model:**
- `tolt_customer_id` - Links user to their Tolt customer record
- `tolt_partner_id` - The partner/referrer who referred this user

**In database tables:**
- NONE! Zero tables in affiliates app.

## API Flow

### 1. Track Referral Click
```
User lands on site with ?ref=ABC123
Frontend → POST /api/v1/affiliates/track-click/
Backend → Tolt API
Response: { "partner_id": "part_xyz..." }
Frontend stores partner_id in localStorage
```

### 2. User Signup (with partner_id)
```
User completes signup form
Frontend → POST /api/v1/auth/signup/ (with partner_id in body)
Backend → Creates user
Backend → Calls create_tolt_customer(user, partner_id) internally
Backend → Saves tolt_customer_id and tolt_partner_id to User model
Response: { "user": {...} }
```

### 3. Report Transaction (From Stripe Webhook)
```
Stripe → Payment succeeded webhook
Backend → Check if user.tolt_customer_id exists
Backend → Call Tolt API to report transaction
Tolt → Credits referrer's account
```

## Files

- `models.py` - Empty (no models!)
- `admin.py` - Empty (no admin!)
- `views.py` - 2 functions:
  - `track_referral_click()` - API endpoint (no auth)
  - `create_tolt_customer()` - Helper function (called from signup)
  - `report_transaction_to_tolt()` - Helper function (called from Stripe webhook)
- `services/tolt_service.py` - Tolt API client
- `serializers.py` - Request/response validation
- `urls.py` - URL routing (only /track-click/)

## Setup

1. **Add to settings.py:**
```python
INSTALLED_APPS = [
    # ...
    "affiliates",
]

TOLT_API_KEY = os.getenv("TOLT_API_KEY")
TOLT_API_BASE_URL = os.getenv("TOLT_API_BASE_URL", "https://api.tolt.com/v1")
```

2. **Run migrations (only for User model changes):**
```bash
cd backend
uv run python manage.py makemigrations users
uv run python manage.py migrate
```

3. **Add to Stripe webhook:**
```python
# In payments/webhooks.py
from affiliates.views import report_transaction_to_tolt

# After successful payment
if user.tolt_customer_id:
    report_transaction_to_tolt(
        user=user,
        charge_id=charge.id,
        amount=charge.amount,
        product_name=subscription.plan.name
    )
```

## Environment Variables

```bash
# Required
TOLT_API_KEY="your_api_key_here"

# Optional (defaults to https://api.tolt.com/v1)
TOLT_API_BASE_URL="https://api.tolt.com/v1"
```

## Frontend Integration

```javascript
// 1. Landing page - capture referral
const urlParams = new URLSearchParams(window.location.search);
const ref = urlParams.get('ref');

if (ref) {
  const response = await fetch('/api/v1/affiliates/track-click/', {
    method: 'POST',
    body: JSON.stringify({
      referral_code: ref,
      page_url: window.location.href,
      device_type: 'desktop'
    })
  });
  
  const { partner_id } = await response.json();
  localStorage.setItem('tolt_partner_id', partner_id);
}

// 2. Signup - send partner_id with signup data
const partnerId = localStorage.getItem('tolt_partner_id');
const signupData = {
  email: 'user@example.com',
  username: 'username',
  password: 'password',
  password2: 'password',
  fullname: 'Full Name',
  partner_id: partnerId  // ← Add partner_id to signup
};

const response = await fetch('/api/v1/auth/signup/', {
  method: 'POST',
  body: JSON.stringify(signupData)
});

// Backend will automatically create Tolt customer
localStorage.removeItem('tolt_partner_id'); // Clean up
```

## Testing

```bash
# Track click
curl -X POST http://localhost:8000/api/v1/affiliates/track-click/ \
  -H "Content-Type: application/json" \
  -d '{
    "referral_code": "ABC123",
    "page_url": "https://tubegenius.com?ref=ABC123",
    "device_type": "desktop"
  }'

# Signup with partner_id (creates Tolt customer automatically)
curl -X POST http://localhost:8000/api/v1/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "password2": "password123",
    "fullname": "Test User",
    "partner_id": "part_s7mbzRGn46BhVgNFHD6fDgXW"
  }'
```

## Why No Database Tables?

**You asked the right question!** Here's why we removed all tables:

1. **Tolt handles tracking** - No need to store click data
2. **Tolt handles auditing** - Transaction history lives in Tolt dashboard
3. **Tolt handles retries** - Their system is designed for this
4. **Stripe handles retries** - Webhook retries guarantee delivery
5. **Simpler = Better** - For MVP, store only what we need (2 fields in User model)

**Can we add tables later?**
Yes! If you need advanced analytics or attribution modeling, you can add:
- `ToltReferralClick` - For click-through rate analysis
- `ToltTransaction` - For retry logic if you don't trust Stripe/Tolt retries

But start minimal and add complexity only when needed.

## Next Steps

1. ✅ Run migrations for User model fields
2. ✅ Add TOLT_API_KEY to environment
3. ✅ Test endpoints manually
4. ✅ Integrate with Stripe webhook
5. ✅ Test with real Tolt API (sandbox mode)
6. ✅ Frontend integration
7. ✅ Monitor logs for errors
