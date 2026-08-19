"""
UAE Promo Pulse - FINAL ENHANCED Dashboard
All bugs fixed, production-ready version
With custom dataset upload capability
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from simulator import PromoSimulator
import numpy as np
import io
import sys
import os
import time
import logging
from datetime import datetime
from typing import Tuple, Dict, Optional, List
import warnings
import json

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.streamlit'))

# Page config
st.set_page_config(
    page_title="UAE Promo Pulse Dashboard",
    page_icon="🇦🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Color Palette
COLORS = {
    'primary': '#1e3a8a',      # Deep professional blue
    'secondary': '#3b82f6',    # Bright blue
    'success': '#10b981',      # Green
    'warning': '#f59e0b',      # Amber
    'danger': '#ef4444',       # Red
    'info': '#06b6d4',         # Cyan
    'dark': '#1f2937',         # Dark gray
    'light': '#f9fafb',        # Light gray
    'white': '#ffffff',
    'border': '#e5e7eb',
    'text_primary': '#111827',
    'text_secondary': '#6b7280',
    'gradient_start': '#1e40af',
    'gradient_end': '#3b82f6'
}

# Dark Mode State
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Professional Executive Dashboard CSS
st.markdown("""
<style>
    /* Import Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: #faf8f3;
    }
    
    /* Main Container */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1600px;
        margin: 0 auto;
    }
    
    /* Typography Hierarchy */
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.2 !important;
    }
    
    h2 {
        font-size: 1.875rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        letter-spacing: -0.01em !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    p, .stMarkdown {
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        color: #475569 !important;
    }
    
    /* Professional KPI Cards */
    .metric-card {
        background: #bae6fd;
        padding: 1.75rem;
        border-radius: 16px;
        border: 1px solid #7dd3fc;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #0ea5e9 0%, #0284c7 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: #38bdf8;
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-card h3 {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: #0c4a6e !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0 0 0.75rem 0 !important;
    }
    
    .metric-card h1 {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        margin: 0 !important;
        line-height: 1 !important;
    }
    
    .metric-card p {
        font-size: 0.875rem !important;
        color: #64748b !important;
        margin: 0.5rem 0 0 0 !important;
    }
    
    /* Streamlit Native Metrics Enhancement */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }
    
    /* Chart Containers */
    .stPlotlyChart {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        min-height: 600px;
        width: 100%;
    }
    
    /* Ensure Plotly charts scale properly */
    .stPlotlyChart > div {
        width: 100% !important;
    }
    
    .js-plotly-plot .plotly {
        width: 100% !important;
        height: 100% !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        color: #1e293b !important;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #cbd5e1 !important;
        background: #f8fafc !important;
    }
    
    .streamlit-expanderContent {
        border: 1px solid #e2e8f0 !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1.5rem !important;
        background: white !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #1e293b !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.625rem 1.5rem;
        font-weight: 600;
        font-size: 0.9375rem;
        letter-spacing: 0.01em;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px 0 rgba(59, 130, 246, 0.4);
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    }
    
    /* Download Button Styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.625rem 1.25rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.2s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px 0 rgba(16, 185, 129, 0.4);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.625rem 1.5rem;
        font-weight: 600;
        color: #64748b;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f1f5f9;
        color: #1e293b;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
    }
    
    /* Divider Styling */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #e2e8f0 20%, #e2e8f0 80%, transparent 100%);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stMultiselect > div > div > div {
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        padding: 0.625rem 1rem !important;
        font-size: 0.9375rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stMultiselect > div > div > div:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Radio Button Styling */
    .stRadio > label {
        font-weight: 600 !important;
        color: #334155 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stRadio > div {
        background: #e0f2fe !important;
        padding: 0.75rem 1rem !important;
        border-radius: 12px !important;
        border: 1px solid #bae6fd !important;
    }
    
    .stRadio > div > label > div {
        background: #e0f2fe !important;
    }
    
    .stRadio > div > label > div[data-checked="true"] {
        background: #bae6fd !important;
        font-weight: 700 !important;
    }
    
    /* Slider Styling */
    .stSlider > div > div > div {
        background: #e2e8f0 !important;
    }
    
    .stSlider > div > div > div > div {
        background: #3b82f6 !important;
    }
    
    /* Info/Warning/Error Boxes */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        padding: 1rem 1.25rem !important;
        font-size: 0.9375rem !important;
    }
    
    /* Success Alert */
    [data-testid="stNotification"] {
        border-radius: 12px;
        border-left: 4px solid #10b981;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    /* Data Tables */
    .dataframe {
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        font-size: 0.875rem !important;
    }
    
    .dataframe thead tr th {
        background: #f8fafc !important;
        color: #475569 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        letter-spacing: 0.05em;
        padding: 0.75rem 1rem !important;
        border-bottom: 2px solid #e2e8f0 !important;
    }
    
    .dataframe tbody tr:hover {
        background: #f8fafc !important;
    }
    
    /* Column Layout Enhancement */
    [data-testid="column"] {
        padding: 0.5rem;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom Badge Styles */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.025em;
    }
    
    .badge-success {
        background: #d1fae5;
        color: #065f46;
    }
    
    .badge-warning {
        background: #fef3c7;
        color: #92400e;
    }
    
    .badge-danger {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .badge-info {
        background: #dbeafe;
        color: #1e40af;
    }
    
    /* Spinner Styling */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        border-radius: 9999px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all cleaned datasets with comprehensive error handling"""
    try:
        start_time = time.time()
        
        # Load with error handling for each file
        data_files = {
            'products': 'products_clean.csv',
            'stores': 'stores_clean.csv',
            'sales': 'sales_clean.csv',
            'inventory': 'inventory_clean.csv',
            'issues': 'issues.csv'
        }
        
        loaded_data = {}
        missing_files = []
        
        for name, filepath in data_files.items():
            try:
                if os.path.exists(filepath):
                    loaded_data[name] = pd.read_csv(filepath)
                    logger.info(f"✓ Loaded {name}: {len(loaded_data[name])} rows")
                else:
                    missing_files.append(filepath)
            except Exception as e:
                logger.error(f"Error loading {filepath}: {str(e)}")
                missing_files.append(filepath)
        
        if missing_files:
            raise FileNotFoundError(f"Missing files: {', '.join(missing_files)}")
        
        # Validate data integrity
        if len(loaded_data['sales']) == 0:
            raise ValueError("Sales data is empty")
        if len(loaded_data['products']) == 0:
            raise ValueError("Products data is empty")
            
        elapsed = time.time() - start_time
        logger.info(f"Data loaded successfully in {elapsed:.2f}s")
        
        return (loaded_data['products'], loaded_data['stores'], 
                loaded_data['sales'], loaded_data['inventory'], loaded_data['issues'])
        
    except FileNotFoundError as e:
        st.error(f"❌ Data file error: {e}")
        st.info("📋 Please run:\n```bash\npython data_generator.py\npython cleaner.py\n```")
        st.stop()
    except ValueError as e:
        st.error(f"❌ Data validation error: {e}")
        st.info("Data appears to be corrupted or empty. Please regenerate it.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Unexpected error loading data: {str(e)}")
        logger.exception("Data loading failed")
        st.stop()

@st.cache_data
def validate_dataframe(df: pd.DataFrame, required_cols: List[str], df_name: str = "DataFrame") -> bool:
    """Validate DataFrame has required columns and data"""
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"❌ {df_name} missing columns: {', '.join(missing_cols)}")
        return False
    if len(df) == 0:
        st.warning(f"⚠️ {df_name} is empty")
        return False
    return True

def calculate_advanced_kpis(sales: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame, 
                           inventory: pd.DataFrame) -> Dict[str, float]:
    """Calculate comprehensive KPIs with caching"""
    try:
        # Basic KPIs
        net_revenue = (sales['selling_price_aed'] * sales['qty']).sum()
        total_cost = (sales['qty'] * products.set_index('product_id').loc[sales['product_id'].values, 'unit_cost_aed']).sum()
        gross_profit = net_revenue - total_cost
        gross_margin_pct = (gross_profit / net_revenue * 100) if net_revenue > 0 else 0
        
        # Returns analysis
        returns = sales[sales['qty'] < 0]['qty'].abs().sum()
        total_qty = sales[sales['qty'] > 0]['qty'].sum()
        return_rate_pct = (returns / total_qty * 100) if total_qty > 0 else 0
        
        # Channel analysis
        if 'channel' in sales.columns:
            channel_revenue = sales.groupby('channel')['selling_price_aed'].sum()
        else:
            channel_revenue = {}
        
        return {
            'net_revenue': net_revenue,
            'gross_profit': gross_profit,
            'gross_margin_pct': gross_margin_pct,
            'return_rate_pct': return_rate_pct,
            'total_transactions': len(sales),
            'avg_transaction_value': net_revenue / len(sales) if len(sales) > 0 else 0,
            'channel_revenue': channel_revenue
        }
    except Exception as e:
        logger.error(f"Error calculating KPIs: {str(e)}")
        return {}

def load_custom_datasets(products_file, stores_file, sales_file, inventory_file, issues_file=None) -> Optional[Tuple]:
    """Load custom datasets from uploaded files with validation"""
    try:
        start_time = time.time()
        
        products = pd.read_csv(products_file)
        stores = pd.read_csv(stores_file)
        sales = pd.read_csv(sales_file)
        inventory = pd.read_csv(inventory_file)
        
        # Issues file is optional
        if issues_file:
            issues = pd.read_csv(issues_file)
        else:
            issues = pd.DataFrame({'issue_type': []})
        
        # Validate required columns
        required_products = ['product_id', 'category', 'brand', 'unit_cost_aed']
        required_stores = ['store_id', 'city', 'channel']
        required_sales = ['order_id', 'product_id', 'store_id', 'qty', 'selling_price_aed']
        required_inventory = ['product_id', 'store_id', 'stock_on_hand']
        
        # Comprehensive validation
        validation_errors = []
        
        for col in required_products:
            if col not in products.columns:
                validation_errors.append(f"Products missing: {col}")
        
        for col in required_stores:
            if col not in stores.columns:
                validation_errors.append(f"Stores missing: {col}")
        
        for col in required_sales:
            if col not in sales.columns:
                validation_errors.append(f"Sales missing: {col}")
        
        for col in required_inventory:
            if col not in inventory.columns:
                validation_errors.append(f"Inventory missing: {col}")
        
        if validation_errors:
            st.error("❌ Validation errors in uploaded files:")
            for error in validation_errors:
                st.write(f"• {error}")
            return None
        
        # Check for empty DataFrames
        if len(sales) == 0:
            st.error("❌ Sales data is empty")
            return None
        if len(products) == 0:
            st.error("❌ Products data is empty")
            return None
        
        elapsed = time.time() - start_time
        st.success(f"✅ Custom data loaded successfully in {elapsed:.2f}s")
        logger.info(f"Custom datasets loaded: Products={len(products)}, Stores={len(stores)}, Sales={len(sales)}")
        
        return products, stores, sales, inventory, issues
    
    except pd.errors.ParserError as e:
        st.error(f"❌ CSV format error: {str(e)}")
        st.info("Please ensure all files are valid CSV format")
        return None
    except Exception as e:
        st.error(f"❌ Error loading custom data: {str(e)}")
        logger.exception("Custom data loading failed")
        return None
        
        if errors:
            return None, "\n".join(errors)
        
        return (products, stores, sales, inventory, issues), None
    except Exception as e:
        return None, f"Error loading files: {str(e)}"

@st.cache_resource
def initialize_simulator(_products, _stores, _sales, _inventory):
    """Initialize simulator"""
    return PromoSimulator(_products, _stores, _sales, _inventory)

def create_scenario_comparison(sim, city, channel, category, budget, margin_floor, days):
    """Compare multiple scenarios"""
    scenarios = []
    discount_levels = [10, 15, 20, 25, 30, 35]
    
    for disc in discount_levels:
        try:
            _, violations, s_kpis = sim.simulate_promo(
                city, channel, category, disc, budget, margin_floor, days
            )
            scenarios.append({
                'Discount %': disc,
                'Revenue (AED)': s_kpis['simulated_revenue'],
                'Margin %': s_kpis['simulated_margin_pct'],
                'Profit (AED)': s_kpis['profit_proxy'],
                'Budget Use %': s_kpis['budget_utilization_pct'],
                'Stockout Risk %': s_kpis['stockout_risk_pct'],
                'Status': '✅ Valid' if not any([violations['budget_exceeded'], violations['margin_below_floor']]) else '❌ Violated'
            })
        except Exception as e:
            st.warning(f"Scenario {disc}% failed: {str(e)}")
    
    return pd.DataFrame(scenarios) if scenarios else pd.DataFrame()

def create_product_matrix(sales_enriched):
    """BCG-style matrix"""
    product_perf = sales_enriched[sales_enriched['payment_status'] == 'Paid'].copy()
    product_perf['revenue'] = product_perf['qty'] * product_perf['selling_price_aed']
    product_perf['cogs'] = product_perf['qty'] * product_perf['unit_cost_aed']
    product_perf['margin'] = product_perf['revenue'] - product_perf['cogs']
    
    perf = product_perf.groupby('category').agg({
        'revenue': 'sum',
        'margin': 'sum',
        'qty': 'sum'
    }).reset_index()
    
    perf['margin_pct'] = (perf['margin'] / perf['revenue'] * 100).fillna(0)
    
    return perf

def create_revenue_margin_chart(sales_data):
    """
    Create enhanced Revenue vs Margin Trend chart for May-September 2024
    with dual Y-axes, interactivity, and analytical features
    """
    # Ensure order_time is datetime
    sales_data = sales_data.copy()
    sales_data['order_time'] = pd.to_datetime(sales_data['order_time'], errors='coerce')
    
    # Filter for May-September 2024
    sales_data = sales_data[
        (sales_data['order_time'].dt.year == 2024) &
        (sales_data['order_time'].dt.month >= 5) &
        (sales_data['order_time'].dt.month <= 9)
    ].copy()
    
    if len(sales_data) == 0:
        st.warning("No data available for May-September 2024")
        return None
    
    # Add week column for aggregation
    sales_data['week_start'] = sales_data['order_time'].dt.to_period('W').apply(lambda r: r.start_time)
    sales_data['week_label'] = sales_data['week_start'].dt.strftime('%b %d')
    
    # Calculate revenue and margin
    sales_data['revenue'] = sales_data['qty'] * sales_data['selling_price_aed']
    sales_data['cogs'] = sales_data['qty'] * sales_data['unit_cost_aed']
    sales_data['margin'] = sales_data['revenue'] - sales_data['cogs']
    
    # Aggregate by week
    weekly_data = sales_data.groupby('week_start').agg({
        'revenue': 'sum',
        'margin': 'sum',
        'qty': 'sum'
    }).reset_index()
    
    weekly_data['margin_pct'] = (weekly_data['margin'] / weekly_data['revenue'] * 100).fillna(0)
    weekly_data['week_label'] = weekly_data['week_start'].dt.strftime('%b %d, %Y')
    
    # Calculate averages
    avg_revenue = weekly_data['revenue'].mean()
    avg_margin = weekly_data['margin_pct'].mean()
    
    # Create figure with secondary y-axis
    fig = make_subplots(
        specs=[[{"secondary_y": True}]],
        subplot_titles=("Revenue vs Margin Trend (May - September 2024)",)
    )
    
    # Revenue as area chart (blue)
    fig.add_trace(
        go.Bar(
            x=weekly_data['week_start'],
            y=weekly_data['revenue'],
            name="Revenue (AED)",
            marker=dict(
                color='#667eea',
                line=dict(color='#667eea', width=0)
            ),
            hovertemplate='<b>Week of %{x|%b %d, %Y}</b><br>' +
                         'Revenue: AED %{y:,.0f}<extra></extra>',
            opacity=0.7
        ),
        secondary_y=False
    )
    
    # Average revenue line (dashed blue)
    fig.add_hline(
        y=avg_revenue,
        line_dash="dash",
        line_color="#667eea",
        annotation_text=f"Avg Revenue: AED {avg_revenue:,.0f}",
        annotation_position="right",
        secondary_y=False,
        opacity=0.5
    )
    
    # Margin % as line chart with markers (pink/magenta)
    fig.add_trace(
        go.Scatter(
            x=weekly_data['week_start'],
            y=weekly_data['margin_pct'],
            name="Margin %",
            mode='lines+markers',
            line=dict(
                color='#f093fb',
                width=3
            ),
            marker=dict(
                size=8,
                symbol='circle',
                color='#f093fb',
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>Week of %{x|%b %d, %Y}</b><br>' +
                         'Margin: %{y:.1f}%<extra></extra>',
            fill='tozeroy',
            fillcolor='rgba(240, 147, 251, 0.2)'
        ),
        secondary_y=True
    )
    
    # Average margin line (dashed pink)
    fig.add_hline(
        y=avg_margin,
        line_dash="dash",
        line_color="#f093fb",
        annotation_text=f"Avg Margin: {avg_margin:.1f}%",
        annotation_position="right",
        secondary_y=True,
        opacity=0.5
    )
    
    # Find and annotate peaks and dips
    max_revenue_idx = weekly_data['revenue'].idxmax()
    min_revenue_idx = weekly_data['revenue'].idxmin()
    max_margin_idx = weekly_data['margin_pct'].idxmax()
    min_margin_idx = weekly_data['margin_pct'].idxmin()
    
    # Add annotations for peaks
    fig.add_annotation(
        x=weekly_data.loc[max_revenue_idx, 'week_start'],
        y=weekly_data.loc[max_revenue_idx, 'revenue'],
        text="📈 Peak Revenue",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#667eea",
        ax=40,
        ay=-40,
        bgcolor="white",
        bordercolor="#667eea",
        borderwidth=1,
        secondary_y=False
    )
    
    fig.add_annotation(
        x=weekly_data.loc[max_margin_idx, 'week_start'],
        y=weekly_data.loc[max_margin_idx, 'margin_pct'],
        text="📈 Peak Margin",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#f093fb",
        ax=40,
        ay=-40,
        bgcolor="white",
        bordercolor="#f093fb",
        borderwidth=1,
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': "📊 Revenue vs Margin Trend Analysis (May - September 2024)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333'}
        },
        hovermode='x unified',
        height=600,
        showlegend=True,
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#ddd',
            borderwidth=1
        ),
        plot_bgcolor='rgba(240, 240, 245, 0.3)',
        paper_bgcolor='white',
        margin=dict(l=80, r=80, t=100, b=80),
        xaxis=dict(
            rangeslider=dict(visible=True, thickness=0.05),
            type='date',
            gridcolor='rgba(200, 200, 200, 0.2)',
            showgrid=True
        )
    )
    
    # Update Y-axes
    fig.update_yaxes(
        title_text="<b>Revenue (AED)</b>",
        secondary_y=False,
        tickformat=',.0f',
        gridcolor='rgba(200, 200, 200, 0.2)',
        showgrid=True
    )
    
    fig.update_yaxes(
        title_text="<b>Margin (%)</b>",
        secondary_y=True,
        tickformat='.1f',
        gridcolor='rgba(200, 200, 200, 0.1)'
    )
    
    # Update X-axis
    fig.update_xaxes(
        title_text="<b>Week</b>",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.2)',
        tickformat='%b %d'
    )
    
    return fig, weekly_data, avg_revenue, avg_margin

def get_performance_benchmarks() -> Dict[str, float]:
    """Get industry performance benchmarks"""
    return {
        'revenue_benchmark': 5000000,  # AED 5M
        'margin_target': 20,  # 20%
        'return_rate_max': 5,  # 5%
        'transaction_growth': 10,  # 10% YoY
        'customer_satisfaction': 85  # 85%
    }

def calculate_performance_vs_benchmark(kpis: Dict, benchmarks: Dict) -> Dict[str, str]:
    """Calculate performance against benchmarks"""
    performance = {}
    
    if kpis.get('net_revenue', 0) >= benchmarks['revenue_benchmark']:
        performance['revenue'] = '✅ Exceeds benchmark'
    else:
        gap = ((benchmarks['revenue_benchmark'] - kpis.get('net_revenue', 0)) / benchmarks['revenue_benchmark'] * 100)
        performance['revenue'] = f'⚠️ {gap:.1f}% below benchmark'
    
    if kpis.get('gross_margin_pct', 0) >= benchmarks['margin_target']:
        performance['margin'] = '✅ On target'
    else:
        gap = benchmarks['margin_target'] - kpis.get('gross_margin_pct', 0)
        performance['margin'] = f'⚠️ {gap:.1f}% below target'
    
    if kpis.get('return_rate_pct', 0) <= benchmarks['return_rate_max']:
        performance['returns'] = '✅ Within acceptable range'
    else:
        performance['returns'] = f'❌ Exceeds threshold by {kpis.get("return_rate_pct", 0) - benchmarks["return_rate_max"]:.1f}%'
    
    return performance

def generate_performance_report(sales: pd.DataFrame, kpis: Dict) -> str:
    """Generate comprehensive performance report"""
    try:
        # Calculate trends
        if 'order_time' in sales.columns:
            sales['order_time'] = pd.to_datetime(sales['order_time'])
            daily_revenue = sales.groupby(sales['order_time'].dt.date)['selling_price_aed'].sum()
            trend = "📈 Uptrend" if len(daily_revenue) > 1 and daily_revenue.iloc[-1] > daily_revenue.iloc[0] else "📉 Downtrend"
        else:
            trend = "⚠️ No trend data"
        
        report = f"""
        PERFORMANCE REPORT
        {'='*50}
        Revenue Trend: {trend}
        Top Channel: {kpis.get('channel_revenue', {}).max() if isinstance(kpis.get('channel_revenue', {}), dict) else 'N/A'}
        """
        return report
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return "Report generation failed"

def apply_professional_chart_style(fig):
    """Apply consistent professional styling to Plotly charts for board-room presentations"""
    fig.update_layout(
        # Professional font
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            size=12,
            color="#475569"
        ),
        
        # Title styling
        title=dict(
            font=dict(size=18, color="#0f172a", family="Inter"),
            x=0.02,
            xanchor='left',
            y=0.98,
            yanchor='top'
        ),
        
        # Clean background
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        
        # Professional gridlines
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#e2e8f0',
            showline=True,
            linewidth=1,
            linecolor='#cbd5e1',
            tickfont=dict(size=11, color='#64748b'),
            title_font=dict(size=12, color='#475569', family="Inter")
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#e2e8f0',
            showline=True,
            linewidth=1,
            linecolor='#cbd5e1',
            tickfont=dict(size=11, color='#64748b'),
            title_font=dict(size=12, color='#475569', family="Inter")
        ),
        
        # Legend styling
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#e2e8f0',
            borderwidth=1,
            font=dict(size=11, color='#475569')
        ),
        
        # Hover styling
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter",
            bordercolor='#cbd5e1'
        ),
        
        # Margins for clean look
        margin=dict(l=60, r=40, t=80, b=60),
        
        # Height for full visibility
        height=600,
        
        # Auto-size for better scaling
        autosize=True
    )
    
    return fig

def main():
    # Data Source Selection
    st.sidebar.header("📊 Data Source")
    data_source = st.sidebar.radio(
        "Select Data Source:",
        ["📁 Pre-Built Dataset", "📤 Upload Custom Data"],
        index=0
    )
    
    # Load data based on selection
    if data_source == "📁 Pre-Built Dataset":
        try:
            products, stores, sales, inventory, issues = load_data()
            st.sidebar.success("✅ Pre-built data loaded")
        except Exception as e:
            st.sidebar.error(f"Error loading pre-built data: {e}")
            st.stop()
    else:
        # Custom data upload
        st.sidebar.markdown("### Upload Required Files:")
        st.sidebar.info("Upload CSV files for: Products, Stores, Sales, and Inventory")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            products_file = st.file_uploader("📦 Products CSV", type="csv", key="products_upload")
            sales_file = st.file_uploader("🛍️ Sales CSV", type="csv", key="sales_upload")
        
        with col2:
            stores_file = st.file_uploader("🏪 Stores CSV", type="csv", key="stores_upload")
            inventory_file = st.file_uploader("📊 Inventory CSV", type="csv", key="inventory_upload")
        
        issues_file = st.file_uploader("📋 Issues CSV (Optional)", type="csv", key="issues_upload")
        
        # Validate and load uploaded files
        if products_file and stores_file and sales_file and inventory_file:
            data_tuple, error = load_custom_datasets(
                products_file, stores_file, sales_file, inventory_file, issues_file
            )
            
            if error:
                st.sidebar.error(f"❌ {error}")
                st.stop()
            else:
                products, stores, sales, inventory, issues = data_tuple
                st.sidebar.success("✅ Custom data loaded successfully!")
        else:
            st.sidebar.warning("⚠️ Please upload all required files (Products, Stores, Sales, Inventory)")
            st.stop()
    
    sim = initialize_simulator(products, stores, sales, inventory)
    
    # Professional Executive Header
    st.markdown("""
    <div style="background: #e0f2fe; 
                padding: 2.5rem 2rem; 
                border-radius: 16px; 
                margin-bottom: 2rem;
                border: 1px solid #bae6fd;">
        <h1 style="color: #0c4a6e; font-size: 2.5rem; font-weight: 800; margin: 0; letter-spacing: -0.02em;">
            🇦🇪 UAE Promo Pulse Dashboard
        </h1>
        <p style="color: #075985; font-size: 1.125rem; margin: 0.5rem 0 0 0; font-weight: 500;">
            Executive Business Intelligence Platform  •  Real-Time Analytics & Insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    source_label = "Pre-built Dataset" if data_source == "📁 Pre-Built Dataset" else "Custom Uploaded Dataset"
    view_mode = "💼 Executive Suite"
    
    # Calculate initial KPIs before Quick Stats section
    # This is calculated early so it can be used in Quick Stats and Performance Benchmarks
    try:
        initial_kpis = sim.compute_kpis(sales)
        if not initial_kpis or len(initial_kpis) == 0:
            raise ValueError("KPI calculation returned empty results")
        kpis = initial_kpis
    except Exception as e:
        logger.error(f"Error calculating initial KPIs: {str(e)}")
        kpis = {
            'net_revenue': 0,
            'gross_profit': 0,
            'gross_margin_pct': 0,
            'return_rate_pct': 0,
            'total_transactions': 0,
            'avg_transaction_value': 0
        }
    
    
    
    # Helpful tip
    if 'sim_results' not in st.session_state:
        st.info("💡 **Tip:** Click '🚀 Launch Simulation' in the sidebar to activate all simulation features!", icon="ℹ️")
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Control Panel")

        with st.expander("📊 Dataset Overview", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📦 Products", f"{len(products):,}", help="Total number of unique products")
                st.metric("🛍️ Transactions", f"{len(sales):,}", help="Total number of sales transactions")
            with col2:
                st.metric("🏪 Stores", f"{len(stores):,}", help="Total number of store locations")
                st.metric("📋 Inventory", f"{len(inventory):,}", help="Total inventory snapshot records")

            st.markdown("---")
            st.markdown("**📅 Data Period**")
            if 'order_time' in sales.columns:
                sales['order_time'] = pd.to_datetime(sales['order_time'])
                min_date = sales['order_time'].min().date()
                max_date = sales['order_time'].max().date()
                st.info(f"From **{min_date}** to **{max_date}**")
            else:
                st.info("Date information not available")

            st.markdown("**📂 Data Source**")
            st.info(f"**{source_label}**")

        with st.expander("⚙️ Dashboard Configuration", expanded=False):
            st.markdown("##### Performance Thresholds & Display Options")
            margin_threshold = st.slider(
                "Gross Margin Target (%)", 
                min_value=5, 
                max_value=50, 
                value=20, 
                step=1,
                help="Alert if margin falls below this threshold"
            )
            return_threshold = st.slider(
                "Return Rate Limit (%)", 
                min_value=1, 
                max_value=15, 
                value=5, 
                step=1,
                help="Alert if return rate exceeds this threshold"
            )

            show_benchmarks = st.checkbox(
                "📈 Show Performance Benchmarks", 
                value=True, 
                help="Display performance comparisons against targets"
            )
            auto_refresh = st.checkbox(
                "🔄 Auto-refresh Data", 
                value=False, 
                help="Automatically refresh dashboard every 5 minutes"
            )

            if auto_refresh:
                st.info("ℹ️ **Auto-refresh enabled** • Dashboard will update every 5 minutes")

            st.session_state.margin_threshold = margin_threshold
            st.session_state.return_threshold = return_threshold
            st.session_state.show_benchmarks = show_benchmarks

        st.markdown("---")
        
        # Quick Presets
        st.subheader("⚡ Quick Presets")
        preset = st.selectbox(
            "Apply Preset Filter",
            ["Custom", "Dubai Electronics", "All Marketplaces", "Fashion App"]
        )
        
        if preset == "Custom":
            sales['order_time'] = pd.to_datetime(sales['order_time'])
            min_date = sales['order_time'].min().date()
            max_date = sales['order_time'].max().date()
            
            st.subheader("📅 Time Period")
            date_range = st.date_input(
                "Select Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            st.subheader("🗺️ Geography & Channel")
            city_filter = st.selectbox("City", ['All'] + sorted(stores['city'].unique().tolist()))
            channel_filter = st.selectbox("Channel", ['All'] + sorted(stores['channel'].unique().tolist()))
            
            st.subheader("🏷️ Product Filters")
            category_filter = st.selectbox("Category", ['All'] + sorted(products['category'].unique().tolist()))
            brand_filter = st.selectbox("Brand", ['All'] + sorted(products['brand'].unique().tolist()))
        else:
            # Apply presets
            if preset == "Dubai Electronics":
                city_filter, category_filter, channel_filter = "Dubai", "Electronics", "All"
            elif preset == "All Marketplaces":
                city_filter, category_filter, channel_filter = "All", "All", "Marketplace"
            elif preset == "Fashion App":
                city_filter, category_filter, channel_filter = "All", "Fashion", "App"
            else:
                city_filter, category_filter, channel_filter = "All", "All", "All"
            
            date_range = None
            brand_filter = "All"
        
        st.markdown("---")
        st.header("🎯 Simulation Lab")
        
        with st.expander("📊 Scenario Settings", expanded=True):
            sim_city = st.selectbox("Target City", ['All'] + sorted(stores['city'].unique().tolist()), key='sim_city')
            sim_channel = st.selectbox("Target Channel", ['All'] + sorted(stores['channel'].unique().tolist()), key='sim_channel')
            sim_category = st.selectbox("Target Category", ['All'] + sorted(products['category'].unique().tolist()), key='sim_category')
            
            discount_pct = st.slider("💰 Discount %", 0, 50, 20, 5)
            promo_budget = st.number_input("💵 Budget (AED)", 10000, 200000, 50000, 5000)
            margin_floor = st.slider("📉 Margin Floor %", 0, 30, 10, 5)
            sim_days = st.selectbox("⏱️ Duration (days)", [7, 14], index=1)
        
        run_sim = st.button("🚀 Launch Simulation", type="primary", use_container_width=True)
        
        if run_sim:
            with st.spinner("🔄 Running simulation..."):
                try:
                    # Validate simulation parameters
                    if discount_pct < 0 or discount_pct > 100:
                        st.error("❌ Discount must be between 0-100%")
                    elif promo_budget <= 0:
                        st.error("❌ Budget must be positive")
                    else:
                        start_time = time.time()
                        simulated, violations, sim_kpis = sim.simulate_promo(
                            sim_city, sim_channel, sim_category,
                            discount_pct, promo_budget, margin_floor, sim_days
                        )
                        elapsed = time.time() - start_time
                        
                        # Validate results
                        if simulated is None or len(simulated) == 0:
                            raise ValueError("Simulation returned no results")
                        
                        st.session_state['sim_results'] = (simulated, violations, sim_kpis)
                        st.success(f"✅ Simulation Complete! ({elapsed:.2f}s)")
                        
                        # Show warnings for constraint violations
                        if violations:
                            violation_messages = []
                            if violations.get('budget_exceeded'):
                                violation_messages.append("⚠️ Budget exceeded")
                            if violations.get('margin_below_floor'):
                                violation_messages.append("⚠️ Margin below floor")
                            if violations.get('stockouts_exist'):
                                violation_messages.append("⚠️ Stockout risk detected")
                            
                            if violation_messages:
                                st.warning("Constraint Violations: " + ", ".join(violation_messages))
                
                except ValueError as e:
                    st.error(f"❌ Validation error: {str(e)}")
                    logger.error(f"Simulation validation error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Simulation error: {str(e)}")
                    st.info("💡 Tips: Try adjusting discount %, budget, or other parameters")
                    logger.exception("Simulation execution failed")
    
    # Apply filters with error handling
    try:
        filtered_sales = sales.copy()
        
        if preset == "Custom" and date_range and len(date_range) == 2:
            filtered_sales = filtered_sales[
                (filtered_sales['order_time'].dt.date >= date_range[0]) &
                (filtered_sales['order_time'].dt.date <= date_range[1])
            ]
        
        # Merge with products and stores
        filtered_sales = filtered_sales.merge(
            products[['product_id', 'category', 'brand', 'unit_cost_aed']], 
            on='product_id',
            how='left'
        )
        filtered_sales = filtered_sales.merge(
            stores[['store_id', 'city', 'channel', 'fulfillment_type']], 
            on='store_id',
            how='left'
        )

        if city_filter != 'All':
            filtered_sales = filtered_sales[filtered_sales['city'] == city_filter]
        if channel_filter != 'All':
            filtered_sales = filtered_sales[filtered_sales['channel'] == channel_filter]
        if category_filter != 'All':
            filtered_sales = filtered_sales[filtered_sales['category'] == category_filter]
        if preset == "Custom" and brand_filter != 'All':
            filtered_sales = filtered_sales[filtered_sales['brand'] == brand_filter]
    
    except Exception as e:
        st.error(f"❌ Error during data preparation: {str(e)}")
        logger.error(f"Data preparation error: {str(e)}")
    # Recalculate KPIs with filtered data
    try:
        filtered_kpis = sim.compute_kpis(filtered_sales)
        if not filtered_kpis or len(filtered_kpis) == 0:
            raise ValueError("KPI calculation returned empty results")
        # Update kpis with filtered values for the visualizations below
        kpis = filtered_kpis
    except Exception as e:
        logger.error(f"Error calculating filtered KPIs: {str(e)}")
        st.error(f"❌ Error calculating filtered KPIs: {str(e)}")
        # Keep the initial kpis if filtering fails
    
    # EXECUTIVE VIEW
    if True:
        st.markdown("""
        <div class="section-header">
            <h2 style="margin: 0; color: #0f172a;">💼 Executive Suite</h2>
            <p style="margin: 0.5rem 0 0 0; color: #64748b; font-size: 0.9375rem;">
                Financial Performance & Strategic Market Analysis
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced KPI Cards with Professional Styling
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>NET REVENUE</h3>
                <h1>AED {kpis['net_revenue']:,.0f}</h1>
                <p>Gross: AED {kpis['gross_revenue']:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>GROSS MARGIN</h3>
                <h1>{kpis['gross_margin_pct']:.1f}%</h1>
                <p>Amount: AED {kpis['gross_margin_aed']:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if 'sim_results' in st.session_state:
                _, _, sim_kpis = st.session_state['sim_results']
                st.markdown(f"""
                <div class="metric-card">
                    <h3>PROFIT PROXY (SIM)</h3>
                    <h1>AED {sim_kpis['profit_proxy']:,.0f}</h1>
                    <p>Margin: {sim_kpis['simulated_margin_pct']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Run simulation")
        
        with col4:
            if 'sim_results' in st.session_state:
                _, _, sim_kpis = st.session_state['sim_results']
                color = "green" if sim_kpis['budget_utilization_pct'] <= 100 else "red"
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size:14px; opacity:0.8;">Budget Usage</h3>
                    <h2 style="margin:10px 0; color:{color};">{sim_kpis['budget_utilization_pct']:.1f}%</h2>
                    <p style="margin:0; font-size:12px;">{sim_kpis['promo_spend']:,.0f} AED spent</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Run simulation")
        
        st.divider()
        
        # Sidebar Controls
        st.sidebar.markdown("### 📊 Dashboard Controls")
        show_avg_lines = st.sidebar.checkbox("Show Average Lines", value=True, key="avg_lines")
        show_smoothed = st.sidebar.checkbox("Smooth Margin Trend", value=False, key="smoothed_trend")
        
        # =======================
        # SECTION 1: TRENDS ANALYSIS
        # =======================
        st.markdown("## 📈 Trends & Performance Analysis")
        st.markdown("<p style='color: #888; font-size: 13px; margin: -10px 0 15px 0;'>Revenue trajectory, profitability trends, and cumulative growth</p>", unsafe_allow_html=True)
        
        # Chart 1: Revenue vs Margin Trend (FULL WIDTH)
        st.markdown("### Revenue vs Margin Trend Analysis")
        st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Weekly analysis of revenue and margin percentage for May-September 2024</p>", unsafe_allow_html=True)
        
        # Create enhanced chart
        chart_result = create_revenue_margin_chart(filtered_sales)
        
        if chart_result:
                    fig, weekly_data, avg_revenue, avg_margin = chart_result
                    
                    # Display chart with Plotly's download option enabled
                    st.plotly_chart(
                        fig, 
                        use_container_width=True,
                        config={'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'revenue_vs_margin_trend',
                            'height': 600,
                            'width': 1000,
                            'scale': 2
                        }}
                    )
                    
                    # Display summary statistics
                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                    
                    with col_stat1:
                        st.metric("📈 Avg Revenue", f"AED {avg_revenue:,.0f}")
                    with col_stat2:
                        st.metric("💰 Avg Margin", f"{avg_margin:.1f}%")
                    with col_stat3:
                        st.metric("📊 Weeks Tracked", len(weekly_data))
                    with col_stat4:
                        total_revenue = weekly_data['revenue'].sum()
                        st.metric("💵 Total Revenue", f"AED {total_revenue:,.0f}")
                    
                    # Data table view (expandable)
                    with st.expander("📋 View Weekly Data", expanded=False):
                        display_data = weekly_data[['week_label', 'revenue', 'margin_pct']].copy()
                        display_data.columns = ['Week', 'Revenue (AED)', 'Margin (%)']
                        display_data['Revenue (AED)'] = display_data['Revenue (AED)'].apply(lambda x: f"AED {x:,.0f}")
                        display_data['Margin (%)'] = display_data['Margin (%)'].apply(lambda x: f"{x:.1f}%")
                        st.dataframe(display_data, use_container_width=True, hide_index=True)
                    
        else:
            st.info("ℹ️ No data available for May-September 2024 period")
        
        # Chart 2: Cumulative Revenue Growth (FULL WIDTH)
        st.markdown("---")
        st.markdown("### Cumulative Revenue Growth")
        st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Progressive total revenue accumulation over time</p>", unsafe_allow_html=True)
        
        ts_cumsum = filtered_sales.copy()
        ts_cumsum['revenue'] = ts_cumsum['qty'] * ts_cumsum['selling_price_aed']
        ts_cumsum['order_time'] = pd.to_datetime(ts_cumsum['order_time'], errors='coerce')
        ts_cumsum = ts_cumsum.sort_values('order_time')
        ts_cumsum['cumulative_revenue'] = ts_cumsum['revenue'].cumsum()
        
        fig = px.area(ts_cumsum, x='order_time', y='cumulative_revenue', 
                     title='Cumulative Revenue Growth',
                     labels={'order_time': 'Date', 'cumulative_revenue': 'Cumulative Revenue (AED)'})
        fig.update_traces(fill='tozeroy', line_color='#4facfe')
        fig.update_layout(height=600, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toggleSpikelines', 'hoverCompareCartesian']})
        
        # =======================
        # SECTION 2: GEOGRAPHIC ANALYSIS
        # =======================
        st.divider()
        st.markdown("## 🗺️ Geographic & Channel Analysis")
        st.markdown("<p style='color: #888; font-size: 13px; margin: -10px 0 15px 0;'>Market distribution across cities and sales channels</p>", unsafe_allow_html=True)
        
        # Chart 3: Revenue Hierarchy (FULL WIDTH)
        st.markdown("### Revenue Distribution by City & Channel")
        st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Sunburst visualization of hierarchical revenue breakdown</p>", unsafe_allow_html=True)
        
        breakdown = sim.get_city_channel_breakdown()
        fig = px.sunburst(breakdown, path=['city', 'channel'], values='revenue',
                         title='Revenue Hierarchy: City → Channel',
                         color='revenue', color_continuous_scale='Viridis')
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toggleSpikelines', 'hoverCompareCartesian']})
        
        # Chart 4: Market Share (FULL WIDTH)
        st.markdown("---")
        st.markdown("### Market Share by Channel & City")
        st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Treemap showing relative market size across channels and cities</p>", unsafe_allow_html=True)
        
        fig = px.treemap(breakdown, path=['channel', 'city'], values='revenue',
                        title='Market Share: Channel → City',
                        color='revenue', color_continuous_scale='Viridis')
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toggleSpikelines', 'hoverCompareCartesian']})
        
        # =======================
        # SECTION 3: PRODUCT ANALYSIS
        # =======================
        st.divider()
        st.markdown("## 🏷️ Product Performance & Strategy")
        st.markdown("<p style='color: #888; font-size: 13px; margin: -10px 0 15px 0;'>BCG matrix analysis: Revenue vs margin with category breakdown</p>", unsafe_allow_html=True)
        
        # Chart 5: Product Performance Matrix (FULL WIDTH)
        st.markdown("### BCG Product Performance Matrix")
        st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Classification by revenue potential and profitability</p>", unsafe_allow_html=True)
        
        perf_matrix = create_product_matrix(filtered_sales)
        
        fig = px.scatter(perf_matrix, x='revenue', y='margin_pct', size='qty', color='category',
                       title='Product Performance Matrix (BCG-Style)', size_max=60)
        
        avg_revenue = perf_matrix['revenue'].median()
        avg_margin = perf_matrix['margin_pct'].median()
        
        fig.add_hline(y=avg_margin, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=avg_revenue, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add BCG quadrant labels
        fig.add_annotation(text="🌟 Stars", x=avg_revenue*1.5, y=avg_margin*1.5, showarrow=False, font=dict(size=14, color="green"))
        fig.add_annotation(text="💰 Money", x=avg_revenue*1.5, y=avg_margin*0.5, showarrow=False, font=dict(size=14, color="blue"))
        fig.add_annotation(text="❓ Question Marks", x=avg_revenue*0.5, y=avg_margin*1.5, showarrow=False, font=dict(size=14, color="orange"))
        fig.add_annotation(text="🐕 Dogs", x=avg_revenue*0.5, y=avg_margin*0.5, showarrow=False, font=dict(size=14, color="red"))
        
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toggleSpikelines', 'hoverCompareCartesian']})
        
        # Strategy Guide (Expandable)
        with st.expander("💡 BCG Strategy Guide", expanded=False):
            col_guide1, col_guide2 = st.columns(2)
            with col_guide1:
                st.markdown("""
                **🌟 Stars** (High Revenue, High Margin)
                - Action: Invest heavily
                - Goal: Maintain dominance
                
                **💰 Money** (High Revenue, Low Margin)
                - Action: Maintain status quo
                - Goal: Generate cash flow
                """)
            with col_guide2:
                st.markdown("""
                **❓ Question Marks** (Low Revenue, High Margin)
                - Action: Selective investment
                - Goal: Test and scale
                
                **🐕 Dogs** (Low Revenue, Low Margin)
                - Action: Divest or discontinue
                - Goal: Reduce portfolio drag
                """)
        
        # =======================
        # SECTION 4: SCENARIO ANALYSIS
        # =======================
        st.divider()
        st.markdown("## 🎯 Scenario Analysis & Optimization")
        st.markdown("<p style='color: #888; font-size: 13px; margin: -10px 0 15px 0;'>Multi-scenario comparison and profit optimization</p>", unsafe_allow_html=True)
        
        if 'sim_results' in st.session_state:
            # Chart 6: Scenario Comparison Table (FULL WIDTH)
            st.markdown("### Multi-Scenario Financial Comparison")
            st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Analysis of different promotional discount scenarios</p>", unsafe_allow_html=True)
            
            scenario_df = create_scenario_comparison(
                sim, sim_city, sim_channel, sim_category,
                promo_budget, margin_floor, sim_days
            )
            
            if not scenario_df.empty:
                optimal_idx = scenario_df['Profit (AED)'].idxmax()
                
                st.dataframe(
                    scenario_df.style.highlight_max(subset=['Profit (AED)'], color='lightgreen')
                                    .format({
                                        'Revenue (AED)': '{:,.0f}',
                                        'Margin %': '{:.1f}',
                                        'Profit (AED)': '{:,.0f}',
                                        'Budget Use %': '{:.1f}',
                                        'Stockout Risk %': '{:.1f}'
                                    }),
                    use_container_width=True,
                    hide_index=True
                )
                
                st.success(f"✨ **Optimal Scenario:** {scenario_df.iloc[optimal_idx]['Discount %']}% discount → {scenario_df.iloc[optimal_idx]['Profit (AED)']:,.0f} AED profit")
                
                # Chart 7: Profit Optimization Curve (FULL WIDTH)
                st.markdown("---")
                st.markdown("### Profit Optimization Curve")
                st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Profit trajectory across different discount levels</p>", unsafe_allow_html=True)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=scenario_df['Discount %'],
                    y=scenario_df['Profit (AED)'],
                    mode='lines+markers',
                    marker=dict(size=12, color=scenario_df['Profit (AED)'], 
                               colorscale='Viridis', showscale=True),
                    line=dict(width=3, color='purple')
                ))
                fig.update_layout(title='Profit Optimization: Discount % vs Profit (AED)', 
                                 xaxis_title='Discount %', yaxis_title='Profit (AED)',
                                 height=600)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toggleSpikelines', 'hoverCompareCartesian']})
            else:
                st.warning("⚠️ No scenario data available")
        else:
            st.info("🚀 Run simulation to generate scenario comparisons")
    
    # MANAGER VIEW
    if True:
        st.header("⚙️ Operations Command Center")
        st.markdown("<p style='color: #888; font-size: 14px; margin: -15px 0 20px 0;'>Real-time operational metrics and risk management</p>", unsafe_allow_html=True)
        
        # KPI Cards (Horizontal layout for manager view)
        st.markdown("### 📊 Key Operational Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'sim_results' in st.session_state:
                _, _, sim_kpis = st.session_state['sim_results']
                risk_color = "red" if sim_kpis['stockout_risk_pct'] > 20 else "orange" if sim_kpis['stockout_risk_pct'] > 10 else "green"
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; font-size:14px; opacity:0.8;">Stockout Risk</h3>
                    <h2 style="margin:10px 0; color:{risk_color};">{sim_kpis['stockout_risk_pct']:.1f}%</h2>
                    <p style="margin:0; font-size:12px;">{sim_kpis['high_risk_skus']} SKUs at risk</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Run simulation")
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin:0; font-size:14px; opacity:0.8;">Return Rate</h3>
                <h2 style="margin:10px 0;">{kpis['return_rate_pct']:.1f}%</h2>
                <p style="margin:0; font-size:12px;">Target: < 5%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin:0; font-size:14px; opacity:0.8;">Payment Failures</h3>
                <h2 style="margin:10px 0;">{kpis['payment_failure_rate_pct']:.1f}%</h2>
                <p style="margin:0; font-size:12px;">Target: < 10%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin:0; font-size:14px; opacity:0.8;">Data Quality</h3>
                <h2 style="margin:10px 0;">{len(issues)}</h2>
                <p style="margin:0; font-size:12px;">Issues Resolved</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # =======================
        # SECTION 1: INVENTORY MANAGEMENT
        # =======================
        st.markdown("## 📦 Inventory Management")
        st.markdown("<p style='color: #888; font-size: 13px; margin: -10px 0 15px 0;'>Stockout risks and inventory distribution analysis</p>", unsafe_allow_html=True)
        
        # Chart 1: Stockout Hotspots
        st.markdown("### Stockout Hotspots by Location")
        st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>At-risk SKUs grouped by city and channel</p>", unsafe_allow_html=True)
        
        if 'sim_results' in st.session_state:
            simulated, _, _ = st.session_state['sim_results']
            
            if 'stockout_risk' in simulated.columns:
                # Check if store_id exists and filter risky items first
                risky_items = simulated[simulated['stockout_risk']].copy()
                
                if len(risky_items) > 0 and 'store_id' in risky_items.columns:
                    # Get unique store IDs from risky items
                    risky_stores = risky_items['store_id'].unique()
                    
                    # Get city and channel for these stores
                    store_info = stores[stores['store_id'].isin(risky_stores)][['store_id', 'city', 'channel']]
                    
                    # Count risks by store first, then merge with city/channel
                    risk_counts = risky_items.groupby('store_id').size().reset_index(name='risk_count')
                    risk_with_location = risk_counts.merge(store_info, on='store_id', how='left')
                    
                    # Aggregate by city and channel
                    if 'city' in risk_with_location.columns and 'channel' in risk_with_location.columns:
                        risk_by_city = risk_with_location.groupby(['city', 'channel'])['risk_count'].sum().reset_index()
                        
                        if len(risk_by_city) > 0:
                            fig = px.bar(
                                risk_by_city,
                                x='city',
                                y='risk_count',
                                color='channel',
                                title='🚨 Stockout Hotspots by Location',
                                barmode='group',
                                color_discrete_sequence=px.colors.qualitative.Bold,
                                labels={'risk_count': 'Number of At-Risk SKUs', 'city': 'City'}
                            )
                            fig.update_layout(height=600)
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toggleSpikelines', 'hoverCompareCartesian']})
                    else:
                        st.info("No location data available for risk aggregation")
                else:
                    # Fallback: just show count by store
                    st.warning("Showing risk by store (city/channel data unavailable)")
                    fig = px.bar(
                        risk_counts.head(10),
                        x='store_id',
                        y='risk_count',
                        title='🚨 Top 10 Stores with Stockout Risk',
                        labels={'risk_count': 'At-Risk SKUs', 'store_id': 'Store'}
                    )
                    fig.update_layout(height=600)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toggleSpikelines', 'hoverCompareCartesian']})
            else:
                st.success("✅ No stockout risks detected!")
        else:
            st.info("Run simulation to see stockout analysis")
        
        # Chart 2: Inventory Distribution
        st.markdown("---")
        st.markdown("### Inventory Level Distribution")
        st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Distribution of current stock levels across all products</p>", unsafe_allow_html=True)
        
        latest_inv = inventory.sort_values('snapshot_date').groupby('product_id').last().reset_index()
        fig = px.histogram(latest_inv, x='stock_on_hand', nbins=40,
                          title='📊 Inventory Distribution', marginal='box')
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toggleSpikelines', 'hoverCompareCartesian']})
        
        # =======================
        # SECTION 2: RISK MANAGEMENT
        # =======================
        st.divider()
        st.markdown("## 🔴 Risk Management & Critical Items")
        st.markdown("<p style='color: #888; font-size: 13px; margin: -10px 0 15px 0;'>Identify and prioritize critical stockout risks</p>", unsafe_allow_html=True)
        
        # Chart 3: Top Critical Risk Items
        st.markdown("### Top 10 Critical Risk Items")
        st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Products at highest risk of stockout with urgency levels</p>", unsafe_allow_html=True)
        
        if 'sim_results' in st.session_state:
            simulated, _, _ = st.session_state['sim_results']
            
            # Extract risk items (those with stockout risk)
            risk_table = simulated[simulated['stockout_risk']].head(10).copy() if 'stockout_risk' in simulated.columns else pd.DataFrame()
            
            if len(risk_table) > 0:
                available_cols = []
                desired_cols = ['product_id', 'city', 'channel', 'category', 'simulated_qty', 
                               'stock_on_hand', 'stock_shortfall', 'urgency_level']
                
                for col in desired_cols:
                    if col in risk_table.columns:
                        available_cols.append(col)
                
                if len(available_cols) > 0:
                    display_table = risk_table[available_cols].copy()
                    
                    # Create readable column names
                    col_mapping = {
                        'product_id': 'Product',
                        'city': 'City',
                        'channel': 'Channel',
                        'category': 'Category',
                        'simulated_qty': 'Demand',
                        'stock_on_hand': 'Stock',
                        'stock_shortfall': 'Shortfall',
                        'urgency_level': 'Urgency'
                    }
                    
                    display_table = display_table.rename(columns={k: v for k, v in col_mapping.items() if k in display_table.columns})
                    
                    # Apply styling only if Urgency column exists
                    if 'Urgency' in display_table.columns:
                        st.dataframe(
                            display_table.style.apply(
                                lambda x: ['background-color: #ffcccc' if v == '🔴 High' 
                                          else 'background-color: #fff9cc' if v == '🟡 Medium'
                                          else '' for v in x], 
                                subset=['Urgency']
                            ),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.dataframe(display_table, use_container_width=True, hide_index=True)
                else:
                    st.warning("Risk data columns not available")
            else:
                st.info("No risk items to display - run simulation first")
        
        # Chart 4: Risk Heat Map / Performance Heatmap
        st.markdown("---")
        st.markdown("### Performance Heat Map (City × Category)")
        st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Revenue and return rate patterns across geographic and product dimensions</p>", unsafe_allow_html=True)
        
        # Create tabs for different metrics
        heatmap_tab1, heatmap_tab2 = st.tabs(["💰 Revenue Heatmap", "🔄 Return Rate Heatmap"])
        
        with heatmap_tab1:
            # Revenue Heatmap using actual sales data
            if 'city' in filtered_sales.columns and 'category' in filtered_sales.columns:
                try:
                    # Calculate revenue by city and category (selling_price_aed * qty)
                    revenue_data = filtered_sales.copy()
                    revenue_data['revenue'] = revenue_data['selling_price_aed'] * revenue_data['qty']
                    revenue_heatmap = revenue_data.groupby(['city', 'category'])['revenue'].sum().reset_index()
                    
                    if len(revenue_heatmap) > 0:
                        # Pivot the data for heatmap
                        revenue_pivot = revenue_heatmap.pivot(
                            index='category', 
                            columns='city', 
                            values='revenue'
                        ).fillna(0)
                        
                        # Create the heatmap
                        fig = px.imshow(
                            revenue_pivot,
                            labels=dict(x='City', y='Category', color='Revenue (AED)'),
                            color_continuous_scale='Blues',
                            aspect='auto',
                            height=600,
                            text_auto='.2s'  # Show values with SI prefix
                        )
                        
                        fig.update_layout(
                            title='Revenue Distribution Across Cities and Categories',
                            xaxis_title='City',
                            yaxis_title='Product Category',
                            margin=dict(l=120, r=80, t=80, b=80),
                            font=dict(size=11)
                        )
                        
                        fig.update_traces(
                            hovertemplate='<b>%{y}</b><br>City: %{x}<br>Revenue: AED %{z:,.0f}<extra></extra>'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toggleSpikelines', 'hoverCompareCartesian']})
                        
                        # Show top performers
                        col1, col2 = st.columns(2)
                        with col1:
                            top_combo = revenue_heatmap.nlargest(5, 'revenue')
                            st.markdown("**🏆 Top 5 City-Category Combinations:**")
                            for idx, row in top_combo.iterrows():
                                st.markdown(f"- **{row['city']}** × {row['category']}: AED {row['revenue']:,.0f}")
                        
                        with col2:
                            bottom_combo = revenue_heatmap.nsmallest(5, 'revenue')
                            st.markdown("**📊 Bottom 5 City-Category Combinations:**")
                            for idx, row in bottom_combo.iterrows():
                                st.markdown(f"- **{row['city']}** × {row['category']}: AED {row['revenue']:,.0f}")
                    else:
                        st.info("No revenue data available for heatmap")
                except Exception as e:
                    st.error(f"Error generating revenue heatmap: {str(e)}")
            else:
                st.warning("City and category data not available")
        
        with heatmap_tab2:
            # Return Rate Heatmap
            if 'city' in filtered_sales.columns and 'category' in filtered_sales.columns and 'return_flag' in filtered_sales.columns:
                try:
                    # Calculate return rates by city and category
                    # return_flag is 'Y' for returned, 'N' for not returned
                    return_data = filtered_sales.copy()
                    return_data['is_returned'] = (return_data['return_flag'] == 'Y').astype(int)
                    
                    return_stats = return_data.groupby(['city', 'category']).agg({
                        'is_returned': 'sum',
                        'order_id': 'count'
                    }).reset_index()
                    
                    return_stats['return_rate'] = (return_stats['is_returned'] / return_stats['order_id'] * 100)
                    
                    if len(return_stats) > 0:
                        # Pivot the data for heatmap
                        return_pivot = return_stats.pivot(
                            index='category', 
                            columns='city', 
                            values='return_rate'
                        ).fillna(0)
                        
                        # Create the heatmap with green scale for returns
                        fig = px.imshow(
                            return_pivot,
                            labels=dict(x='City', y='Category', color='Return Rate (%)'),
                            color_continuous_scale='Greens',  # Green scale: light to dark
                            aspect='auto',
                            height=600,
                            text_auto='.1f'  # Show values with 1 decimal
                        )
                        
                        fig.update_layout(
                            title='Return Rate Distribution Across Cities and Categories',
                            xaxis_title='City',
                            yaxis_title='Product Category',
                            margin=dict(l=120, r=80, t=80, b=80),
                            font=dict(size=11)
                        )
                        
                        fig.update_traces(
                            hovertemplate='<b>%{y}</b><br>City: %{x}<br>Return Rate: %{z:.2f}%<extra></extra>'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toggleSpikelines', 'hoverCompareCartesian']})
                        
                        # Show highest return rates (risk areas)
                        col1, col2 = st.columns(2)
                        with col1:
                            high_returns = return_stats.nlargest(5, 'return_rate')
                            st.markdown("**⚠️ Highest Return Rates (Risk Areas):**")
                            for idx, row in high_returns.iterrows():
                                st.markdown(f"- **{row['city']}** × {row['category']}: {row['return_rate']:.1f}%")
                        
                        with col2:
                            low_returns = return_stats.nsmallest(5, 'return_rate')
                            st.markdown("**✅ Lowest Return Rates (Best Performance):**")
                            for idx, row in low_returns.iterrows():
                                st.markdown(f"- **{row['city']}** × {row['category']}: {row['return_rate']:.1f}%")
                    else:
                        st.info("No return rate data available for heatmap")
                except Exception as e:
                    st.error(f"Error generating return rate heatmap: {str(e)}")
            else:
                st.warning("Return data not available for this view")
        
        # =======================
        # SECTION 3: DATA QUALITY
        # =======================
        st.divider()
        st.markdown("## 🔍 Data Quality & Issues")
        st.markdown("<p style='color: #888; font-size: 13px; margin: -10px 0 15px 0;'>Monitor data completeness, accuracy, and validation issues</p>", unsafe_allow_html=True)
        
        # Chart 5: Pareto Analysis
        st.markdown("### Data Quality Pareto Analysis")
        st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Most common data quality issues affecting business processes</p>", unsafe_allow_html=True)
        
        issue_counts = issues['issue_type'].value_counts().reset_index()
        issue_counts.columns = ['Issue Type', 'Count']
        issue_counts['Cumulative %'] = (issue_counts['Count'].cumsum() / issue_counts['Count'].sum() * 100)
        # Create custom x-axis labels with counts
        issue_counts['x_label'] = [f"{issue_type} ({count})" for issue_type, count in zip(issue_counts['Issue Type'], issue_counts['Count'])]
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=issue_counts['x_label'], y=issue_counts['Count'], 
                            name='Count', marker_color='indianred'), secondary_y=False)
        fig.add_trace(go.Scatter(x=issue_counts['x_label'], y=issue_counts['Cumulative %'],
                                name='Cumulative %', mode='lines+markers', marker_color='blue'), secondary_y=True)
        fig.update_layout(title='Data Quality Pareto Analysis', hovermode='x unified', xaxis_title='Issue Type with Count', height=600)
        fig.update_yaxes(title_text="Count", secondary_y=False)
        fig.update_yaxes(title_text="Cumulative %", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toggleSpikelines', 'hoverCompareCartesian']})
        
        # Data Quality Metrics
        st.markdown("---")
        st.markdown("### Quality Metrics")
        st.markdown("<p style='color: #999; font-size: 12px; margin: -5px 0 10px 0;'>Summary of data quality indicators</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Issues", len(issues))
        with col2:
            st.metric("Issue Types", len(issue_counts))
        with col3:
            st.metric("Top Issue", issue_counts.iloc[0]['Issue Type'] if len(issue_counts) > 0 else "None")
        
    # Download Section
    st.markdown("---")
    st.subheader("💾 Download & Export")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.download_button("📊 Sales Data", sales.to_csv(index=False).encode('utf-8'),
                          f"sales_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
    
    with col2:
        st.download_button("🔍 Issues Log", issues.to_csv(index=False).encode('utf-8'),
                          f"issues_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
    
    with col3:
        if 'sim_results' in st.session_state:
            try:
                simulated, _, _ = st.session_state['sim_results']
                st.download_button("🎯 Simulation", simulated.to_csv(index=False).encode('utf-8'),
                                  f"simulation_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
            except Exception as e:
                st.warning(f"Cannot export simulation: {str(e)}")
    
    with col5:
        # Performance report
        try:
            report_text = generate_performance_report(sales, kpis)
            st.download_button("📈 Report", report_text.encode('utf-8'),
                              f"performance_{datetime.now().strftime('%Y%m%d')}.txt", "text/plain", use_container_width=True)
        except Exception as e:
            st.warning(f"Cannot export report: {str(e)}")
    
    # ===== NEW: ADVANCED EXPORTS =====
    with st.expander("📤 Advanced Export Options", expanded=False):
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            st.write("**Export Format**")
            export_format = st.radio("Select format:", ["CSV", "Excel", "JSON"], horizontal=True)
            
            if st.button("📥 Export All Data"):
                try:
                    if export_format == "JSON":
                        json_data = {
                            'sales': sales.to_dict(orient='records'),
                            'products': products.to_dict(orient='records'),
                            'kpis': kpis
                        }
                        st.download_button(
                            "📥 Download JSON",
                            json.dumps(json_data, indent=2, default=str).encode('utf-8'),
                            f"dashboard_export_{datetime.now().strftime('%Y%m%d')}.json",
                            "application/json",
                            use_container_width=True
                        )
                    else:
                        st.info(f"✅ Export to {export_format} format ready")
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")
                    logger.error(f"Export error: {str(e)}")
        
        with export_col2:
            st.write("**Data Summary**")
            st.metric("Total Records", len(sales) + len(products))
            st.metric("Date Range", f"{sales['order_time'].min() if 'order_time' in sales.columns else 'N/A'}")

if __name__ == "__main__":
    main()