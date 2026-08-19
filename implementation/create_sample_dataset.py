"""
Sample Custom Dataset Generator
Create example CSV files for custom data upload
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(123)
random.seed(123)

def create_sample_products():
    """Create sample products CSV"""
    data = {
        'product_id': [f'P{str(i).zfill(4)}' for i in range(1, 51)],
        'category': np.random.choice(['Electronics', 'Fashion', 'Home & Kitchen', 'Grocery', 'Beauty'], 50),
        'brand': np.random.choice(['Samsung', 'Apple', 'Nike', 'Adidas', 'LG', 'Sony', 'Carrefour'], 50),
        'unit_cost_aed': np.random.uniform(20, 500, 50).round(2)
    }
    df = pd.DataFrame(data)
    df.to_csv('sample_products.csv', index=False)
    print(f"✓ Created: sample_products.csv ({len(df)} rows)")

def create_sample_stores():
    """Create sample stores CSV"""
    cities = ['Dubai', 'Abu Dhabi', 'Sharjah']
    channels = ['App', 'Web', 'Marketplace']
    
    data = []
    store_id = 1
    for city in cities:
        for channel in channels:
            for i in range(2):  # 2 stores per city-channel combination
                data.append({
                    'store_id': f'S{str(store_id).zfill(3)}',
                    'city': city,
                    'channel': channel
                })
                store_id += 1
    
    df = pd.DataFrame(data)
    df.to_csv('sample_stores.csv', index=False)
    print(f"✓ Created: sample_stores.csv ({len(df)} rows)")

def create_sample_sales():
    """Create sample sales CSV"""
    products = [f'P{str(i).zfill(4)}' for i in range(1, 51)]
    stores = [f'S{str(i).zfill(3)}' for i in range(1, 19)]
    
    start_date = datetime(2024, 9, 1)
    data = []
    
    for i in range(1, 1001):  # 1000 orders
        order_date = start_date + timedelta(days=random.randint(0, 120))
        
        data.append({
            'order_id': f'ORD{str(i).zfill(6)}',
            'order_time': order_date.strftime('%Y-%m-%d %H:%M:%S'),
            'product_id': random.choice(products),
            'store_id': random.choice(stores),
            'qty': random.randint(1, 5),
            'selling_price_aed': round(random.uniform(50, 500), 2),
            'discount_pct': random.choice([0, 5, 10, 15, 20, 25]),
            'payment_status': random.choice(['Paid', 'Paid', 'Paid', 'Failed', 'Refunded']),
            'return_flag': random.choice(['N', 'N', 'N', 'N', 'N', 'Y'])  # 20% return rate
        })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_sales.csv', index=False)
    print(f"✓ Created: sample_sales.csv ({len(df)} rows)")

def create_sample_inventory():
    """Create sample inventory CSV"""
    products = [f'P{str(i).zfill(4)}' for i in range(1, 51)]
    stores = [f'S{str(i).zfill(3)}' for i in range(1, 19)]
    
    start_date = datetime(2024, 12, 1)
    data = []
    
    for day in range(30):
        snapshot_date = (start_date - timedelta(days=day)).strftime('%Y-%m-%d')
        
        for product_id in products[::3]:  # Sample every 3rd product
            for store_id in stores[::2]:  # Sample every 2nd store
                data.append({
                    'snapshot_date': snapshot_date,
                    'product_id': product_id,
                    'store_id': store_id,
                    'stock_on_hand': random.randint(10, 500),
                    'reorder_point': random.randint(20, 100),
                    'lead_time_days': random.randint(3, 14)
                })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_inventory.csv', index=False)
    print(f"✓ Created: sample_inventory.csv ({len(df)} rows)")

def create_sample_issues():
    """Create sample issues CSV (optional)"""
    data = {
        'issue_id': [f'ISS{str(i).zfill(4)}' for i in range(1, 11)],
        'issue_type': np.random.choice(['Missing Value', 'Duplicate', 'Outlier', 'Format Error'], 10),
        'description': [
            'Missing discount percentage in order ORD000005',
            'Duplicate order ID detected: ORD000010',
            'Price outlier: 50x normal price',
            'Invalid date format in order ORD000015',
            'Stock quantity negative: -50 units',
            'City name mismatch: Dubayy vs Dubai',
            'Missing product cost for P0001',
            'Channel mismatch: Shop vs App',
            'Quantity outlier: 500 units ordered',
            'Payment status unknown for ORD000020'
        ],
        'severity': np.random.choice(['High', 'Medium', 'Low'], 10)
    }
    df = pd.DataFrame(data)
    df.to_csv('sample_issues.csv', index=False)
    print(f"✓ Created: sample_issues.csv ({len(df)} rows)")

def main():
    print("=" * 60)
    print("Creating Sample Dataset Files for Custom Upload")
    print("=" * 60)
    print()
    
    create_sample_products()
    create_sample_stores()
    create_sample_sales()
    create_sample_inventory()
    create_sample_issues()
    
    print()
    print("=" * 60)
    print("Sample files created successfully!")
    print("=" * 60)
    print()
    print("Files generated:")
    print("  - sample_products.csv")
    print("  - sample_stores.csv")
    print("  - sample_sales.csv")
    print("  - sample_inventory.csv")
    print("  - sample_issues.csv (optional)")
    print()
    print("To use these files:")
    print("  1. Launch the dashboard")
    print("  2. Select '📤 Upload Custom Data' in sidebar")
    print("  3. Upload: sample_products.csv, sample_stores.csv,")
    print("           sample_sales.csv, sample_inventory.csv")
    print("  4. Optionally upload: sample_issues.csv")
    print("  5. Dashboard will load with sample data")
    print()
    print("💡 Tip: Edit these files to customize the data for your needs!")

if __name__ == "__main__":
    main()
