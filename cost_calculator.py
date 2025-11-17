#!/usr/bin/env python3
"""
REDLINE Cost Calculator
Calculates infrastructure costs and recommends pricing with markup
"""

import os
from typing import Dict, Optional
from datetime import datetime

class CostCalculator:
    """Calculate costs and recommend pricing for REDLINE deployment"""
    
    # Infrastructure Costs (Monthly)
    RENDER_STARTER = 7.00  # $7/month
    RENDER_PROFESSIONAL = 25.00  # $25/month
    
    # Storage Costs (Monthly)
    R2_STORAGE_PER_GB = 0.015  # $0.015/GB/month
    R2_FREE_TIER_GB = 10  # First 10GB free
    
    # API Costs (Monthly - Free Tiers)
    ALPHA_VANTAGE_FREE = 0.00  # Free tier: 5 calls/min, 500/day
    ALPHA_VANTAGE_PAID = 49.99  # Paid: 75 calls/min
    FINNHUB_FREE = 0.00  # Free tier: 60 calls/min, 1000/day
    FINNHUB_PAID = 9.00  # Paid: 60 calls/min, more features
    
    # Stripe Fees (Per Transaction)
    STRIPE_PERCENTAGE = 0.029  # 2.9%
    STRIPE_FIXED = 0.30  # $0.30
    
    def __init__(self):
        self.monthly_costs = {}
        self.recommended_pricing = {}
    
    def calculate_infrastructure_costs(self, render_plan: str = 'starter') -> float:
        """Calculate monthly infrastructure costs"""
        if render_plan == 'starter':
            return self.RENDER_STARTER
        elif render_plan == 'professional':
            return self.RENDER_PROFESSIONAL
        else:
            return self.RENDER_STARTER
    
    def calculate_storage_costs(self, storage_gb: float) -> float:
        """Calculate monthly R2 storage costs"""
        if storage_gb <= self.R2_FREE_TIER_GB:
            return 0.00
        
        billable_gb = storage_gb - self.R2_FREE_TIER_GB
        return billable_gb * self.R2_STORAGE_PER_GB
    
    def calculate_api_costs(self, use_alpha_vantage: bool = False,
                          use_finnhub: bool = False,
                          use_paid_tiers: bool = False) -> float:
        """Calculate monthly API costs"""
        cost = 0.00
        
        if use_alpha_vantage:
            if use_paid_tiers:
                cost += self.ALPHA_VANTAGE_PAID
            else:
                cost += self.ALPHA_VANTAGE_FREE
        
        if use_finnhub:
            if use_paid_tiers:
                cost += self.FINNHUB_PAID
            else:
                cost += self.FINNHUB_FREE
        
        return cost
    
    def calculate_stripe_fee(self, transaction_amount: float) -> float:
        """Calculate Stripe fee for a transaction"""
        return (transaction_amount * self.STRIPE_PERCENTAGE) + self.STRIPE_FIXED
    
    def calculate_net_revenue(self, transaction_amount: float) -> float:
        """Calculate net revenue after Stripe fees"""
        return transaction_amount - self.calculate_stripe_fee(transaction_amount)
    
    def calculate_total_monthly_costs(self, render_plan: str = 'starter',
                                     storage_gb: float = 10.0,
                                     use_alpha_vantage: bool = False,
                                     use_finnhub: bool = False,
                                     use_paid_api_tiers: bool = False) -> Dict:
        """Calculate total monthly costs"""
        infrastructure = self.calculate_infrastructure_costs(render_plan)
        storage = self.calculate_storage_costs(storage_gb)
        api = self.calculate_api_costs(use_alpha_vantage, use_finnhub, use_paid_api_tiers)
        total = infrastructure + storage + api
        return {
            'infrastructure': infrastructure, 'storage': storage, 'api': api, 'total': total,
            'breakdown': {'render': infrastructure, 'r2_storage': storage, 'api_services': api}
        }
    
    def calculate_cost_per_hour(self, 
                                monthly_costs: float,
                                hours_sold_per_month: float) -> float:
        """Calculate cost per hour delivered"""
        if hours_sold_per_month == 0:
            return 0.00
        return monthly_costs / hours_sold_per_month
    
    def recommend_pricing(self, monthly_costs: float, target_margin: float = 0.60,
                         hours_sold_per_month: float = 100.0) -> Dict:
        """Recommend pricing based on costs and target margin"""
        cost_per_hour = self.calculate_cost_per_hour(monthly_costs, hours_sold_per_month)
        price_per_hour = cost_per_hour / (1 - target_margin) if target_margin < 1.0 else cost_per_hour * 2
        if price_per_hour < 1.00:
            price_per_hour = 1.00
        elif price_per_hour < 5.00:
            price_per_hour = round(price_per_hour, 2)
        else:
            price_per_hour = round(price_per_hour / 5) * 5
        hours_per_dollar = 1.0 / price_per_hour
        profit_per_hour = price_per_hour - cost_per_hour
        actual_margin = (profit_per_hour / price_per_hour * 100) if price_per_hour > 0 else 0
        return {
            'cost_per_hour': round(cost_per_hour, 4), 'recommended_price_per_hour': price_per_hour,
            'hours_per_dollar': round(hours_per_dollar, 4), 'profit_per_hour': round(profit_per_hour, 4),
            'actual_margin': round(actual_margin, 2), 'target_margin': round(target_margin * 100, 2)
        }
    
    def generate_report(self,
                       render_plan: str = 'starter',
                       storage_gb: float = 10.0,
                       use_alpha_vantage: bool = False,
                       use_finnhub: bool = False,
                       use_paid_api_tiers: bool = False,
                       hours_sold_per_month: float = 100.0,
                       target_margin: float = 0.60) -> str:
        """Generate cost analysis report"""
        costs = self.calculate_total_monthly_costs(
            render_plan, storage_gb, use_alpha_vantage, 
            use_finnhub, use_paid_api_tiers
        )
        pricing = self.recommend_pricing(costs['total'], target_margin, hours_sold_per_month)
        
        report = f"""REDLINE Cost Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

MONTHLY COSTS
Infrastructure (Render {render_plan}):    ${costs['infrastructure']:.2f}
Storage (R2, {storage_gb}GB):            ${costs['storage']:.2f}
API Services:                             ${costs['api']:.2f}
TOTAL MONTHLY COSTS:                     ${costs['total']:.2f}

COST PER HOUR
Hours Sold/Month:                        {hours_sold_per_month:.0f}
Cost Per Hour:                           ${pricing['cost_per_hour']:.4f}

RECOMMENDED PRICING
Target Margin:                           {pricing['target_margin']:.1f}%
Recommended Price/Hour:                  ${pricing['recommended_price_per_hour']:.2f}
Hours Per Dollar:                         {pricing['hours_per_dollar']:.4f}
Profit Per Hour:                          ${pricing['profit_per_hour']:.4f}
Actual Margin:                            {pricing['actual_margin']:.1f}%

ENVIRONMENT VARIABLE
HOURS_PER_DOLLAR={pricing['hours_per_dollar']:.4f}

STRIPE FEE IMPACT
"""
        for amount in [25.00, 45.00, 80.00, 180.00]:
            fee = self.calculate_stripe_fee(amount)
            net = self.calculate_net_revenue(amount)
            report += f"Payment ${amount:.2f}: Fee ${fee:.2f}, Net ${net:.2f}\n"
        return report

def main():
    """Main function for command-line usage"""
    import sys
    calculator = CostCalculator()
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("""REDLINE Cost Calculator
Usage: python cost_calculator.py [render_plan] [storage_gb] [hours_sold] [target_margin]
Examples: python cost_calculator.py starter 10 100 0.60""")
        return
    
    render_plan = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('RENDER_PLAN', 'starter')
    storage_gb = float(sys.argv[2]) if len(sys.argv) > 2 else float(os.environ.get('STORAGE_GB', '10.0'))
    hours_sold = float(sys.argv[3]) if len(sys.argv) > 3 else float(os.environ.get('HOURS_SOLD', '100.0'))
    target_margin = float(sys.argv[4]) if len(sys.argv) > 4 else float(os.environ.get('TARGET_MARGIN', '0.60'))
    
    print(calculator.generate_report(render_plan=render_plan, storage_gb=storage_gb,
                                     hours_sold_per_month=hours_sold, target_margin=target_margin))

if __name__ == '__main__':
    main()

