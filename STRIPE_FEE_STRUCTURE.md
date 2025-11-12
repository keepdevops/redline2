# Stripe Fee Structure - What Stripe Charges

## Standard Stripe Fees

### Online Payments (Current Implementation)

**Fee Structure**: **2.9% + $0.30** per successful transaction

**Breakdown**:
- **Percentage**: 2.9% of transaction amount
- **Fixed Fee**: $0.30 per transaction
- **Total**: Both fees apply to every payment

### Fee Examples

| Payment Amount | Stripe Fee | Net to Redline |
|---------------|------------|----------------|
| $5.00 | $0.45 (2.9% + $0.30) | $4.55 |
| $25.00 | $1.03 (2.9% + $0.30) | $23.97 |
| $45.00 | $1.61 (2.9% + $0.30) | $43.39 |
| $80.00 | $2.62 (2.9% + $0.30) | $77.38 |
| $100.00 | $3.20 (2.9% + $0.30) | $96.80 |
| $180.00 | $5.52 (2.9% + $0.30) | $174.48 |

### Formula

```
Stripe Fee = (Amount × 0.029) + $0.30
Net Amount = Amount - Stripe Fee
```

## Current REDLINE Pricing Impact

### Hour Packages with Stripe Fees

| Package | Price | Stripe Fee | Net Revenue | Hours | Effective Cost/Hour |
|---------|-------|------------|-------------|-------|---------------------|
| Small (5h) | $25.00 | $1.03 | $23.97 | 5 | $4.79/hour |
| Medium (10h) | $45.00 | $1.61 | $43.39 | 10 | $4.34/hour |
| Large (20h) | $80.00 | $2.62 | $77.38 | 20 | $3.87/hour |
| XLarge (50h) | $180.00 | $5.52 | $174.48 | 50 | $3.49/hour |

**Note**: Larger packages have better effective rates due to fixed fee being spread over more hours.

## Stripe Fee Variations

### 1. Standard Online Payments
- **Fee**: 2.9% + $0.30
- **Applies to**: Most online card payments
- **Current REDLINE**: Uses this rate

### 2. In-Person Payments (Not Used)
- **Fee**: 2.7% + $0.05
- **Applies to**: Physical card readers
- **REDLINE**: Not applicable (online only)

### 3. International Cards
- **Fee**: 2.9% + $0.30 + 1% (additional)
- **Applies to**: Cards issued outside US
- **Total**: ~3.9% + $0.30

### 4. Currency Conversion
- **Fee**: Additional 1% if currency conversion needed
- **Applies to**: Non-USD payments
- **REDLINE**: Currently USD only

### 5. Disputed Charges (Chargebacks)
- **Fee**: $15.00 per dispute (if lost)
- **Applies to**: Customer disputes a charge
- **Additional**: Original transaction fee not refunded

## Stripe Fee Calculation in Code

### Current Implementation
```python
# redline/web/routes/payments.py
# Stripe fees are automatically deducted
# No manual calculation needed - Stripe handles it

# Example: User pays $45
# Stripe charges: $45 × 0.029 + $0.30 = $1.61
# Redline receives: $45 - $1.61 = $43.39
```

### Manual Calculation (if needed)
```python
def calculate_stripe_fee(amount: float) -> float:
    """Calculate Stripe fee for a transaction"""
    percentage_fee = amount * 0.029  # 2.9%
    fixed_fee = 0.30  # $0.30
    return percentage_fee + fixed_fee

def calculate_net_revenue(amount: float) -> float:
    """Calculate net revenue after Stripe fees"""
    return amount - calculate_stripe_fee(amount)

# Example
gross = 45.00
fee = calculate_stripe_fee(gross)  # $1.61
net = calculate_net_revenue(gross)  # $43.39
```

## Stripe Payout Schedule

### When Redline Receives Money

**Timeline**:
1. **Day 0**: Customer pays $45
2. **Day 0**: Stripe processes payment
3. **Day 0-2**: Stripe holds funds (pending)
4. **Day 2**: Stripe transfers $43.39 to Redline's bank account

**Payout Frequency**:
- **Daily**: If balance > $1
- **Weekly**: If balance < $1 (less common)
- **Manual**: Can request instant payout (additional fee)

## Fee Impact on Pricing Strategy

### Current Pricing
- **Listed Price**: $5/hour
- **After Stripe Fee**: ~$4.34-4.79/hour (depending on package)
- **Effective Margin**: ~87-96% (after Stripe fees)

### Recommended Pricing Adjustments

**Option 1: Absorb Fees** (Current)
- Keep prices as-is
- Accept lower margin on small purchases
- Better for customer experience

**Option 2: Pass Fees to Customer**
- Add 3% "processing fee" to prices
- Customer pays: $25.75 instead of $25.00
- Redline receives: ~$25.00 after fees

**Option 3: Minimum Purchase**
- Set minimum purchase (e.g., $10)
- Reduces impact of fixed $0.30 fee
- Better margin on small transactions

## Stripe Fee Comparison

### Stripe vs Competitors

| Provider | Online Fee | Fixed Fee | Best For |
|----------|-----------|-----------|----------|
| **Stripe** | 2.9% | $0.30 | Most businesses |
| PayPal | 2.9% | $0.30 | Similar to Stripe |
| Square | 2.9% | $0.30 | Similar to Stripe |
| Braintree | 2.9% | $0.30 | Similar to Stripe |
| Authorize.net | 2.9% | $0.30 | Enterprise |

**Note**: Most payment processors charge similar rates. Stripe is competitive.

## Reducing Stripe Fees

### 1. Volume Discounts
- **Stripe**: Offers custom pricing for high volume (>$1M/year)
- **Reduction**: Can negotiate lower rates
- **REDLINE**: Not applicable yet (low volume)

### 2. ACH/Bank Transfers
- **Fee**: 0.8% (capped at $5)
- **Limitation**: Takes 5-7 days to process
- **Use Case**: Large payments, B2B

### 3. Stripe Connect (Marketplace)
- **Fee**: Different structure for marketplaces
- **Use Case**: If REDLINE becomes a marketplace
- **Not Applicable**: Current single-vendor model

### 4. Optimize Package Sizes
- **Current**: Small packages have higher effective fees
- **Solution**: Encourage larger packages
- **Benefit**: Fixed fee spread over more hours

## Fee Tracking in REDLINE

### Current Implementation
- ✅ Payment amounts logged
- ✅ Stripe session IDs tracked
- ❌ Stripe fees not explicitly tracked
- ❌ Net revenue not calculated

### Recommended Addition
```python
# Add to payment_history table
'gross_amount': 45.00,
'stripe_fee': 1.61,
'net_amount': 43.39,
'fee_percentage': 3.58  # (1.61/45.00) × 100
```

## Summary

### Stripe Charges Per Dollar

**Standard Rate**: **2.9% + $0.30** per transaction

**Breakdown**:
- **2.9%** of transaction amount
- **$0.30** fixed fee per transaction
- **Total**: Both fees apply

**Example**: 
- Customer pays $100
- Stripe fee: ($100 × 0.029) + $0.30 = $3.20
- Redline receives: $100 - $3.20 = $96.80
- **Effective fee rate**: 3.2% (on $100 transaction)

**Note**: Effective percentage decreases as transaction size increases due to fixed fee component.

