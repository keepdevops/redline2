# Cost Tracking and Markup Strategy for REDLINE

## Overview

This guide helps you calculate infrastructure costs, determine appropriate markup, and ensure profitability for REDLINE deployment on Render with Cloudflare R2.

## Cost Components

### 1. Infrastructure Costs (Fixed Monthly)

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| **Render** | Starter | $7.00 |
| **Render** | Professional | $25.00 |
| **Cloudflare DNS/SSL** | Free | $0.00 |

**Total Infrastructure**: $7-25/month (depending on plan)

### 2. Storage Costs (Variable Monthly)

**Cloudflare R2:**
- First 10GB: **FREE**
- Additional: $0.015/GB/month
- Egress: **FREE** (unlimited)

**Cost Calculation:**
```
Storage Cost = max(0, (Total GB - 10) × $0.015)
```

**Examples:**
- 10GB: $0.00/month (free tier)
- 50GB: (50 - 10) × $0.015 = $0.60/month
- 100GB: (100 - 10) × $0.015 = $1.35/month
- 500GB: (500 - 10) × $0.015 = $7.35/month

### 3. API Costs (Optional)

**Free Tiers (Recommended):**
- Alpha Vantage: $0.00 (5 calls/min, 500/day)
- Finnhub: $0.00 (60 calls/min, 1000/day)
- Yahoo Finance: $0.00 (no API key needed)

**Paid Tiers (If Needed):**
- Alpha Vantage: $49.99/month (75 calls/min)
- Finnhub: $9.00/month (enhanced features)

**Recommendation**: Start with free tiers, upgrade only if needed.

### 4. Stripe Payment Processing Fees

**Per Transaction:**
- Percentage: 2.9% of transaction amount
- Fixed: $0.30 per transaction
- **Total**: (Amount × 0.029) + $0.30

**Examples:**
- $25 payment: $0.73 fee, net $24.27
- $45 payment: $1.61 fee, net $43.39
- $80 payment: $2.62 fee, net $77.38
- $180 payment: $5.52 fee, net $174.48

## Total Monthly Cost Calculation

### Scenario 1: Starter Plan, Low Usage

**Assumptions:**
- Render Starter: $7.00
- Storage: 10GB (free tier)
- API: Free tiers
- **Total**: $7.00/month

### Scenario 2: Starter Plan, Medium Usage

**Assumptions:**
- Render Starter: $7.00
- Storage: 50GB = $0.60
- API: Free tiers
- **Total**: $7.60/month

### Scenario 3: Professional Plan, High Usage

**Assumptions:**
- Render Professional: $25.00
- Storage: 200GB = $2.85
- API: Paid tiers = $58.99
- **Total**: $86.84/month

## Cost Per Hour Calculation

### Formula

```
Cost Per Hour = Total Monthly Costs / Hours Sold Per Month
```

### Examples

**Scenario A: Low Volume**
- Monthly costs: $7.00
- Hours sold: 10 hours/month
- **Cost per hour**: $7.00 / 10 = $0.70/hour

**Scenario B: Medium Volume**
- Monthly costs: $7.60
- Hours sold: 100 hours/month
- **Cost per hour**: $7.60 / 100 = $0.076/hour

**Scenario C: High Volume**
- Monthly costs: $86.84
- Hours sold: 1000 hours/month
- **Cost per hour**: $86.84 / 1000 = $0.087/hour

## Markup Strategy

### Target Profit Margins

| Margin | Description | Use Case |
|--------|-------------|----------|
| 50% | Minimum viable | Early stage, competitive pricing |
| 60% | Recommended | Balanced profit and competitiveness |
| 70% | High margin | Established product, premium pricing |
| 80% | Maximum | Enterprise, high-value features |

### Pricing Formula

```
Selling Price = Cost Per Hour / (1 - Target Margin)
```

**Example:**
- Cost per hour: $0.076
- Target margin: 60% (0.60)
- Selling price: $0.076 / (1 - 0.60) = $0.19/hour

**Rounded to market price**: $5.00/hour (common pricing)

### Current REDLINE Pricing

**Current Configuration:**
- `HOURS_PER_DOLLAR=0.2` (1 hour = $5, or 0.2 hours per dollar)
- **Price per hour**: $5.00

**Cost Analysis:**
- If cost per hour = $0.076
- Selling price = $5.00
- **Profit per hour**: $4.924
- **Margin**: 98.5% (very healthy!)

## Recommended Pricing Tiers

### Based on Cost Scenarios

| Scenario | Monthly Cost | Hours/Month | Cost/Hour | Recommended Price/Hour | Margin |
|----------|--------------|-------------|-----------|------------------------|--------|
| Low Volume | $7.00 | 10 | $0.70 | $5.00 | 86% |
| Medium Volume | $7.60 | 100 | $0.076 | $5.00 | 98.5% |
| High Volume | $86.84 | 1000 | $0.087 | $5.00 | 98.3% |

**Conclusion**: $5/hour provides excellent margins at all volume levels.

## Using the Cost Calculator

### Run Cost Calculator

```bash
# Basic usage (defaults)
python3 cost_calculator.py

# Custom scenario
python3 cost_calculator.py starter 50 200 0.60
# Arguments: [render_plan] [storage_gb] [hours_sold] [target_margin]

# With environment variables
export RENDER_PLAN=starter
export STORAGE_GB=50
export HOURS_SOLD=200
export TARGET_MARGIN=0.60
python3 cost_calculator.py
```

### Example Output

```
REDLINE Cost Analysis Report
Generated: 2025-01-15 10:30:00

========================================
MONTHLY COSTS
========================================
Infrastructure (Render starter):    $7.00
Storage (R2, 50GB):                 $0.60
API Services:                        $0.00
----------------------------------------
TOTAL MONTHLY COSTS:                $7.60

========================================
COST PER HOUR
========================================
Hours Sold/Month:                   200
Cost Per Hour:                       $0.0380

========================================
RECOMMENDED PRICING
========================================
Target Margin:                      60.0%
Recommended Price/Hour:              $5.00
Hours Per Dollar:                    0.2000
Profit Per Hour:                      $4.9620
Actual Margin:                        99.2%

========================================
ENVIRONMENT VARIABLE
========================================
HOURS_PER_DOLLAR=0.2000
```

## Markup Calculation Examples

### Example 1: Low Volume Startup

**Costs:**
- Infrastructure: $7.00
- Storage: $0.00 (free tier)
- **Total**: $7.00/month

**Sales:**
- 20 hours sold/month
- Cost per hour: $7.00 / 20 = $0.35/hour

**Pricing:**
- Target margin: 60%
- Selling price: $0.35 / (1 - 0.60) = $0.875/hour
- **Rounded**: $5.00/hour (market standard)
- **Actual margin**: 93%

### Example 2: Growing Business

**Costs:**
- Infrastructure: $7.00
- Storage: $1.50 (100GB)
- **Total**: $8.50/month

**Sales:**
- 500 hours sold/month
- Cost per hour: $8.50 / 500 = $0.017/hour

**Pricing:**
- Target margin: 60%
- Selling price: $0.017 / (1 - 0.60) = $0.0425/hour
- **Rounded**: $5.00/hour
- **Actual margin**: 99.7%

### Example 3: High Volume with Paid APIs

**Costs:**
- Infrastructure: $25.00 (Professional)
- Storage: $7.35 (500GB)
- APIs: $58.99 (paid tiers)
- **Total**: $91.34/month

**Sales:**
- 2000 hours sold/month
- Cost per hour: $91.34 / 2000 = $0.046/hour

**Pricing:**
- Target margin: 60%
- Selling price: $0.046 / (1 - 0.60) = $0.115/hour
- **Rounded**: $5.00/hour
- **Actual margin**: 99.1%

## Cost Monitoring

### Track Monthly Costs

1. **Render Dashboard**
   - View monthly usage
   - Check service costs
   - Monitor resource usage

2. **Cloudflare R2 Dashboard**
   - View storage usage
   - Check operation counts
   - Monitor costs

3. **Stripe Dashboard**
   - View transaction fees
   - Track revenue
   - Calculate net revenue

### Calculate Actual Costs

```python
# Use cost_calculator.py
from cost_calculator import CostCalculator

calc = CostCalculator()

# Get current month's costs
costs = calc.calculate_total_monthly_costs(
    render_plan='starter',
    storage_gb=50.0,
    use_alpha_vantage=False,
    use_finnhub=False
)

print(f"Total monthly cost: ${costs['total']:.2f}")
```

## Adjusting Pricing

### When to Increase Prices

1. **Costs Increase**
   - Infrastructure costs rise
   - Storage usage grows significantly
   - API costs increase

2. **Market Conditions**
   - Competitors raise prices
   - Value proposition increases
   - Demand exceeds supply

### When to Decrease Prices

1. **Costs Decrease**
   - Infrastructure costs drop
   - Volume discounts available
   - Efficiency improvements

2. **Market Conditions**
   - Competitive pressure
   - Market penetration strategy
   - Customer acquisition focus

## Profitability Analysis

### Break-Even Calculation

```
Break-Even Hours = Monthly Costs / Price Per Hour
```

**Example:**
- Monthly costs: $7.60
- Price per hour: $5.00
- **Break-even**: $7.60 / $5.00 = 1.52 hours/month

**Conclusion**: Very low break-even point!

### Profit Projections

| Hours Sold/Month | Revenue | Costs | Profit | Margin |
|------------------|---------|-------|--------|--------|
| 10 | $50.00 | $7.00 | $43.00 | 86% |
| 100 | $500.00 | $7.60 | $492.40 | 98.5% |
| 500 | $2,500.00 | $8.50 | $2,491.50 | 99.7% |
| 1000 | $5,000.00 | $10.00 | $4,990.00 | 99.8% |

## Recommended Markup Strategy

### Current Pricing Analysis

**Current**: $5.00/hour (`HOURS_PER_DOLLAR=0.2`)

**Cost at 100 hours/month**: ~$0.076/hour
**Margin**: 98.5%

**Verdict**: ✅ **Excellent margin** - pricing is very profitable

### Recommendations

1. **Keep Current Pricing** ($5/hour)
   - Provides excellent margins
   - Competitive with market
   - Room for cost increases

2. **Monitor Costs Monthly**
   - Track actual infrastructure costs
   - Monitor storage growth
   - Watch API usage

3. **Adjust if Needed**
   - If costs exceed $0.50/hour, consider price increase
   - If margin drops below 80%, review pricing
   - Recalculate quarterly

## Cost Tracking Checklist

- [ ] Calculate monthly infrastructure costs
- [ ] Track storage usage and costs
- [ ] Monitor API usage (if using paid tiers)
- [ ] Calculate cost per hour delivered
- [ ] Verify markup is adequate (target: 60%+)
- [ ] Review pricing quarterly
- [ ] Adjust if costs increase significantly

## Quick Reference

### Cost Calculator Usage

```bash
# Generate cost report
python3 cost_calculator.py starter 50 200 0.60

# Output includes:
# - Monthly costs breakdown
# - Cost per hour
# - Recommended pricing
# - HOURS_PER_DOLLAR value
```

### Update Pricing

If costs change significantly:

1. Run cost calculator with new values
2. Review recommended pricing
3. Update `HOURS_PER_DOLLAR` in Render environment
4. Update `HOURS_PER_DOLLAR` in `env.template`
5. Redeploy service

---

**Current Pricing**: $5.00/hour (HOURS_PER_DOLLAR=0.2)  
**Recommended Margin**: 60-70%  
**Current Margin**: ~98% (excellent!)

