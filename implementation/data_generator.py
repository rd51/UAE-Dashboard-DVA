"""
UAE Promo Pulse - Data Generator
Generates realistic dirty datasets with injected data quality issues
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_products(n_products=300):
    """Generate products table with missing unit costs"""
    categories = ['Electronics', 'Fashion', 'Home & Kitchen', 'Grocery', 
                  'Beauty', 'Sports', 'Books', 'Toys']
    brands = ['Samsung', 'Apple', 'Nike', 'Adidas', 'LG', 'Sony', 
              'Puma', 'H&M', 'Zara', 'Noon', 'Carrefour', 'Lulu']
    
    products = []
    for i in range(1, n_products + 1):
        product_id = f"P{str(i).zfill(4)}"
        category = random.choice(categories)
        brand = random.choice(brands)
        base_price = round(random.uniform(50, 4050), 2)
        
        # INJECT ISSUE: Missing unit_cost for ~2% of products
        if random.random() < 0.02:
            unit_cost = np.nan
        else:
            unit_cost = round(base_price * random.uniform(0.4, 0.7), 2)
        
        tax_rate = 0.05
        launch_flag = 'New' if random.random() < 0.15 else 'Regular'
        
        products.append({
            'product_id': product_id,
            'category': category,
            'brand': brand,
            'base_price_aed': base_price,
            'unit_cost_aed': unit_cost,
            'tax_rate': tax_rate,
            'launch_flag': launch_flag
        })
    
    return pd.DataFrame(products)

def generate_stores():
    """Generate stores table with inconsistent city names"""
    city_variants = {
        'Dubai': ['Dubai', 'DUBAI', 'dubai', 'Dubayy', 'Dubai ', ' Dubai'],
        'Abu Dhabi': ['Abu Dhabi', 'ABU DHABI', 'abu dhabi', 'AbuDhabi', 'Abu-Dhabi'],
        'Sharjah': ['Sharjah', 'SHARJAH', 'sharjah', 'Sharja', 'Sharjh']
    }
    
    channels = ['App', 'Web', 'Marketplace']
    fulfillment_types = ['Own', '3PL']
    
    stores = []
    store_id = 1
    
    for city in city_variants.keys():
        for channel in channels:
            for fulfill in fulfillment_types:
                # INJECT ISSUE: Inconsistent city names for ~26% of stores
                if random.random() < 0.26:
                    chosen_city = random.choice(city_variants[city])
                else:
                    chosen_city = city
                
                stores.append({
                    'store_id': f"S{str(store_id).zfill(3)}",
                    'city': chosen_city,
                    'channel': channel,
                    'fulfillment_type': fulfill
                })
                store_id += 1
    
    return pd.DataFrame(stores)

def generate_sales_raw(n_orders=32500, products_df=None, stores_df=None):
    """Generate sales_raw table with multiple data quality issues"""
    if products_df is None or stores_df is None:
        raise ValueError("Products and stores dataframes required")
    
    payment_statuses = ['Paid', 'Failed', 'Refunded']
    corrupted_times = ['not_a_time', '2024-13-45', '99/99/9999', 
                       'invalid', '2024-02-30 25:99:99']
    
    start_date = datetime(2024, 9, 10)
    sales = []
    
    for i in range(1, n_orders + 1):
        order_id = f"ORD{str(i).zfill(6)}"
        
        # INJECT ISSUE: Duplicate order_ids for ~0.5%
        if random.random() < 0.005 and i > 100:
            dup_id = random.randint(1, i - 100)
            order_id = f"ORD{str(dup_id).zfill(6)}"
        
        # Generate order time (last 120 days)
        days_ago = random.randint(0, 120)
        order_date = start_date - timedelta(days=days_ago)
        
        # INJECT ISSUE: Corrupted timestamps for ~1.6%
        if random.random() < 0.016:
            order_time = random.choice(corrupted_times)
        else:
            order_time = order_date.strftime('%Y-%m-%d %H:%M:%S')
        
        product_id = random.choice(products_df['product_id'].values)
        store_id = random.choice(stores_df['store_id'].values)
        
        # INJECT ISSUE: Outlier quantities for ~0.4%
        if random.random() < 0.004:
            qty = random.choice([50, 75])
        else:
            qty = random.randint(1, 5)
        
        # Get base price
        base_price = products_df[products_df['product_id'] == product_id]['base_price_aed'].values[0]
        
        # INJECT ISSUE: Outlier prices for ~0.4%
        if random.random() < 0.004:
            selling_price = base_price * random.choice([10, 15])
        else:
            selling_price = base_price
        
        # INJECT ISSUE: Missing discount_pct for ~3%
        if random.random() < 0.03:
            discount_pct = np.nan
        else:
            discount_pct = random.randint(0, 40)
        
        # Payment status distribution
        rand = random.random()
        if rand < 0.85:
            payment_status = 'Paid'
        elif rand < 0.95:
            payment_status = 'Failed'
        else:
            payment_status = 'Refunded'
        
        return_flag = 'Y' if random.random() < 0.05 else 'N'
        
        sales.append({
            'order_id': order_id,
            'order_time': order_time,
            'product_id': product_id,
            'store_id': store_id,
            'qty': qty,
            'selling_price_aed': selling_price,
            'discount_pct': discount_pct,
            'payment_status': payment_status,
            'return_flag': return_flag
        })
    
    return pd.DataFrame(sales)

def generate_inventory_snapshot(products_df=None, stores_df=None, n_days=30):
    """Generate inventory snapshot with impossible inventory values"""
    if products_df is None or stores_df is None:
        raise ValueError("Products and stores dataframes required")
    
    start_date = datetime(2024, 12, 10)
    inventory = []
    
    # Sample products (every 3rd product to reduce size)
    sampled_products = products_df[::3]['product_id'].values
    
    for day in range(n_days):
        snapshot_date = (start_date - timedelta(days=day)).strftime('%Y-%m-%d')
        
        for product_id in sampled_products:
            store_id = random.choice(stores_df['store_id'].values)
            
            # INJECT ISSUE: Impossible inventory for ~0.6%
            if random.random() < 0.006:
                stock_on_hand = random.choice([-15, 9999])
            else:
                stock_on_hand = random.randint(10, 210)
            
            reorder_point = random.randint(20, 70)
            lead_time_days = random.randint(3, 12)
            
            inventory.append({
                'snapshot_date': snapshot_date,
                'product_id': product_id,
                'store_id': store_id,
                'stock_on_hand': stock_on_hand,
                'reorder_point': reorder_point,
                'lead_time_days': lead_time_days
            })
    
    return pd.DataFrame(inventory)

def generate_campaign_plan():
    """Generate campaign plan table (clean data)"""
    campaigns = [
        ['C001', '2025-01-15', '2025-01-22', 'Dubai', 'App', 'Electronics', 25, 50000],
        ['C002', '2025-01-15', '2025-01-29', 'All', 'Web', 'Fashion', 20, 75000],
        ['C003', '2025-01-18', '2025-01-25', 'Abu Dhabi', 'Marketplace', 'All', 30, 40000],
        ['C004', '2025-01-10', '2025-01-20', 'Sharjah', 'All', 'Grocery', 15, 30000],
        ['C005', '2025-01-12', '2025-01-26', 'All', 'App', 'Beauty', 22, 60000],
        ['C006', '2025-01-20', '2025-02-03', 'Dubai', 'Web', 'Home & Kitchen', 18, 45000],
        ['C007', '2025-01-14', '2025-01-28', 'All', 'Marketplace', 'Sports', 28, 55000],
        ['C008', '2025-01-16', '2025-01-23', 'Abu Dhabi', 'App', 'All', 20, 70000],
        ['C009', '2025-01-19', '2025-02-02', 'Sharjah', 'Web', 'Toys', 25, 35000],
        ['C010', '2025-01-11', '2025-01-25', 'Dubai', 'All', 'Books', 30, 25000]
    ]
    
    df = pd.DataFrame(campaigns, columns=[
        'campaign_id', 'start_date', 'end_date', 'city', 'channel', 
        'category', 'discount_pct', 'promo_budget_aed'
    ])
    
    return df

def main():
    """Generate all datasets and save to CSV"""
    print("Generating UAE Promo Pulse Datasets...")
    
    # Generate products
    print("Generating products...")
    products_df = generate_products(300)
    products_df.to_csv('products.csv', index=False)
    print(f"✓ Products: {len(products_df)} rows")
    
    # Generate stores
    print("Generating stores...")
    stores_df = generate_stores()
    stores_df.to_csv('stores.csv', index=False)
    print(f"✓ Stores: {len(stores_df)} rows")
    
    # Generate sales
    print("Generating sales_raw (this may take a moment)...")
    sales_df = generate_sales_raw(32500, products_df, stores_df)
    sales_df.to_csv('sales_raw.csv', index=False)
    print(f"✓ Sales: {len(sales_df)} rows")
    
    # Generate inventory
    print("Generating inventory_snapshot...")
    inventory_df = generate_inventory_snapshot(products_df, stores_df, 30)
    inventory_df.to_csv('inventory_snapshot.csv', index=False)
    print(f"✓ Inventory: {len(inventory_df)} rows")
    
    # Generate campaigns
    print("Generating campaign_plan...")
    campaigns_df = generate_campaign_plan()
    campaigns_df.to_csv('campaign_plan.csv', index=False)
    print(f"✓ Campaigns: {len(campaigns_df)} rows")
    
    print("\n" + "="*60)
    print("Dataset Generation Complete!")
    print("="*60)
    print("\nInjected Issues Summary:")
    print(f"  • Missing unit_cost_aed: ~{products_df['unit_cost_aed'].isna().sum()} products")
    print(f"  • Inconsistent cities: ~{len(stores_df)} stores")
    print(f"  • Missing discount_pct: ~{sales_df['discount_pct'].isna().sum()} sales")
    print(f"  • Duplicate order_ids: detected during validation")
    print(f"  • Corrupted timestamps: detected during validation")
    print(f"  • Outliers: detected during validation")
    print(f"  • Impossible inventory: detected during validation")
    print("\nFiles saved:")
    print("  - products.csv")
    print("  - stores.csv")
    print("  - sales_raw.csv")
    print("  - inventory_snapshot.csv")
    print("  - campaign_plan.csv")

if __name__ == "__main__":
    main()