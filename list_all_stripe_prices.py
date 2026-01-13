#!/usr/bin/env python3
"""
List all Stripe Products and Prices to help find the correct Price ID for metered billing.
"""

import os
import sys

try:
    import stripe
except ImportError:
    print("❌ Error: stripe package not installed")
    print("   Install with: pip install stripe")
    sys.exit(1)

def list_all_products_and_prices():
    """List all products and their prices"""
    
    stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
    
    if not stripe_secret_key:
        print("❌ Error: STRIPE_SECRET_KEY not found in environment")
        sys.exit(1)
    
    stripe.api_key = stripe_secret_key
    
    print("🔍 Listing all Products and Prices in your Stripe account...")
    print("=" * 80)
    
    try:
        # List all products
        products = stripe.Product.list(limit=100)
        
        if not products.data:
            print("⚠️  No products found in your Stripe account!")
            print("\n   To create a product with metered billing:")
            print("   1. Go to: https://dashboard.stripe.com/products")
            print("   2. Click 'Add product'")
            print("   3. Set up a metered billing subscription price")
            sys.exit(1)
        
        print(f"\n📦 Found {len(products.data)} product(s):\n")
        
        all_metered_prices = []
        
        for product in products.data:
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📦 Product: {product.name}")
            print(f"   Product ID: {product.id}")
            print(f"   Description: {product.description or '(no description)'}")
            print(f"   Active: {product.active}")
            print()
            
            # Get all prices for this product
            prices = stripe.Price.list(product=product.id, limit=100, active=True)
            
            if not prices.data:
                print("   ⚠️  No active prices found for this product\n")
                continue
            
            print(f"   💰 Prices ({len(prices.data)}):")
            
            for price in prices.data:
                print(f"\n      • Price ID: {price.id}")
                print(f"        Nickname: {price.nickname or '(no nickname)'}")
                print(f"        Type: {price.type}")
                
                if price.type == 'recurring':
                    recurring = price.recurring
                    print(f"        Billing: {recurring['interval']} ({recurring['interval_count']} {recurring['interval']}(s))")
                    print(f"        Usage Type: {recurring['usage_type']}")
                    
                    if price.billing_scheme == 'per_unit':
                        if price.unit_amount:
                            amount = price.unit_amount / 100
                            print(f"        Base Amount: ${amount:.2f} {price.currency.upper()}")
                        else:
                            print(f"        Base Amount: $0.00 {price.currency.upper()}")
                        
                        if recurring['usage_type'] == 'metered':
                            print(f"        ✅ METERED BILLING - Suitable for subscriptions!")
                            all_metered_prices.append({
                                'product_name': product.name,
                                'product_id': product.id,
                                'price_id': price.id,
                                'nickname': price.nickname,
                                'currency': price.currency.upper(),
                                'interval': recurring['interval']
                            })
                    else:
                        print(f"        Billing Scheme: {price.billing_scheme}")
                        if price.unit_amount:
                            amount = price.unit_amount / 100
                            print(f"        Amount: ${amount:.2f} {price.currency.upper()}")
                else:
                    if price.unit_amount:
                        amount = price.unit_amount / 100
                        print(f"        Amount: ${amount:.2f} {price.currency.upper()}")
                    print(f"        ⚠️  One-time payment (not for subscriptions)")
            
            print()
        
        # Summary of metered prices
        print("=" * 80)
        print("📋 SUMMARY - METERED BILLING PRICES:")
        print("=" * 80)
        
        if all_metered_prices:
            print(f"\n✅ Found {len(all_metered_prices)} metered billing price(s):\n")
            for idx, price_info in enumerate(all_metered_prices, 1):
                print(f"   {idx}. {price_info['product_name']}")
                print(f"      Price ID: {price_info['price_id']}")
                print(f"      Nickname: {price_info['nickname'] or '(no nickname)'}")
                print(f"      Currency: {price_info['currency']}")
                print(f"      Interval: {price_info['interval']}")
                print(f"      ✅ USE THIS: STRIPE_PRICE_ID_METERED={price_info['price_id']}")
                print()
            
            # Recommend the first one
            recommended = all_metered_prices[0]
            print("\n" + "=" * 80)
            print("✅ RECOMMENDED CONFIGURATION:")
            print("=" * 80)
            print(f"\n   Add this to your .env file:")
            print(f"   STRIPE_PRICE_ID_METERED={recommended['price_id']}")
            print()
            print(f"   Or update the existing line:")
            print(f"   STRIPE_PRICE_ID_METERED={recommended['price_id']}")
        else:
            print("\n⚠️  No metered billing prices found!")
            print("\n   To create a metered billing price:")
            print("   1. Go to: https://dashboard.stripe.com/products")
            print("   2. Create a new product or select an existing one")
            print("   3. Click 'Add another price'")
            print("   4. Configure:")
            print("      - Billing: Recurring")
            print("      - Price: $0.00 (or your base subscription fee)")
            print("      - Billing scheme: Per unit")
            print("      - Usage type: Metered")
            print("      - Metered aggregation: Sum")
            print("   5. Save and copy the Price ID (starts with 'price_')")
        
    except stripe.error.AuthenticationError as e:
        print(f"❌ Stripe Authentication Error: {str(e)}")
        print("   Please check your STRIPE_SECRET_KEY in your .env file")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    list_all_products_and_prices()
