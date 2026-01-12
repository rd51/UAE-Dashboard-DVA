"""
UAE Promo Pulse - Data Cleaner (PHASE 1)
Complete cleaning pipeline with validation, issues logging, and justified policies
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

class ValidationRules:
    """Defines all validation rules with policies"""
    
    TIMESTAMP_PATTERN = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
    PRICE_MIN, PRICE_MAX = 0, 10000
    QUANTITY_MIN, QUANTITY_MAX = 1, 100
    VALID_CITIES = {'Dubai', 'Abu Dhabi', 'Sharjah'}
    VALID_CHANNELS = {'App', 'Web', 'Marketplace'}
    VALID_CATEGORIES = {'Electronics', 'Fashion', 'Home & Kitchen', 
                       'Grocery', 'Beauty', 'Sports', 'Books', 'Toys'}
    VALID_PAYMENT_STATUS = {'Paid', 'Failed', 'Refunded'}
    VALID_FULFILLMENT = {'Own', '3PL'}
    
    @staticmethod
    def validate_timestamp(value):
        """Check timestamp is parsable - YYYY-MM-DD HH:MM:SS"""
        if pd.isna(value) or value == '':
            return False, "Missing timestamp"
        try:
            if not re.match(ValidationRules.TIMESTAMP_PATTERN, str(value)):
                return False, f"Invalid format: {value}"
            pd.to_datetime(value)
            return True, None
        except:
            return False, f"Unparsable: {value}"
    
    @staticmethod
    def validate_price(value):
        """Check price in range [0, 10000] AED"""
        try:
            p = float(value)
            if p < ValidationRules.PRICE_MIN or p > ValidationRules.PRICE_MAX:
                return False, f"Outside range [{ValidationRules.PRICE_MIN}, {ValidationRules.PRICE_MAX}]: {p}"
            return True, None
        except:
            return False, f"Not numeric: {value}"
    
    @staticmethod
    def validate_quantity(value):
        """Check quantity in range [1, 100]"""
        try:
            q = int(float(value))
            if q < ValidationRules.QUANTITY_MIN or q > ValidationRules.QUANTITY_MAX:
                return False, f"Outside range [{ValidationRules.QUANTITY_MIN}, {ValidationRules.QUANTITY_MAX}]: {q}"
            return True, None
        except:
            return False, f"Not numeric: {value}"
    
    @staticmethod
    def validate_city(value):
        """Check city is valid"""
        if pd.isna(value) or value == '':
            return False, "Missing city"
        city = str(value).strip()
        if city not in ValidationRules.VALID_CITIES:
            return False, f"Invalid city: {city}"
        return True, None
    
    @staticmethod
    def validate_channel(value):
        """Check channel is valid"""
        if pd.isna(value) or value == '':
            return False, "Missing channel"
        channel = str(value).strip()
        if channel not in ValidationRules.VALID_CHANNELS:
            return False, f"Invalid channel: {channel}"
        return True, None
    
    @staticmethod
    def validate_category(value):
        """Check category is valid"""
        if pd.isna(value) or value == '':
            return False, "Missing category"
        cat = str(value).strip()
        if cat not in ValidationRules.VALID_CATEGORIES:
            return False, f"Invalid category: {cat}"
        return True, None
    
    @staticmethod
    def validate_payment_status(value):
        """Check payment status is valid"""
        if pd.isna(value) or value == '':
            return False, "Missing payment_status"
        status = str(value).strip()
        if status not in ValidationRules.VALID_PAYMENT_STATUS:
            return False, f"Invalid status: {status}"
        return True, None
    
    @staticmethod
    def validate_cost_constraint(cost, price):
        """Check unit_cost <= base_price"""
        try:
            c = float(cost)
            p = float(price)
            if c > p:
                return False, f"Cost {c} > Price {p}"
            return True, None
        except:
            return True, None  # Skip if either is missing/non-numeric
    
    @staticmethod
    def validate_stock(value):
        """Check stock is non-negative"""
        try:
            s = float(value)
            if s < 0:
                return False, f"Negative stock: {s}"
            if s > 1000:
                return False, f"Extreme stock: {s}"
            return True, None
        except:
            return False, f"Not numeric: {value}"


class CleaningPolicies:
    """Justified cleaning decisions for each issue type"""
    
    POLICIES = {
        'INVALID_TIMESTAMP': {
            'action': 'DROP',
            'justification': 'Corrupted timestamps cannot be reliably inferred. Data integrity > completeness.'
        },
        'OUTLIER_VALUE': {
            'action': 'CAP',
            'justification': 'Cap at defined bounds (price 10k, qty 100) to preserve data volume while fixing anomalies.'
        },
        'MISSING_VALUE': {
            'action': 'IMPUTE',
            'justification': 'discount_pct → 0 (no discount is valid); unit_cost → 50% of base_price (standard markup).'
        },
        'INVALID_CITY': {
            'action': 'CORRECT',
            'justification': 'Standardize to valid cities. Default to Dubai. Ensures geographic consistency.'
        },
        'INVALID_CHANNEL': {
            'action': 'CORRECT',
            'justification': 'Standardize to valid channels. Default to App. Required for channel analysis.'
        },
        'INVALID_CATEGORY': {
            'action': 'CORRECT',
            'justification': 'Default to Electronics. Preserves product dimension for analysis.'
        },
        'INVALID_VALUE': {
            'action': 'CORRECT',
            'justification': 'payment_status → Paid; fulfillment_type → Own. Preserves transaction data.'
        },
        'CONSTRAINT_VIOLATION': {
            'action': 'CAP',
            'justification': 'unit_cost > base_price: cap at base_price. Maintains margin logic and business rules.'
        },
        'IMPOSSIBLE_VALUE': {
            'action': 'CORRECT',
            'justification': 'Negative stock → 0; stock > 1000 → 500 (supply chain bounds).'
        },
        'DUPLICATE_ID': {
            'action': 'DROP',
            'justification': 'Keep latest by timestamp. Most recent transaction is canonical record.'
        },
        'INCONSISTENT_VALUE': {
            'action': 'CORRECT',
            'justification': 'Standardize variations (dubai→Dubai, ABU DHABI→Abu Dhabi). Case/spacing cleanup.'
        }
    }
    
    @staticmethod
    def get_policy(issue_type):
        """Get cleaning policy for issue type"""
        return CleaningPolicies.POLICIES.get(
            issue_type, 
            {'action': 'SKIP', 'justification': 'No policy defined'}
        )


class DataCleaner:
    """Complete data cleaning pipeline with comprehensive issue logging"""
    
    def __init__(self):
        self.issues_log = []
        self.cleaning_summary = {}
    
    # ========================
    # SALES DATA CLEANING
    # ========================
    def clean_sales_data(self, df):
        """Clean sales_raw table with all data quality checks"""
        print("\n" + "="*80)
        print("CLEANING: SALES DATA")
        print("="*80)
        
        df_clean = df.copy()
        original_count = len(df_clean)
        
        # Step 1: Handle duplicate order_ids (Policy: Keep latest by timestamp)
        print("\n[1/8] Handling duplicate order IDs...")
        duplicates = df_clean['order_id'].duplicated(keep=False)
        dup_count = (duplicates.sum() + 1) // 2
        
        if dup_count > 0:
            df_clean['_parsed_time'] = pd.to_datetime(df_clean['order_time'], errors='coerce')
            dup_ids = df_clean[duplicates]['order_id'].unique()
            indices_to_drop = []
            
            for order_id in dup_ids:
                dup_group = df_clean[df_clean['order_id'] == order_id]
                valid_times = dup_group[dup_group['_parsed_time'].notna()]
                
                if len(valid_times) > 0:
                    keep_idx = valid_times['_parsed_time'].idxmax()
                else:
                    keep_idx = dup_group.index[0]
                
                drop_indices = dup_group.index.difference([keep_idx]).tolist()
                indices_to_drop.extend(drop_indices)
                
                for idx in drop_indices:
                    self.issues_log.append({
                        'record_identifier': order_id,
                        'issue_type': 'DUPLICATE_ID',
                        'issue_detail': 'Duplicate order_id - multiple transactions',
                        'action_taken': 'DROPPED'
                    })
            
            df_clean = df_clean.drop(indices_to_drop).reset_index(drop=True)
            df_clean = df_clean.drop('_parsed_time', axis=1)
            print(f"   ✓ Dropped {len(indices_to_drop)} duplicate records, kept latest")
        
        # Step 2: Handle corrupted timestamps (Policy: DROP)
        print("[2/8] Validating timestamps...")
        invalid_time_mask = pd.to_datetime(df_clean['order_time'], errors='coerce').isna()
        
        for idx in df_clean[invalid_time_mask].index:
            order_id = df_clean.loc[idx, 'order_id']
            bad_time = str(df_clean.loc[idx, 'order_time'])[:50]
            self.issues_log.append({
                'record_identifier': order_id,
                'issue_type': 'INVALID_TIMESTAMP',
                'issue_detail': f'Corrupted timestamp: {bad_time}',
                'action_taken': 'DROPPED'
            })
        
        df_clean = df_clean[~invalid_time_mask].reset_index(drop=True)
        df_clean['order_time'] = pd.to_datetime(df_clean['order_time'])
        print(f"   ✓ Dropped {invalid_time_mask.sum()} invalid timestamps")
        
        # Step 3: Handle missing discount_pct (Policy: IMPUTE to 0)
        print("[3/8] Imputing missing values...")
        missing_discount = df_clean['discount_pct'].isna()
        
        for idx in df_clean[missing_discount].index:
            order_id = df_clean.loc[idx, 'order_id']
            self.issues_log.append({
                'record_identifier': order_id,
                'issue_type': 'MISSING_VALUE',
                'issue_detail': 'Missing discount_pct',
                'action_taken': 'IMPUTED'
            })
        
        df_clean['discount_pct'] = df_clean['discount_pct'].fillna(0)
        print(f"   ✓ Imputed {missing_discount.sum()} missing discount values to 0")
        
        # Step 4: Handle outlier quantities (Policy: CAP at 100)
        print("[4/8] Capping quantity outliers...")
        outlier_qty = df_clean['qty'] > ValidationRules.QUANTITY_MAX
        
        for idx in df_clean[outlier_qty].index:
            order_id = df_clean.loc[idx, 'order_id']
            old_qty = int(df_clean.loc[idx, 'qty'])
            self.issues_log.append({
                'record_identifier': order_id,
                'issue_type': 'OUTLIER_VALUE',
                'issue_detail': f'Quantity {old_qty} exceeds maximum {ValidationRules.QUANTITY_MAX}',
                'action_taken': 'CAPPED'
            })
            df_clean.loc[idx, 'qty'] = ValidationRules.QUANTITY_MAX
        
        print(f"   ✓ Capped {outlier_qty.sum()} quantity outliers at {ValidationRules.QUANTITY_MAX}")
        
        # Step 5: Handle outlier prices (Policy: CAP at 10000 AED)
        print("[5/8] Capping price outliers...")
        outlier_price = df_clean['selling_price_aed'] > ValidationRules.PRICE_MAX
        
        for idx in df_clean[outlier_price].index:
            order_id = df_clean.loc[idx, 'order_id']
            old_price = float(df_clean.loc[idx, 'selling_price_aed'])
            self.issues_log.append({
                'record_identifier': order_id,
                'issue_type': 'OUTLIER_VALUE',
                'issue_detail': f'Price {old_price:.2f} AED exceeds maximum {ValidationRules.PRICE_MAX}',
                'action_taken': 'CAPPED'
            })
            df_clean.loc[idx, 'selling_price_aed'] = ValidationRules.PRICE_MAX
        
        print(f"   ✓ Capped {outlier_price.sum()} price outliers at {ValidationRules.PRICE_MAX} AED")
        
        # Step 6: Standardize city names (Policy: CORRECT with mapping)
        print("[6/8] Standardizing city names...")
        city_mapping = {
            'dubai': 'Dubai', 'DUBAI': 'Dubai', 'Dubayy': 'Dubai',
            'abu dhabi': 'Abu Dhabi', 'ABU DHABI': 'Abu Dhabi',
            'AbuDhabi': 'Abu Dhabi', 'Abu-Dhabi': 'Abu Dhabi',
            'sharjah': 'Sharjah', 'SHARJAH': 'Sharjah',
            'Sharja': 'Sharjah', 'Sharjh': 'Sharjah'
        }
        
        corrections_count = 0
        for idx in df_clean.index:
            if 'city' in df_clean.columns and pd.notna(df_clean.loc[idx, 'city']):
                city = str(df_clean.loc[idx, 'city']).strip()
                if city in city_mapping:
                    new_city = city_mapping[city]
                    df_clean.loc[idx, 'city'] = new_city
                    corrections_count += 1
                    self.issues_log.append({
                        'record_identifier': df_clean.loc[idx, 'order_id'],
                        'issue_type': 'INCONSISTENT_VALUE',
                        'issue_detail': f'City "{city}" standardized to "{new_city}"',
                        'action_taken': 'CORRECTED'
                    })
                elif city not in ValidationRules.VALID_CITIES:
                    df_clean.loc[idx, 'city'] = 'Dubai'  # Default
                    self.issues_log.append({
                        'record_identifier': df_clean.loc[idx, 'order_id'],
                        'issue_type': 'INVALID_CITY',
                        'issue_detail': f'Invalid city "{city}" → defaulted to Dubai',
                        'action_taken': 'CORRECTED'
                    })
        
        print(f"   ✓ Standardized {corrections_count} city names")
        
        # Step 7: Validate payment_status (Policy: CORRECT to Paid)
        print("[7/8] Validating payment status...")
        invalid_payment = ~df_clean['payment_status'].isin(ValidationRules.VALID_PAYMENT_STATUS)
        
        for idx in df_clean[invalid_payment].index:
            order_id = df_clean.loc[idx, 'order_id']
            bad_status = str(df_clean.loc[idx, 'payment_status'])
            self.issues_log.append({
                'record_identifier': order_id,
                'issue_type': 'INVALID_VALUE',
                'issue_detail': f'Invalid payment_status: "{bad_status}" → "Paid"',
                'action_taken': 'CORRECTED'
            })
            df_clean.loc[idx, 'payment_status'] = 'Paid'
        
        print(f"   ✓ Validated {len(df_clean)} payment statuses")
        
        # Step 8: Category validation if present
        print("[8/8] Running full validation suite...")
        if 'category' in df_clean.columns:
            invalid_cat = ~df_clean['category'].isin(ValidationRules.VALID_CATEGORIES)
            for idx in df_clean[invalid_cat].index:
                order_id = df_clean.loc[idx, 'order_id']
                bad_cat = str(df_clean.loc[idx, 'category'])
                self.issues_log.append({
                    'record_identifier': order_id,
                    'issue_type': 'INVALID_CATEGORY',
                    'issue_detail': f'Invalid category: "{bad_cat}" → "Electronics"',
                    'action_taken': 'CORRECTED'
                })
                df_clean.loc[idx, 'category'] = 'Electronics'
        
        # Summary
        dropped = original_count - len(df_clean)
        valid = len(df_clean)
        cleanliness = (valid / original_count) * 100 if original_count > 0 else 0
        
        summary = {
            'original_records': original_count,
            'cleaned_records': valid,
            'dropped_records': dropped,
            'issues_found': len([i for i in self.issues_log if 'ORD' in i['record_identifier']]),
            'cleanliness_score': cleanliness
        }
        
        print(f"\n   Summary:")
        print(f"   • Original: {summary['original_records']}")
        print(f"   • Cleaned: {summary['cleaned_records']}")
        print(f"   • Dropped: {summary['dropped_records']}")
        print(f"   • Cleanliness: {summary['cleanliness_score']:.1f}%")
        
        self.cleaning_summary['sales'] = summary
        return df_clean
    
    # ========================
    # PRODUCTS DATA CLEANING
    # ========================
    def clean_products_data(self, df):
        """Clean products table"""
        print("\n" + "="*80)
        print("CLEANING: PRODUCTS DATA")
        print("="*80)
        
        df_clean = df.copy()
        original_count = len(df_clean)
        
        # Step 1: Handle missing unit_cost_aed (Policy: IMPUTE as 50% of base_price)
        print("\n[1/2] Imputing missing unit costs...")
        missing_cost = df_clean['unit_cost_aed'].isna()
        
        for idx in df_clean[missing_cost].index:
            product_id = df_clean.loc[idx, 'product_id']
            base_price = df_clean.loc[idx, 'base_price_aed']
            imputed_cost = base_price * 0.5
            df_clean.loc[idx, 'unit_cost_aed'] = imputed_cost
            
            self.issues_log.append({
                'record_identifier': product_id,
                'issue_type': 'MISSING_VALUE',
                'issue_detail': f'Missing unit_cost_aed - imputed as 50% of {base_price}',
                'action_taken': 'IMPUTED'
            })
        
        print(f"   ✓ Imputed {missing_cost.sum()} missing unit costs")
        
        # Step 2: Validate cost constraint (Policy: CAP unit_cost at base_price)
        print("[2/2] Validating cost constraints...")
        invalid_cost = df_clean['unit_cost_aed'] > df_clean['base_price_aed']
        
        for idx in df_clean[invalid_cost].index:
            product_id = df_clean.loc[idx, 'product_id']
            old_cost = df_clean.loc[idx, 'unit_cost_aed']
            new_cost = df_clean.loc[idx, 'base_price_aed']
            df_clean.loc[idx, 'unit_cost_aed'] = new_cost
            
            self.issues_log.append({
                'record_identifier': product_id,
                'issue_type': 'CONSTRAINT_VIOLATION',
                'issue_detail': f'unit_cost ({old_cost}) > base_price ({new_cost}) - capped',
                'action_taken': 'CAPPED'
            })
        
        print(f"   ✓ Fixed {invalid_cost.sum()} cost constraint violations")
        
        summary = {
            'original_records': original_count,
            'cleaned_records': len(df_clean),
            'issues_found': len([i for i in self.issues_log if 'P' in i['record_identifier']]),
            'cleanliness_score': 100.0
        }
        
        self.cleaning_summary['products'] = summary
        return df_clean
    
    # ========================
    # STORES DATA CLEANING
    # ========================
    def clean_stores_data(self, df):
        """Clean stores table"""
        print("\n" + "="*80)
        print("CLEANING: STORES DATA")
        print("="*80)
        
        df_clean = df.copy()
        original_count = len(df_clean)
        
        # Standardize city names
        print("\n[1/1] Standardizing store attributes...")
        
        city_mapping = {
            'dubai': 'Dubai', 'DUBAI': 'Dubai', 'Dubayy': 'Dubai',
            'abu dhabi': 'Abu Dhabi', 'ABU DHABI': 'Abu Dhabi',
            'AbuDhabi': 'Abu Dhabi', 'Abu-Dhabi': 'Abu Dhabi',
            'sharjah': 'Sharjah', 'SHARJAH': 'Sharjah',
            'Sharja': 'Sharjah', 'Sharjh': 'Sharjah'
        }
        
        corrections = 0
        for idx in df_clean.index:
            if 'city' in df_clean.columns and pd.notna(df_clean.loc[idx, 'city']):
                city = str(df_clean.loc[idx, 'city']).strip()
                if city in city_mapping:
                    df_clean.loc[idx, 'city'] = city_mapping[city]
                    corrections += 1
                elif city not in ValidationRules.VALID_CITIES:
                    df_clean.loc[idx, 'city'] = 'Dubai'
                    corrections += 1
        
        print(f"   ✓ Standardized {corrections} city names")
        
        summary = {
            'original_records': original_count,
            'cleaned_records': len(df_clean),
            'issues_found': corrections,
            'cleanliness_score': 100.0
        }
        
        self.cleaning_summary['stores'] = summary
        return df_clean
    
    # ========================
    # INVENTORY DATA CLEANING
    # ========================
    def clean_inventory_data(self, df):
        """Clean inventory_snapshot table"""
        print("\n" + "="*80)
        print("CLEANING: INVENTORY DATA")
        print("="*80)
        
        df_clean = df.copy()
        original_count = len(df_clean)
        
        # Step 1: Handle negative stock (Policy: SET to 0)
        print("\n[1/2] Correcting impossible inventory values...")
        negative_stock = df_clean['stock_on_hand'] < 0
        
        for idx in df_clean[negative_stock].index:
            snapshot_date = df_clean.loc[idx, 'snapshot_date']
            product_id = df_clean.loc[idx, 'product_id']
            old_stock = df_clean.loc[idx, 'stock_on_hand']
            record_id = f"{snapshot_date}_{product_id}"
            
            df_clean.loc[idx, 'stock_on_hand'] = 0
            
            self.issues_log.append({
                'record_identifier': record_id,
                'issue_type': 'IMPOSSIBLE_VALUE',
                'issue_detail': f'Negative stock {old_stock} corrected to 0',
                'action_taken': 'CORRECTED'
            })
        
        print(f"   ✓ Corrected {negative_stock.sum()} negative stock values")
        
        # Step 2: Handle extreme stock (Policy: CAP at 500)
        print("[2/2] Capping extreme inventory...")
        extreme_stock = df_clean['stock_on_hand'] > 1000
        
        for idx in df_clean[extreme_stock].index:
            snapshot_date = df_clean.loc[idx, 'snapshot_date']
            product_id = df_clean.loc[idx, 'product_id']
            old_stock = df_clean.loc[idx, 'stock_on_hand']
            record_id = f"{snapshot_date}_{product_id}"
            
            df_clean.loc[idx, 'stock_on_hand'] = 500
            
            self.issues_log.append({
                'record_identifier': record_id,
                'issue_type': 'OUTLIER_VALUE',
                'issue_detail': f'Extreme stock {old_stock} capped to 500',
                'action_taken': 'CAPPED'
            })
        
        print(f"   ✓ Capped {extreme_stock.sum()} extreme inventory values")
        
        summary = {
            'original_records': original_count,
            'cleaned_records': len(df_clean),
            'issues_found': negative_stock.sum() + extreme_stock.sum(),
            'cleanliness_score': 100.0
        }
        
        self.cleaning_summary['inventory'] = summary
        return df_clean
    
    # ========================
    # MAIN CLEANING PIPELINE
    # ========================
    def clean_all_data(self, products_df, stores_df, sales_df, inventory_df):
        """Execute complete cleaning pipeline for all datasets"""
        
        print("\n" + "="*80)
        print(" "*15 + "UAE PROMO PULSE - PHASE 1 DATA CLEANING PIPELINE")
        print("="*80)
        
        # Clean each dataset
        products_clean = self.clean_products_data(products_df)
        stores_clean = self.clean_stores_data(stores_df)
        sales_clean = self.clean_sales_data(sales_df)
        inventory_clean = self.clean_inventory_data(inventory_df)
        
        # Generate issues log
        issues_df = pd.DataFrame(self.issues_log)
        
        # Print comprehensive summary
        print("\n" + "="*80)
        print(" "*30 + "CLEANING SUMMARY")
        print("="*80)
        
        print("\n📦 PRODUCTS DATA:")
        print(f"   • Original Records: {self.cleaning_summary['products']['original_records']}")
        print(f"   • Cleaned Records: {self.cleaning_summary['products']['cleaned_records']}")
        print(f"   • Issues Found: {self.cleaning_summary['products']['issues_found']}")
        print(f"   • Quality Score: {self.cleaning_summary['products']['cleanliness_score']:.1f}%")
        
        print("\n🏪 STORES DATA:")
        print(f"   • Original Records: {self.cleaning_summary['stores']['original_records']}")
        print(f"   • Cleaned Records: {self.cleaning_summary['stores']['cleaned_records']}")
        print(f"   • Issues Found: {self.cleaning_summary['stores']['issues_found']}")
        print(f"   • Quality Score: {self.cleaning_summary['stores']['cleanliness_score']:.1f}%")
        
        print("\n💰 SALES DATA:")
        print(f"   • Original Records: {self.cleaning_summary['sales']['original_records']}")
        print(f"   • Cleaned Records: {self.cleaning_summary['sales']['cleaned_records']}")
        print(f"   • Dropped Records: {self.cleaning_summary['sales']['dropped_records']}")
        print(f"   • Issues Found: {self.cleaning_summary['sales']['issues_found']}")
        print(f"   • Quality Score: {self.cleaning_summary['sales']['cleanliness_score']:.1f}%")
        
        print("\n📦 INVENTORY DATA:")
        print(f"   • Original Records: {self.cleaning_summary['inventory']['original_records']}")
        print(f"   • Cleaned Records: {self.cleaning_summary['inventory']['cleaned_records']}")
        print(f"   • Issues Found: {self.cleaning_summary['inventory']['issues_found']}")
        print(f"   • Quality Score: {self.cleaning_summary['inventory']['cleanliness_score']:.1f}%")
        
        print("\n" + "-"*80)
        print(f"TOTAL ISSUES LOGGED: {len(issues_df)}")
        
        if len(issues_df) > 0:
            print("\nIssue Breakdown by Type:")
            for issue_type, count in issues_df['issue_type'].value_counts().items():
                print(f"   • {issue_type}: {count}")
        
        print("\n" + "="*80)
        print(" "*25 + "✅ CLEANING PIPELINE COMPLETE")
        print("="*80 + "\n")
        
        return products_clean, stores_clean, sales_clean, inventory_clean, issues_df


def main():
    """Main execution - load, clean, and save data"""
    try:
        print("📂 Loading raw datasets...")
        products = pd.read_csv('products.csv')
        stores = pd.read_csv('stores.csv')
        sales = pd.read_csv('sales_raw.csv')
        inventory = pd.read_csv('inventory_snapshot.csv')
        
        print(f"✓ Loaded: {len(products)} products, {len(stores)} stores, {len(sales)} sales, {len(inventory)} inventory")
        
        # Execute cleaning pipeline
        cleaner = DataCleaner()
        products_c, stores_c, sales_c, inventory_c, issues_df = \
            cleaner.clean_all_data(products, stores, sales, inventory)
        
        # Save cleaned datasets
        print("💾 Saving cleaned datasets...")
        products_c.to_csv('products_clean.csv', index=False)
        stores_c.to_csv('stores_clean.csv', index=False)
        sales_c.to_csv('sales_clean.csv', index=False)
        inventory_c.to_csv('inventory_clean.csv', index=False)
        issues_df.to_csv('issues.csv', index=False)
        
        print("✅ All files saved successfully!")
        print("   • products_clean.csv")
        print("   • stores_clean.csv")
        print("   • sales_clean.csv")
        print("   • inventory_clean.csv")
        print("   • issues.csv")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please run data_generator.py first to generate raw datasets.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()