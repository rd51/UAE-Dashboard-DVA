"""
UAE Promo Pulse - Data Validator
Phase 1: Validation Rules, Issues Logging, Cleaning Decisions
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
    
    @staticmethod
    def validate_timestamp(value):
        """Check timestamp is parsable"""
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
        """Check price in reasonable range"""
        try:
            p = float(value)
            if p < ValidationRules.PRICE_MIN or p > ValidationRules.PRICE_MAX:
                return False, f"Outside range [{ValidationRules.PRICE_MIN}, {ValidationRules.PRICE_MAX}]: {p}"
            return True, None
        except:
            return False, f"Not numeric: {value}"
    
    @staticmethod
    def validate_quantity(value):
        """Check quantity in reasonable range"""
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
            return True, None  # Skip if either is missing
    
    @staticmethod
    def validate_stock(value):
        """Check stock is non-negative"""
        try:
            s = float(value)
            if s < 0:
                return False, f"Negative stock: {s}"
            return True, None
        except:
            return False, f"Not numeric: {value}"


class DataValidator:
    """Main validator with comprehensive issue logging"""
    
    def __init__(self):
        self.issues = []
    
    def validate_sales_record(self, record, record_id):
        """Validate single sales record"""
        issues = []
        
        # Timestamp validation
        if 'order_time' in record:
            valid, msg = ValidationRules.validate_timestamp(record['order_time'])
            if not valid:
                issues.append({
                    'issue_type': 'INVALID_TIMESTAMP',
                    'issue_detail': msg,
                    'action_taken': 'DROP'
                })
        
        # Price validation
        if 'selling_price_aed' in record:
            valid, msg = ValidationRules.validate_price(record['selling_price_aed'])
            if not valid:
                issues.append({
                    'issue_type': 'OUTLIER_VALUE',
                    'issue_detail': msg,
                    'action_taken': 'CAP'
                })
        
        # Quantity validation
        if 'qty' in record:
            valid, msg = ValidationRules.validate_quantity(record['qty'])
            if not valid:
                issues.append({
                    'issue_type': 'OUTLIER_VALUE',
                    'issue_detail': msg,
                    'action_taken': 'CAP'
                })
        
        # City validation
        if 'city' in record:
            valid, msg = ValidationRules.validate_city(record['city'])
            if not valid:
                issues.append({
                    'issue_type': 'INVALID_CITY',
                    'issue_detail': msg,
                    'action_taken': 'CORRECT'
                })
        
        # Channel validation
        if 'channel' in record:
            valid, msg = ValidationRules.validate_channel(record['channel'])
            if not valid:
                issues.append({
                    'issue_type': 'INVALID_CHANNEL',
                    'issue_detail': msg,
                    'action_taken': 'CORRECT'
                })
        
        # Payment status validation
        if 'payment_status' in record:
            valid, msg = ValidationRules.validate_payment_status(record['payment_status'])
            if not valid:
                issues.append({
                    'issue_type': 'INVALID_VALUE',
                    'issue_detail': msg,
                    'action_taken': 'CORRECT'
                })
        
        # Cost constraint validation
        if 'unit_cost_aed' in record and 'base_price_aed' in record:
            valid, msg = ValidationRules.validate_cost_constraint(
                record['unit_cost_aed'], 
                record['base_price_aed']
            )
            if not valid:
                issues.append({
                    'issue_type': 'CONSTRAINT_VIOLATION',
                    'issue_detail': msg,
                    'action_taken': 'CAP'
                })
        
        # Missing discount
        if 'discount_pct' not in record or pd.isna(record.get('discount_pct')):
            issues.append({
                'issue_type': 'MISSING_VALUE',
                'issue_detail': 'Missing discount_pct',
                'action_taken': 'IMPUTE'
            })
        
        return issues
    
    def validate_inventory_record(self, record, record_id):
        """Validate inventory record"""
        issues = []
        
        # Stock validation
        if 'stock_on_hand' in record:
            valid, msg = ValidationRules.validate_stock(record['stock_on_hand'])
            if not valid:
                issues.append({
                    'issue_type': 'IMPOSSIBLE_VALUE',
                    'issue_detail': msg,
                    'action_taken': 'CORRECT'
                })
        
        return issues
    
    def validate_products_record(self, record, record_id):
        """Validate product record"""
        issues = []
        
        # Missing unit_cost
        if 'unit_cost_aed' not in record or pd.isna(record.get('unit_cost_aed')):
            issues.append({
                'issue_type': 'MISSING_VALUE',
                'issue_detail': 'Missing unit_cost_aed',
                'action_taken': 'IMPUTE'
            })
        
        # Cost constraint
        if 'unit_cost_aed' in record and 'base_price_aed' in record:
            valid, msg = ValidationRules.validate_cost_constraint(
                record['unit_cost_aed'],
                record['base_price_aed']
            )
            if not valid:
                issues.append({
                    'issue_type': 'CONSTRAINT_VIOLATION',
                    'issue_detail': msg,
                    'action_taken': 'CAP'
                })
        
        return issues
    
    def validate_dataset(self, df, dataset_type='sales'):
        """Validate entire dataset"""
        validation_issues = []
        
        for idx, row in df.iterrows():
            record_id = row.get('order_id') or row.get('product_id') or f'ROW_{idx}'
            
            if dataset_type == 'sales':
                issues = self.validate_sales_record(row.to_dict(), record_id)
            elif dataset_type == 'inventory':
                issues = self.validate_inventory_record(row.to_dict(), record_id)
            elif dataset_type == 'products':
                issues = self.validate_products_record(row.to_dict(), record_id)
            else:
                issues = []
            
            for issue in issues:
                validation_issues.append({
                    'record_identifier': record_id,
                    'issue_type': issue['issue_type'],
                    'issue_detail': issue['issue_detail'],
                    'action_taken': issue['action_taken']
                })
        
        self.issues = validation_issues
        return pd.DataFrame(validation_issues)


class CleaningPolicies:
    """Justified cleaning decisions with policies"""
    
    POLICIES = {
        'INVALID_TIMESTAMP': {
            'action': 'DROP',
            'justification': 'Corrupted timestamps cannot be inferred; data integrity > completeness'
        },
        'OUTLIER_VALUE': {
            'action': 'CAP',
            'justification': 'Cap at percentile bounds (95th percentile) to preserve data while fixing anomalies'
        },
        'MISSING_VALUE': {
            'action': 'IMPUTE',
            'justification': 'discount_pct: set to 0 (no discount); unit_cost: impute as 50% of base_price'
        },
        'INVALID_CITY': {
            'action': 'CORRECT',
            'justification': 'Standardize to valid city names (Dubai default); supports geospatial analysis'
        },
        'INVALID_CHANNEL': {
            'action': 'CORRECT',
            'justification': 'Standardize to valid channel (App default); ensures channel consistency'
        },
        'INVALID_VALUE': {
            'action': 'CORRECT',
            'justification': 'payment_status: default to Paid; preserves transaction data'
        },
        'CONSTRAINT_VIOLATION': {
            'action': 'CAP',
            'justification': 'unit_cost > base_price: cap unit_cost at base_price; maintains margin logic'
        },
        'IMPOSSIBLE_VALUE': {
            'action': 'CORRECT',
            'justification': 'Negative stock: set to 0; stock > 1000: cap at 500 (supply chain bounds)'
        }
    }
    
    @staticmethod
    def get_policy(issue_type):
        """Get cleaning policy for issue type"""
        return CleaningPolicies.POLICIES.get(
            issue_type, 
            {'action': 'SKIP', 'justification': 'No policy defined'}
        )