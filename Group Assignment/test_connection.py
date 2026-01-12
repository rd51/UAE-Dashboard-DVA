"""
Diagnostic Script - Tests all file connections and data flow
Run this BEFORE running the dashboard to identify issues
"""

import os
import sys

print("="*60)
print("DIAGNOSTIC TEST - UAE Promo Pulse")
print("="*60)
print()

# Test 1: Check if all Python files exist
print("TEST 1: Checking Python files...")
required_files = ['data_generator.py', 'cleaner.py', 'simulator.py', 'app_enhanced.py']
for file in required_files:
    if os.path.exists(file):
        print(f"  ✅ {file} found")
    else:
        print(f"  ❌ {file} MISSING")

print()

# Test 2: Check if data files exist
print("TEST 2: Checking data files...")
data_files = {
    'Raw': ['products.csv', 'stores.csv', 'sales_raw.csv', 'inventory_snapshot.csv', 'campaign_plan.csv'],
    'Clean': ['products_clean.csv', 'stores_clean.csv', 'sales_clean.csv', 'inventory_clean.csv', 'issues.csv']
}

for category, files in data_files.items():
    print(f"\n  {category} Files:")
    for file in files:
        if os.path.exists(file):
            print(f"    ✅ {file}")
        else:
            print(f"    ❌ {file} - Run {'data_generator.py' if category == 'Raw' else 'cleaner.py'}")

print()

# Test 3: Try importing modules
print("TEST 3: Testing imports...")
try:
    import pandas as pd
    print("  ✅ pandas")
except ImportError as e:
    print(f"  ❌ pandas - {e}")

try:
    import numpy as np
    print("  ✅ numpy")
except ImportError as e:
    print(f"  ❌ numpy - {e}")

try:
    import streamlit as st
    print("  ✅ streamlit")
except ImportError as e:
    print(f"  ❌ streamlit - {e}")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    print("  ✅ plotly (all modules)")
except ImportError as e:
    print(f"  ❌ plotly - {e}")

print()

# Test 4: Try loading data files
print("TEST 4: Testing data loading...")
try:
    import pandas as pd
    
    if os.path.exists('products_clean.csv'):
        products = pd.read_csv('products_clean.csv')
        print(f"  ✅ products_clean.csv loaded ({len(products)} rows)")
    else:
        print("  ⚠️  products_clean.csv not found - run cleaner.py first")
    
    if os.path.exists('stores_clean.csv'):
        stores = pd.read_csv('stores_clean.csv')
        print(f"  ✅ stores_clean.csv loaded ({len(stores)} rows)")
    else:
        print("  ⚠️  stores_clean.csv not found - run cleaner.py first")
    
    if os.path.exists('sales_clean.csv'):
        sales = pd.read_csv('sales_clean.csv')
        print(f"  ✅ sales_clean.csv loaded ({len(sales)} rows)")
    else:
        print("  ⚠️  sales_clean.csv not found - run cleaner.py first")
    
    if os.path.exists('inventory_clean.csv'):
        inventory = pd.read_csv('inventory_clean.csv')
        print(f"  ✅ inventory_clean.csv loaded ({len(inventory)} rows)")
    else:
        print("  ⚠️  inventory_clean.csv not found - run cleaner.py first")

except Exception as e:
    print(f"  ❌ Error loading data: {e}")

print()

# Test 5: Try importing simulator
print("TEST 5: Testing simulator module...")
try:
    from simulator import PromoSimulator
    print("  ✅ PromoSimulator class imported successfully")
    
    # Try initializing if data exists
    if all(os.path.exists(f) for f in ['products_clean.csv', 'stores_clean.csv', 
                                         'sales_clean.csv', 'inventory_clean.csv']):
        import pandas as pd
        products = pd.read_csv('products_clean.csv')
        stores = pd.read_csv('stores_clean.csv')
        sales = pd.read_csv('sales_clean.csv')
        inventory = pd.read_csv('inventory_clean.csv')
        
        sim = PromoSimulator(products, stores, sales, inventory)
        print("  ✅ PromoSimulator initialized successfully")
        
        # Test KPI computation
        kpis = sim.compute_kpis()
        print(f"  ✅ KPI computation works - Net Revenue: {kpis['net_revenue']:,.0f} AED")
        
except ImportError as e:
    print(f"  ❌ Cannot import simulator: {e}")
except Exception as e:
    print(f"  ❌ Error with simulator: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 6: Check data integrity
print("TEST 6: Checking data integrity...")
try:
    import pandas as pd
    
    if all(os.path.exists(f) for f in ['products_clean.csv', 'stores_clean.csv', 'sales_clean.csv']):
        products = pd.read_csv('products_clean.csv')
        stores = pd.read_csv('stores_clean.csv')
        sales = pd.read_csv('sales_clean.csv')
        
        # Check for required columns
        required_cols = {
            'products': ['product_id', 'category', 'brand', 'base_price_aed', 'unit_cost_aed'],
            'stores': ['store_id', 'city', 'channel', 'fulfillment_type'],
            'sales': ['order_id', 'order_time', 'product_id', 'store_id', 'qty', 'selling_price_aed', 'payment_status']
        }
        
        dfs = {'products': products, 'stores': stores, 'sales': sales}
        
        for name, df in dfs.items():
            missing = [col for col in required_cols[name] if col not in df.columns]
            if missing:
                print(f"  ❌ {name}.csv missing columns: {missing}")
            else:
                print(f"  ✅ {name}.csv has all required columns")
        
        # Check for foreign key integrity
        sales_products = set(sales['product_id'].unique())
        products_ids = set(products['product_id'].unique())
        orphan_products = sales_products - products_ids
        
        if orphan_products:
            print(f"  ⚠️  Warning: {len(orphan_products)} product_ids in sales not in products table")
        else:
            print("  ✅ All sales.product_id values exist in products table")
        
        sales_stores = set(sales['store_id'].unique())
        stores_ids = set(stores['store_id'].unique())
        orphan_stores = sales_stores - stores_ids
        
        if orphan_stores:
            print(f"  ⚠️  Warning: {len(orphan_stores)} store_ids in sales not in stores table")
        else:
            print("  ✅ All sales.store_id values exist in stores table")

except Exception as e:
    print(f"  ❌ Data integrity check failed: {e}")

print()
print("="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
print()

# Summary and recommendations
print("RECOMMENDATIONS:")
print()

if not all(os.path.exists(f) for f in ['products.csv', 'stores.csv', 'sales_raw.csv', 
                                         'inventory_snapshot.csv', 'campaign_plan.csv']):
    print("1. ⚠️  Run: python data_generator.py")

if not all(os.path.exists(f) for f in ['products_clean.csv', 'stores_clean.csv', 
                                         'sales_clean.csv', 'inventory_clean.csv', 'issues.csv']):
    print("2. ⚠️  Run: python cleaner.py")

try:
    from simulator import PromoSimulator
    if all(os.path.exists(f) for f in ['products_clean.csv', 'stores_clean.csv', 
                                         'sales_clean.csv', 'inventory_clean.csv']):
        print("3. ✅ Ready to run: streamlit run app_enhanced.py")
    else:
        print("3. ⚠️  Complete steps 1-2 first, then run: streamlit run app_enhanced.py")
except:
    print("3. ❌ Fix simulator.py errors before running dashboard")

print()
print("If you see errors above, copy and paste them for help!")