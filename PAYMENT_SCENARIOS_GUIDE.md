# Payment Scenarios Testing Guide

## Overview

This guide covers testing various payment scenarios to ensure the payment system works correctly in all situations.

## Test Scenarios

### 1. All Hour Packages

Test each predefined package:
- Small: 5 hours for $25
- Medium: 10 hours for $45
- Large: 20 hours for $80
- XLarge: 50 hours for $180

**Run test:**
```bash
python3 test_payment_scenarios.py --scenario packages
```

**What to verify:**
- Each package creates checkout successfully
- Prices match expected values
- Hours match package description
- Payment completes successfully
- Hours added correctly

### 2. Custom Hours Purchase

Test purchasing custom amounts of hours:
- 1 hour
- 15 hours
- 25 hours
- 100 hours

**Run test:**
```bash
python3 test_payment_scenarios.py --scenario custom
```

**What to verify:**
- Custom hours calculate price correctly ($5/hour base)
- Checkout created successfully
- Payment processes correctly
- Exact hours added to license

### 3. Multiple Purchases

Test making multiple purchases on the same license:
- Purchase 5 hours
- Purchase 10 hours
- Purchase 20 hours
- Verify hours accumulate

**Run test:**
```bash
python3 test_payment_scenarios.py --scenario multiple
```

**What to verify:**
- Each purchase adds hours correctly
- Hours accumulate (don't replace)
- Balance updates after each purchase
- Payment history shows all purchases

### 4. Balance Checks

Test balance checking functionality:
- Check balance with valid license
- Verify hours remaining
- Check purchased vs used hours

**Run test:**
```bash
python3 test_payment_scenarios.py --scenario balance
```

**What to verify:**
- Balance returns correct hours
- Purchased hours tracked correctly
- Used hours tracked correctly
- Balance updates after purchases

### 5. Invalid License Handling

Test error handling:
- Invalid license key
- Missing license key
- Expired license

**Run test:**
```bash
python3 test_payment_scenarios.py --scenario invalid
```

**What to verify:**
- Invalid keys rejected properly
- Error messages clear
- No crashes on invalid input

### 6. Payment Failures

Test declined payment scenarios:
- Card declined (4000 0000 0000 0002)
- Insufficient funds (4000 0000 0000 9995)
- Expired card (4000 0000 0000 0069)

**Manual test:**
1. Create checkout session
2. Use declined test card
3. Verify payment fails
4. Verify no hours added
5. Verify error handling

### 7. Webhook Processing

Test webhook delivery and processing:
- Webhook received from Stripe
- Signature verification
- Hours added via webhook
- Payment logged to database

**Check:**
- Stripe CLI shows `[200]` responses
- Web app logs show webhook processing
- Hours added correctly
- Payment logged to database

### 8. Concurrent Purchases

Test multiple simultaneous purchases:
- Create multiple checkout sessions
- Complete payments simultaneously
- Verify all hours added correctly

**Manual test:**
1. Create multiple checkout sessions
2. Complete payments in parallel
3. Verify all hours added
4. Check balance is correct

## Running All Tests

```bash
python3 test_payment_scenarios.py --scenario all
```

## Test Cards Reference

### Successful Payments
- **Visa**: `4242 4242 4242 4242`
- **Mastercard**: `5555 5555 5555 4444`
- **American Express**: `3782 822463 10005`

### Declined Payments
- **Card declined**: `4000 0000 0000 0002`
- **Insufficient funds**: `4000 0000 0000 9995`
- **Expired card**: `4000 0000 0000 0069`

### 3D Secure
- **Requires authentication**: `4000 0025 0000 3155`
- **Authentication fails**: `4000 0000 0000 3055`

## Verification Checklist

After each test:

- [ ] Checkout session created
- [ ] Payment completed (or failed as expected)
- [ ] Webhook received (`[200]` in Stripe CLI)
- [ ] Hours added correctly (or not added if failed)
- [ ] Balance updated correctly
- [ ] Payment logged to database
- [ ] No errors in logs

## Expected Results

### Successful Payment
- Checkout URL generated
- Payment completes
- Webhook received (`[200]`)
- Hours added to license
- Balance updated
- Payment logged

### Failed Payment
- Checkout URL generated
- Payment declined
- No webhook (or failed webhook)
- No hours added
- Balance unchanged
- Error logged (if applicable)

## Troubleshooting

### Checkout Not Created
- Verify Stripe keys are set
- Check web app is running
- Verify license key is valid

### Payment Not Processing
- Check Stripe test mode
- Verify test card numbers
- Check Stripe dashboard for errors

### Hours Not Added
- Check webhook forwarding is running
- Verify license server is running
- Check web app logs for errors
- Verify webhook secret matches

### Balance Not Updating
- Check license server logs
- Verify API endpoint is accessible
- Check database for payment records

