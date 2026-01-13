#!/usr/bin/env python3
"""
Helper script to find the correct Stripe Price ID for metered billing subscriptions.
This script will:
1. Look up the product ID you have configured
2. List all prices associated with that product
3. Identify which prices are suitable for metered billing subscriptions
"""

import os
import sys

try:
    import stripe
except ImportError:
    print("❌ Error: stripe package not installed")
    print("   Install with: pip install stripe")
    sys.exit(1)

def find_price_id():
    """Find the correct Price ID for metered billing"""
    
    # Get configuration from environment
    stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
    product_id = os.environ.get('STRIPE_PRICE_ID_METERED', '').strip()
    
    # If it's already a price ID, we're done
    if product_id.startswith('price_'):
        print(f"✅ STRIPE_PRICE_ID_METERED is already a Price ID: {product_id}")
        return product_id
    
    if not stripe_secret_key:
        print("❌ Error: STRIPE_SECRET_KEY not found in environment")
        print("   Please set it in your .env file or export it")
        sys.exit(1)
    
    if not product_id or not product_id.startswith('prod_'):
        print("❌ Error: STRIPE_PRICE_ID_METERED is not set or is not a Product ID")
        print(f"   Current value: {product_id}")
        print("   Expected format: prod_xxxxxxxxxxxxx")
        sys.exit(1)
    
    # Set up Stripe API
    stripe.api_key = stripe_secret_key
    
    print(f"🔍 Looking up Product ID: {product_id}")
    print("=" * 60)
    
    try:
        # Get the product
        product = stripe.Product.retrieve(product_id)
        print(f"📦 Product Name: {product.name}")
        print(f"   Product ID: {product.id}")
        print(f"   Description: {product.description or '(no description)'}")
        print()
        
        # List all prices for this product
        print("💰 Available Prices for this Product:")
        print("-" * 60)
        
        prices = stripe.Price.list(product=product_id, limit=100)
        
        if not prices.data:
            print("   ⚠️  No prices found for this product!")
            print()
            print("   To create a price:")
            print("   1. Go to Stripe Dashboard > Products")
            print(f"   2. Click on '{product.name}'")
            print("   3. Click 'Add another price'")
            print("   4. Set billing to 'Metered billing'")
            print("   5. Configure your usage-based pricing")
            sys.exit(1)
        
        metered_prices = []
        recurring_prices = []
        one_time_prices = []
        
        for price in prices.data:
            price_info = {
                'id': price.id,
                'nickname': price.nickname or '(no nickname)',
                'type': price.type,  # 'one_time' or 'recurring'
                'billing_scheme': getattr(price, 'billing_scheme', None),
                'unit_amount': price.unit_amount,
                'currency': price.currency.upper(),
                'recurring': getattr(price, 'recurring', None)
            }
            
            if price.type == 'recurring':
                if price.billing_scheme == 'per_unit':
                    # Check if it's metered
                    if price.recurring.usage_type == 'metered':
                        metered_prices.append(price_info)
                    else:
                        recurring_prices.append(price_info)
                else:
                    recurring_prices.append(price_info)
            else:
                one_time_prices.append(price_info)
        
        # Display metered prices (most relevant for subscriptions)
        if metered_prices:
            print("\n✅ METERED BILLING PRICES (Recommended for subscriptions):")
            print("=" * 60)
            for idx, price in enumerate(metered_prices, 1):
                recurring = price['recurring']
                print(f"\n   {idx}. Price ID: {price['id']}")
                print(f"      Nickname: {price['nickname']}")
                print(f"      Type: {price['type']} - {price['billing_scheme']}")
                print(f"      Billing: {recurring['interval']} ({recurring['interval_count']} {recurring['interval']}(s))")
                print(f"      Usage Type: {recurring['usage_type']}")
                if recurring.get('aggregate_usage'):
                    print(f"      Aggregate: {recurring['aggregate_usage']}")
                print(f"      Currency: {price['currency']}")
                print(f"      ✅ USE THIS: STRIPE_PRICE_ID_METERED={price['id']}")
        
        # Display other recurring prices
        if recurring_prices:
            print("\n⚠️  RECURRING PRICES (Not metered - fixed monthly/yearly):")
            print("=" * 60)
            for idx, price in enumerate(recurring_prices, 1):
                recurring = price['recurring']
                amount = price['unit_amount'] / 100 if price['unit_amount'] else 0
                print(f"\n   {idx}. Price ID: {price['id']}")
                print(f"      Nickname: {price['nickname']}")
                print(f"      Amount: ${amount:.2f} {price['currency']}")
                print(f"      Billing: {recurring['interval']} ({recurring['interval_count']} {recurring['interval']}(s))")
                print(f"      Usage Type: {recurring['usage_type']}")
        
        # Display one-time prices
        if one_time_prices:
            print("\n📌 ONE-TIME PRICES (Not for subscriptions):")
            print("=" * 60)
            for idx, price in enumerate(one_time_prices, 1):
                amount = price['unit_amount'] / 100 if price['unit_amount'] else 0
                print(f"\n   {idx}. Price ID: {price['id']}")
                print(f"      Nickname: {price['nickname']}")
                print(f"      Amount: ${amount:.2f} {price['currency']}")
        
        # Recommendations
        print("\n" + "=" * 60)
        print("📋 RECOMMENDATIONS:")
        print("=" * 60)
        
        if metered_prices:
            recommended = metered_prices[0]
            print(f"\n✅ Use this Price ID for metered billing subscriptions:")
            print(f"   STRIPE_PRICE_ID_METERED={recommended['id']}")
            print(f"\n   Update your .env file:")
            print(f"   STRIPE_PRICE_ID_METERED={recommended['id']}")
        else:
            print("\n⚠️  No metered billing prices found!")
            print("\n   To create a metered billing price:")
            print("   1. Go to Stripe Dashboard: https://dashboard.stripe.com/products")
            print(f"   2. Click on product: {product.name}")
            print("   3. Click 'Add another price'")
            print("   4. Set:")
            print("      - Billing: Recurring")
            print("      - Price: $0.00 (or your base price)")
            print("      - Billing scheme: Per unit")
            print("      - Usage type: Metered")
            print("      - Metered aggregation: Sum (or your preference)")
            print("   5. Save and copy the Price ID (starts with 'price_')")
        
        return metered_prices[0]['id'] if metered_prices else None
        
    except stripe.error.InvalidRequestError as e:
        print(f"❌ Stripe API Error: {str(e)}")
        if 'No such product' in str(e):
            print(f"\n   The Product ID '{product_id}' doesn't exist in your Stripe account.")
            print("   Please check your Stripe Dashboard to find the correct Product ID.")
        sys.exit(1)
    except stripe.error.AuthenticationError as e:
        print(f"❌ Stripe Authentication Error: {str(e)}")
        print("   Please check your STRIPE_SECRET_KEY in your .env file")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    price_id = find_price_id()
    if price_id:
        print(f"\n✅ Success! Use Price ID: {price_id}")
        sys.exit(0)
    else:
        sys.exit(1)
