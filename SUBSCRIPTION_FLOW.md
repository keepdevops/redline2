# Stripe Subscription Flow Diagram

## User Journey

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SUBSCRIPTION FLOW                             │
└─────────────────────────────────────────────────────────────────────┘

1. USER VISITS SUBSCRIPTION PAGE
   ┌──────────────────────────────────────┐
   │  GET /payments/subscription          │
   │  ────────────────────────────────    │
   │  • Display pricing ($5/hour)         │
   │  • Show features list                │
   │  • Email input form                  │
   │  • Subscribe button                  │
   └──────────────────────────────────────┘
                    │
                    │ User enters email
                    │ Clicks "Subscribe Now"
                    ▼
   ┌──────────────────────────────────────┐
   │  POST /payments/create-              │
   │       subscription-checkout          │
   │  ────────────────────────────────    │
   │  • Validate email                    │
   │  • Create Stripe Checkout Session    │
   │  • Return checkout URL               │
   └──────────────────────────────────────┘
                    │
                    │ Redirect to Stripe
                    ▼
   ┌──────────────────────────────────────┐
   │  STRIPE HOSTED CHECKOUT              │
   │  ────────────────────────────────    │
   │  • User enters payment details       │
   │  • Card: 4242 4242 4242 4242         │
   │  • Expiry: Any future date           │
   │  • CVC: Any 3 digits                 │
   │  • ZIP: Any 5 digits                 │
   └──────────────────────────────────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
     SUCCESS              CANCELLED
          │                   │
          ▼                   ▼
   ┌─────────────┐     ┌─────────────┐
   │   SUCCESS   │     │   CANCEL    │
   │    PAGE     │     │    PAGE     │
   └─────────────┘     └─────────────┘
          │                   │
          │                   │
          ▼                   ▼
   ┌─────────────┐     ┌─────────────┐
   │  Dashboard  │     │  Try Again  │
   │   Active    │     │  or Go Home │
   │Subscription │     │             │
   └─────────────┘     └─────────────┘
```

## Backend Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND PROCESSING                              │
└─────────────────────────────────────────────────────────────────────┘

POST /payments/create-subscription-checkout
│
├─ 1. Receive request with email
│
├─ 2. Validate email format
│
├─ 3. Call Stripe API
│    └─ stripe.checkout.Session.create({
│         mode: 'subscription',
│         line_items: [{ price: STRIPE_PRICE_ID_METERED }],
│         customer_email: email,
│         success_url: /payments/subscription-success,
│         cancel_url: /payments/subscription-cancel
│       })
│
├─ 4. Return checkout URL
│
└─ 5. Frontend redirects to Stripe
      │
      ├─ User completes payment ──► Stripe creates:
      │                               - Customer
      │                               - Subscription
      │                               - Payment Method
      │
      └─ Stripe redirects back ──► Success or Cancel page
```

## Webhook Flow (Post-Subscription)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WEBHOOK EVENTS                                │
└─────────────────────────────────────────────────────────────────────┘

Stripe sends webhook to: POST /payments/webhook
│
├─ customer.subscription.created
│  └─ Action: Store subscription in Supabase
│      - user_id (from Supabase Auth)
│      - stripe_customer_id
│      - stripe_subscription_id
│      - subscription_status = 'active'
│
├─ customer.subscription.updated
│  └─ Action: Update subscription status
│      - status (active/past_due/canceled)
│
├─ customer.subscription.deleted
│  └─ Action: Revoke access
│      - subscription_status = 'canceled'
│
├─ invoice.payment_succeeded
│  └─ Action: Log payment
│      - Store in payment_history table
│      - Reset usage counter for new period
│
└─ invoice.payment_failed
   └─ Action: Handle failed payment
       - Notify user
       - subscription_status = 'past_due'
```

## Usage Reporting Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     METERED USAGE TRACKING                           │
└─────────────────────────────────────────────────────────────────────┘

User processes data (DuckDB, conversions, etc.)
│
├─ 1. Track processing time
│      - Start time: timestamp
│      - End time: timestamp
│      - Duration: 2.5 hours
│
├─ 2. Log to Supabase
│      INSERT INTO usage_history {
│        user_id,
│        stripe_customer_id,
│        hours_used: 2.5,
│        job_id,
│        api_endpoint
│      }
│
├─ 3. Report to Stripe
│      stripe.SubscriptionItem.create_usage_record({
│        subscription_item_id,
│        quantity: 250,  # 2.5 hours × 100
│        timestamp: now()
│      })
│
└─ 4. Stripe accumulates usage
       └─ At end of billing period:
          - Total usage: 10.5 hours
          - Charge: 10.5 × $5 = $52.50
          - Generate invoice
          - Charge payment method
          - Send invoice to customer
```

## Integration with Supabase (Future)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SUPABASE INTEGRATION                              │
└─────────────────────────────────────────────────────────────────────┘

After subscription checkout:
│
├─ 1. Create Supabase Auth user
│      supabase.auth.signUp({
│        email,
│        password: auto-generated
│      })
│      └─ Returns: user_id
│
├─ 2. Create user profile in PostgreSQL
│      INSERT INTO public.users {
│        id: user_id,
│        email,
│        stripe_customer_id,
│        stripe_subscription_id,
│        subscription_status: 'active'
│      }
│
├─ 3. Generate JWT token
│      token = supabase.auth.getSession()
│
└─ 4. Return to frontend
       └─ Store JWT token in:
          - Cookie: sb-access-token
          - localStorage: redline_auth
```

## File Structure

```
redline/
├── web/
│   ├── templates/
│   │   ├── subscription.html              # Landing page
│   │   ├── subscription_success.html      # Success page
│   │   └── subscription_cancel.html       # Cancel page
│   │
│   └── routes/
│       ├── payments_checkout.py           # Checkout session creation
│       ├── payments_tab.py                # Page routes
│       └── payments_webhook.py            # Webhook handlers
│
├── payment/
│   └── config.py                          # Stripe configuration
│
├── .env.subscription.example              # Environment template
├── SUBSCRIPTION_SETUP.md                  # Setup guide
├── SUBSCRIPTION_FLOW.md                   # This file
└── test_subscription_setup.py             # Verification script
```

## Environment Variables Flow

```
.env file
│
├─ STRIPE_SECRET_KEY ────────────► Backend API calls
│                                   (create checkout, retrieve subscription)
│
├─ STRIPE_PUBLISHABLE_KEY ───────► Frontend (subscription.html)
│                                   (display in page for reference)
│
├─ STRIPE_WEBHOOK_SECRET ────────► Webhook verification
│                                   (verify webhook signature)
│
└─ STRIPE_PRICE_ID_METERED ──────► Checkout session creation
                                    (line_items price)
```

## Testing Checklist

```
☐ Set environment variables
☐ Run: ./test_subscription_setup.py
☐ Start Flask: python web_app.py
☐ Visit: http://localhost:8080/payments/subscription
☐ Enter test email
☐ Click Subscribe
☐ Redirected to Stripe Checkout
☐ Enter test card: 4242 4242 4242 4242
☐ Complete checkout
☐ Redirected to success page
☐ Check Stripe Dashboard → Customers → See new subscription
☐ Check Stripe Dashboard → Subscriptions → See active subscription
```

## Production Deployment

```
1. Switch to live keys
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...

2. Create webhook endpoint
   URL: https://yourdomain.com/payments/webhook
   Events: customer.subscription.*, invoice.*

3. Update environment
   STRIPE_WEBHOOK_SECRET=whsec_live_...

4. Test in production
   - Use real card (will charge $5/hour usage)
   - Verify webhook delivery
   - Check subscription created

5. Monitor
   - Stripe Dashboard → Payments
   - Stripe Dashboard → Subscriptions
   - Check logs for errors
```

---

For detailed setup instructions, see **SUBSCRIPTION_SETUP.md**
