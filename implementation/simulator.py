"""
UAE Promo Pulse - Simulator
Computes KPIs and runs what-if discount simulations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class PromoSimulator:
    def __init__(self, products_df, stores_df, sales_df, inventory_df):
        """Initialize simulator with cleaned data"""
        self.products = products_df.copy()
        self.stores = stores_df.copy()
        self.sales = sales_df.copy()
        self.inventory = inventory_df.copy()
        
        # Ensure order_time is datetime
        if 'order_time' in self.sales.columns:
            self.sales['order_time'] = pd.to_datetime(self.sales['order_time'], errors='coerce')
        
        # Merge sales with products for cost calculations
        self.sales_enriched = self.sales.merge(
            self.products[['product_id', 'category', 'brand', 'unit_cost_aed']], 
            on='product_id', 
            how='left'
        )
        
        # Merge with stores for geography/channel
        self.sales_enriched = self.sales_enriched.merge(
            self.stores[['store_id', 'city', 'channel', 'fulfillment_type']], 
            on='store_id', 
            how='left'
        )
    
    def compute_kpis(self, df=None):
        """Compute all 12+ KPIs"""
        if df is None:
            df = self.sales_enriched
        
        # Filter to Paid transactions only for revenue
        paid_df = df[df['payment_status'] == 'Paid'].copy()
        
        # 1. Gross Revenue (Paid only)
        paid_df['revenue'] = paid_df['qty'] * paid_df['selling_price_aed']
        gross_revenue = paid_df['revenue'].sum()
        
        # 2. Refund Amount
        refund_df = df[df['payment_status'] == 'Refunded']
        refund_df['refund_amt'] = refund_df['qty'] * refund_df['selling_price_aed']
        refund_amount = refund_df['refund_amt'].sum()
        
        # 3. Net Revenue
        net_revenue = gross_revenue - refund_amount
        
        # 4. COGS (Cost of Goods Sold)
        paid_df['cogs'] = paid_df['qty'] * paid_df['unit_cost_aed']
        cogs = paid_df['cogs'].sum()
        
        # 5. Gross Margin (AED)
        gross_margin = net_revenue - cogs
        
        # 6. Gross Margin %
        gross_margin_pct = (gross_margin / net_revenue * 100) if net_revenue > 0 else 0
        
        # 7. Average Discount %
        avg_discount = df['discount_pct'].mean()
        
        # 8. Return Rate %
        return_rate = (len(df[df['return_flag'] == 'Y']) / len(df) * 100) if len(df) > 0 else 0
        
        # 9. Payment Failure Rate %
        payment_failure_rate = (len(df[df['payment_status'] == 'Failed']) / len(df) * 100) if len(df) > 0 else 0
        
        kpis = {
            'gross_revenue': gross_revenue,
            'refund_amount': refund_amount,
            'net_revenue': net_revenue,
            'cogs': cogs,
            'gross_margin_aed': gross_margin,
            'gross_margin_pct': gross_margin_pct,
            'avg_discount_pct': avg_discount,
            'return_rate_pct': return_rate,
            'payment_failure_rate_pct': payment_failure_rate
        }
        
        return kpis
    
    def calculate_baseline_demand(self, city=None, channel=None, category=None):
        """Calculate baseline daily demand per product-store from last 30 days"""
        # Filter sales to last 30 days
        self.sales_enriched['order_time'] = pd.to_datetime(self.sales_enriched['order_time'])
        max_date = self.sales_enriched['order_time'].max()
        start_date = max_date - timedelta(days=30)
        
        recent_sales = self.sales_enriched[
            (self.sales_enriched['order_time'] >= start_date) & 
            (self.sales_enriched['payment_status'] == 'Paid')
        ].copy()
        
        # Apply filters
        if city and city != 'All':
            recent_sales = recent_sales[recent_sales['city'] == city]
        if channel and channel != 'All':
            recent_sales = recent_sales[recent_sales['channel'] == channel]
        if category and category != 'All':
            recent_sales = recent_sales[recent_sales['category'] == category]
        
        # Calculate daily demand per product-store
        baseline = recent_sales.groupby(['product_id', 'store_id']).agg({
            'qty': 'sum'
        }).reset_index()
        
        # Convert to daily average (30 days)
        baseline['daily_demand'] = baseline['qty'] / 30
        baseline = baseline[['product_id', 'store_id', 'daily_demand']]
        
        return baseline
    
    def apply_uplift_logic(self, baseline_df, discount_pct, channel=None, category=None):
        """
        Apply rule-based demand uplift based on discount and product/channel characteristics
        
        Assumptions:
        - Base uplift: discount_pct / 10 (e.g., 20% discount = 2x uplift)
        - Channel multiplier: Marketplace (1.3x), App (1.2x), Web (1.0x)
        - Category multiplier: Electronics/Fashion (1.2x), Others (1.0x)
        """
        df = baseline_df.copy()
        
        # Merge with products to get category
        df = df.merge(
            self.products[['product_id', 'category']], 
            on='product_id', 
            how='left'
        )
        
        # Merge with stores to get channel
        df = df.merge(
            self.stores[['store_id', 'channel']], 
            on='store_id', 
            how='left'
        )
        
        # Base uplift factor
        base_uplift = 1 + (discount_pct / 10)
        
        # Channel multiplier
        channel_mult = df['channel'].map({
            'Marketplace': 1.3,
            'App': 1.2,
            'Web': 1.0
        }).fillna(1.0)
        
        # Category multiplier
        category_mult = df['category'].map({
            'Electronics': 1.2,
            'Fashion': 1.2,
            'Beauty': 1.1,
            'Sports': 1.1,
        }).fillna(1.0)
        
        # Calculate simulated demand
        df['uplift_factor'] = base_uplift * channel_mult * category_mult
        df['simulated_daily_demand'] = df['daily_demand'] * df['uplift_factor']
        
        return df
    
    def simulate_promo(self, city='All', channel='All', category='All', 
                      discount_pct=20, promo_budget_aed=100000, 
                      margin_floor_pct=10, simulation_days=14):
        """
        Run what-if simulation with constraints
        
        Returns:
        - Simulation results DataFrame
        - Constraint violations dictionary
        - Simulation KPIs
        """
        # 1. Calculate baseline demand
        baseline = self.calculate_baseline_demand(city, channel, category)
        
        # 2. Apply uplift logic
        simulated = self.apply_uplift_logic(baseline, discount_pct, channel, category)
        
        # 3. Calculate simulated qty for the period
        simulated['simulated_qty'] = simulated['simulated_daily_demand'] * simulation_days
        simulated['simulated_qty'] = simulated['simulated_qty'].round().astype(int)
        
        # 4. Merge with products for pricing
        simulated = simulated.merge(
            self.products[['product_id', 'base_price_aed', 'unit_cost_aed']], 
            on='product_id', 
            how='left'
        )
        
        # 5. Calculate financial metrics
        simulated['discounted_price'] = simulated['base_price_aed'] * (1 - discount_pct / 100)
        simulated['simulated_revenue'] = simulated['simulated_qty'] * simulated['discounted_price']
        simulated['simulated_cogs'] = simulated['simulated_qty'] * simulated['unit_cost_aed']
        simulated['simulated_margin'] = simulated['simulated_revenue'] - simulated['simulated_cogs']
        simulated['margin_pct'] = (simulated['simulated_margin'] / simulated['simulated_revenue'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        
        # 6. Calculate promo spend (discount amount)
        simulated['promo_spend'] = simulated['simulated_qty'] * simulated['base_price_aed'] * (discount_pct / 100)
        
        # 7. Get latest inventory
        latest_inventory = self.inventory.sort_values('snapshot_date').groupby(
            ['product_id', 'store_id']
        ).last().reset_index()[['product_id', 'store_id', 'stock_on_hand']]
        
        simulated = simulated.merge(
            latest_inventory, 
            on=['product_id', 'store_id'], 
            how='left'
        )
        simulated['stock_on_hand'] = simulated['stock_on_hand'].fillna(0)
        
        # 8. Check stockout risk
        simulated['stockout_risk'] = simulated['simulated_qty'] > simulated['stock_on_hand']
        simulated['stock_shortfall'] = (simulated['simulated_qty'] - simulated['stock_on_hand']).clip(lower=0)
        
        # 9. Calculate overall metrics
        total_promo_spend = simulated['promo_spend'].sum()
        total_revenue = simulated['simulated_revenue'].sum()
        total_margin = simulated['simulated_margin'].sum()
        overall_margin_pct = (total_margin / total_revenue * 100) if total_revenue > 0 else 0
        profit_proxy = total_margin  # Simplified profit
        
        # 10. Check constraints
        violations = {
            'budget_exceeded': total_promo_spend > promo_budget_aed,
            'margin_below_floor': overall_margin_pct < margin_floor_pct,
            'stockouts_exist': simulated['stockout_risk'].any(),
            'budget_utilization_pct': (total_promo_spend / promo_budget_aed * 100) if promo_budget_aed > 0 else 0,
            'margin_gap': margin_floor_pct - overall_margin_pct if overall_margin_pct < margin_floor_pct else 0,
            'stockout_risk_pct': (simulated['stockout_risk'].sum() / len(simulated) * 100) if len(simulated) > 0 else 0
        }
        
        # 11. Identify top violators
        violations['top_budget_contributors'] = simulated.nlargest(10, 'promo_spend')[
            ['product_id', 'store_id', 'promo_spend']
        ].to_dict('records')
        
        violations['top_margin_violators'] = simulated[simulated['margin_pct'] < margin_floor_pct].nlargest(10, 'simulated_revenue')[
            ['product_id', 'store_id', 'margin_pct', 'simulated_revenue']
        ].to_dict('records')
        
        violations['top_stockout_risks'] = simulated[simulated['stockout_risk']].nlargest(10, 'stock_shortfall')[
            ['product_id', 'store_id', 'simulated_qty', 'stock_on_hand', 'stock_shortfall']
        ].to_dict('records')
        
        # 12. Simulation KPIs
        sim_kpis = {
            'promo_spend': total_promo_spend,
            'simulated_revenue': total_revenue,
            'simulated_margin': total_margin,
            'simulated_margin_pct': overall_margin_pct,
            'profit_proxy': profit_proxy,
            'budget_utilization_pct': violations['budget_utilization_pct'],
            'stockout_risk_pct': violations['stockout_risk_pct'],
            'high_risk_skus': simulated['stockout_risk'].sum()
        }
        
        return simulated, violations, sim_kpis
    
    def get_time_series_data(self, freq='D'):
        """Get daily/weekly time series for trend charts"""
        df = self.sales_enriched[self.sales_enriched['payment_status'] == 'Paid'].copy()
        df['order_time'] = pd.to_datetime(df['order_time'])
        df['revenue'] = df['qty'] * df['selling_price_aed']
        df['cogs'] = df['qty'] * df['unit_cost_aed']
        df['margin'] = df['revenue'] - df['cogs']
        
        if freq == 'D':
            ts = df.set_index('order_time').resample('D').agg({
                'revenue': 'sum',
                'margin': 'sum',
                'qty': 'sum'
            }).reset_index()
        else:  # Weekly
            ts = df.set_index('order_time').resample('W').agg({
                'revenue': 'sum',
                'margin': 'sum',
                'qty': 'sum'
            }).reset_index()
        
        ts['margin_pct'] = (ts['margin'] / ts['revenue'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        
        return ts
    
    def get_city_channel_breakdown(self):
        """Get revenue breakdown by city and channel"""
        df = self.sales_enriched[self.sales_enriched['payment_status'] == 'Paid'].copy()
        df['revenue'] = df['qty'] * df['selling_price_aed']
        
        breakdown = df.groupby(['city', 'channel']).agg({
            'revenue': 'sum',
            'qty': 'sum'
        }).reset_index()
        
        return breakdown
    
    def get_category_margin(self):
        """Get margin % by category"""
        df = self.sales_enriched[self.sales_enriched['payment_status'] == 'Paid'].copy()
        df['revenue'] = df['qty'] * df['selling_price_aed']
        df['cogs'] = df['qty'] * df['unit_cost_aed']
        df['margin'] = df['revenue'] - df['cogs']
        
        cat_margin = df.groupby('category').agg({
            'revenue': 'sum',
            'margin': 'sum'
        }).reset_index()
        
        cat_margin['margin_pct'] = (cat_margin['margin'] / cat_margin['revenue'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        
        return cat_margin

def main():
    """Test the simulator"""
    print("Loading cleaned datasets...")
    
    try:
        products = pd.read_csv('products_clean.csv')
        stores = pd.read_csv('stores_clean.csv')
        sales = pd.read_csv('sales_clean.csv')
        inventory = pd.read_csv('inventory_clean.csv')
        
        print("Initializing simulator...")
        sim = PromoSimulator(products, stores, sales, inventory)
        
        print("\nComputing historical KPIs...")
        kpis = sim.compute_kpis()
        
        print("\nHistorical KPIs:")
        print(f"  Gross Revenue: {kpis['gross_revenue']:,.2f} AED")
        print(f"  Net Revenue: {kpis['net_revenue']:,.2f} AED")
        print(f"  Gross Margin: {kpis['gross_margin_aed']:,.2f} AED ({kpis['gross_margin_pct']:.2f}%)")
        print(f"  Avg Discount: {kpis['avg_discount_pct']:.2f}%")
        print(f"  Return Rate: {kpis['return_rate_pct']:.2f}%")
        
        print("\nRunning simulation...")
        simulated, violations, sim_kpis = sim.simulate_promo(
            city='All',
            channel='All',
            category='Electronics',
            discount_pct=25,
            promo_budget_aed=50000,
            margin_floor_pct=15,
            simulation_days=14
        )
        
        print("\nSimulation Results:")
        print(f"  Promo Spend: {sim_kpis['promo_spend']:,.2f} AED")
        print(f"  Budget Utilization: {sim_kpis['budget_utilization_pct']:.2f}%")
        print(f"  Simulated Revenue: {sim_kpis['simulated_revenue']:,.2f} AED")
        print(f"  Simulated Margin: {sim_kpis['simulated_margin_pct']:.2f}%")
        print(f"  Stockout Risk: {sim_kpis['stockout_risk_pct']:.2f}%")
        
        print("\nConstraint Violations:")
        print(f"  Budget Exceeded: {violations['budget_exceeded']}")
        print(f"  Margin Below Floor: {violations['margin_below_floor']}")
        print(f"  Stockouts Exist: {violations['stockouts_exist']}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run cleaner.py first to generate cleaned datasets.")

if __name__ == "__main__":
    main()