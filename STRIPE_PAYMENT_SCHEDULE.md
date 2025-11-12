# Stripe Payment Schedule - Current Implementation

## Current Payment Model

### ✅ **One-Time Payments (Pay-As-You-Go)**

**Current Implementation**: `mode='payment'` in Stripe Checkout

**How it works**:
- Users purchase hours **one time** via Stripe Checkout
- Payment is processed **immediately** when checkout completes
- Hours are added to license **immediately** after payment
- **No recurring charges** - users pay only when they buy more hours

**Code Reference**:
```python
# redline/web/routes/payments.py, line 74
checkout_session = stripe.checkout.Session.create(
    ...
    mode='payment',  # One-time payment
    ...
)
```

## Payment Schedule Details

### Current Schedule: **One-Time / Pay-As-You-Go**

| Payment Type | Schedule | When Charged | Frequency |
|-------------|----------|--------------|-----------|
| **Hour Packages** | One-time | Immediately | When user purchases |
| **Custom Hours** | One-time | Immediately | When user purchases |

**Example**:
- User buys 10 hours for $45 → **Charged $45 once**
- User uses 5 hours → **No additional charge**
- User buys 20 more hours → **Charged $80 once**

### Payment Processing Timeline

1. **User initiates purchase** → Creates Stripe Checkout session
2. **User completes payment** → Stripe processes payment immediately
3. **Webhook received** → `checkout.session.completed` event
4. **Hours added** → License updated with purchased hours
5. **Payment complete** → One-time transaction finished

## Stripe Payment Modes Available

### 1. `mode='payment'` (Current - One-Time)
**What it is**: Single, immediate payment
**When charged**: Once, at checkout
**Use case**: Pay-as-you-go hour purchases

**Pros**:
- ✅ Simple for users
- ✅ No recurring commitments
- ✅ Users control spending
- ✅ No subscription management

**Cons**:
- ❌ Users must manually purchase more hours
- ❌ No predictable revenue
- ❌ Users can run out of hours unexpectedly

### 2. `mode='subscription'` (Not Implemented)
**What it is**: Recurring payments on a schedule
**When charged**: Automatically on schedule (monthly, annual, etc.)
**Use case**: Monthly/annual subscriptions

**Pros**:
- ✅ Predictable revenue
- ✅ Automatic renewals
- ✅ Better user experience (no manual purchases)
- ✅ Can include automatic hour allocation

**Cons**:
- ❌ More complex to implement
- ❌ Users locked into recurring charges
- ❌ Need subscription management

### 3. `mode='setup'` (Not Implemented)
**What it is**: Save payment method for future use
**When charged**: Not charged, just saves card
**Use case**: Save card for future one-click purchases

**Pros**:
- ✅ Faster checkout for repeat customers
- ✅ Better user experience

**Cons**:
- ❌ Still requires manual purchases
- ❌ Additional PCI compliance considerations

## Recommended Payment Schedules

### Option 1: Keep Current (One-Time) + Add Auto-Purchase
**Model**: One-time payments with automatic top-up

**How it works**:
- Users set a "low balance threshold" (e.g., 1 hour remaining)
- When hours drop below threshold, automatically purchase more
- Uses saved payment method
- User gets notified before auto-purchase

**Implementation**:
```python
# Add to license data
'auto_purchase_enabled': True,
'auto_purchase_threshold': 1.0,  # hours
'auto_purchase_amount': 10,  # hours
'payment_method_id': 'pm_xxx'  # Saved Stripe payment method
```

### Option 2: Hybrid Model (Recommended)
**Model**: One-time purchases + Optional subscriptions

**How it works**:
- **Free Tier**: Pay-as-you-go (current model)
- **Standard Tier**: Monthly subscription with included hours
- **Professional Tier**: Annual subscription with bonus hours

**Implementation**:
```python
# Subscription mode
checkout_session = stripe.checkout.Session.create(
    mode='subscription',
    line_items=[{
        'price': 'price_monthly_standard',  # Stripe Price ID
        'quantity': 1,
    }],
    subscription_data={
        'metadata': {
            'license_key': license_key,
            'hours_per_month': 20
        }
    }
)
```

### Option 3: Subscription-Only Model
**Model**: All users on subscriptions

**Tiers**:
- **Starter**: $29/month → 10 hours/month
- **Professional**: $99/month → 50 hours/month
- **Enterprise**: $299/month → Unlimited hours

**Implementation**:
- Change `mode='subscription'` in checkout
- Create Stripe Products and Prices
- Handle subscription webhooks
- Allocate hours monthly

## Stripe Payment Schedule Options

### One-Time Payment (Current)
```python
mode='payment'
# Charged: Immediately
# Frequency: Once per purchase
# Renewal: Manual (user must purchase again)
```

### Monthly Subscription
```python
mode='subscription'
# Charged: Monthly on same date
# Frequency: Every month
# Renewal: Automatic
```

### Annual Subscription
```python
mode='subscription'
# Charged: Yearly on same date
# Frequency: Every year
# Renewal: Automatic
```

### Usage-Based Billing
```python
# Stripe Billing (not implemented)
# Charged: Based on actual usage
# Frequency: Monthly invoice
# Renewal: Automatic
```

## Stripe Payout Schedule (To Redline)

### Standard Payout Schedule
- **Timing**: 2 business days after payment
- **Frequency**: Daily (if balance > $1)
- **Method**: Bank transfer to Redline's account
- **Fees**: Stripe takes 2.9% + $0.30 per transaction

### Example Timeline
1. **Day 0**: User pays $45 for 10 hours
2. **Day 0**: Stripe processes payment ($45 - $1.61 fee = $43.39)
3. **Day 2**: $43.39 transferred to Redline's bank account

## Implementation Status

### ✅ Implemented
- One-time payments (`mode='payment'`)
- Immediate payment processing
- Webhook handling for payment confirmation
- Hours allocation after payment

### ❌ Not Implemented
- Recurring subscriptions (`mode='subscription'`)
- Saved payment methods
- Auto-purchase on low balance
- Subscription management
- Usage-based billing

## Adding Subscription Support

### Step 1: Create Stripe Products & Prices
```python
# Create product
product = stripe.Product.create(
    name="REDLINE Professional",
    description="50 hours/month access"
)

# Create price
price = stripe.Price.create(
    product=product.id,
    unit_amount=9900,  # $99.00
    currency='usd',
    recurring={
        'interval': 'month'
    }
)
```

### Step 2: Update Checkout Session
```python
checkout_session = stripe.checkout.Session.create(
    mode='subscription',  # Changed from 'payment'
    line_items=[{
        'price': price.id,  # Use Price ID instead of price_data
        'quantity': 1,
    }],
    subscription_data={
        'metadata': {
            'license_key': license_key,
            'hours_per_month': 50
        }
    }
)
```

### Step 3: Handle Subscription Webhooks
```python
# Handle subscription events
if event['type'] == 'invoice.payment_succeeded':
    # Monthly payment succeeded
    # Add hours to license
    subscription = event['data']['object']
    license_key = subscription['metadata']['license_key']
    hours = subscription['metadata']['hours_per_month']
    # Add hours to license
```

## Current Payment Schedule Summary

**Answer**: **One-time payments only** - users are charged immediately when they purchase hours. There is **no recurring schedule** - users must manually purchase more hours when they run out.

**Future Options**:
1. Keep one-time + add auto-purchase
2. Add subscription tiers (monthly/annual)
3. Hybrid model (both options available)

