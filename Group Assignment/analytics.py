import pandas as pd
import numpy as np

# =========================================================
# MAIN ANALYTICS ENGINE
# =========================================================

class Analytics:
    """Handles KPI calculations and analytical functions"""

    def __init__(self, products, stores, sales, inventory):
        self.products = products
        self.stores = stores
        self.sales = sales
        self.inventory = inventory

    # -----------------------------------------------------
    # CORE KPI CALCULATIONS
    # -----------------------------------------------------
    def calculate_kpis(self, filtered_sales=None):
        if filtered_sales is None:
            filtered_sales = self.sales

        sales_with_details = filtered_sales.merge(
            self.products[['product_id', 'unit_cost_aed', 'base_price_aed']],
            on='product_id',
            how='left'
        )

        paid_sales = sales_with_details[sales_with_details['payment_status'] == 'Paid']

        kpis = {}

        kpis['gross_revenue'] = (paid_sales['selling_price_aed'] * paid_sales['qty']).sum()

        refunded = sales_with_details[sales_with_details['payment_status'] == 'Refunded']
        kpis['refund_amount'] = (refunded['selling_price_aed'] * refunded['qty']).sum()

        kpis['net_revenue'] = kpis['gross_revenue'] - kpis['refund_amount']

        kpis['cogs'] = (paid_sales['unit_cost_aed'] * paid_sales['qty']).sum()

        kpis['gross_margin_aed'] = kpis['net_revenue'] - kpis['cogs']
        kpis['gross_margin_pct'] = (
            kpis['gross_margin_aed'] / kpis['net_revenue'] * 100
            if kpis['net_revenue'] > 0 else 0
        )

        kpis['avg_discount_pct'] = paid_sales['discount_pct'].mean()
        kpis['total_orders'] = len(paid_sales)
        kpis['avg_order_value'] = (
            kpis['net_revenue'] / kpis['total_orders']
            if kpis['total_orders'] > 0 else 0
        )

        total_orders = len(
            sales_with_details[sales_with_details['payment_status'].isin(['Paid', 'Refunded'])]
        )
        returned_orders = sales_with_details['return_flag'].sum()
        kpis['return_rate_pct'] = (
            returned_orders / total_orders * 100 if total_orders > 0 else 0
        )

        total_attempts = len(sales_with_details)
        failed = len(sales_with_details[sales_with_details['payment_status'] == 'Failed'])
        kpis['payment_failure_rate_pct'] = (
            failed / total_attempts * 100 if total_attempts > 0 else 0
        )

        kpis['total_qty_sold'] = paid_sales['qty'].sum()
        kpis['unique_products'] = paid_sales['product_id'].nunique()
        kpis['unique_customers'] = paid_sales['order_id'].nunique()

        return kpis

    # -----------------------------------------------------
    # REVENUE TREND
    # -----------------------------------------------------
    def calculate_revenue_trend(self, sales_data, freq='D'):
        paid = sales_data[sales_data['payment_status'] == 'Paid'].copy()
        if paid.empty:
            return pd.DataFrame()

        paid['revenue'] = paid['selling_price_aed'] * paid['qty']
        trend = paid.groupby(pd.Grouper(key='order_time', freq=freq)).agg(
            revenue=('revenue', 'sum'),
            orders=('order_id', 'count'),
            quantity=('qty', 'sum')
        ).reset_index()

        return trend

    # -----------------------------------------------------
    # REVENUE HIERARCHY (CITY × CHANNEL)
    # -----------------------------------------------------
    def get_city_channel_hierarchy(self):
        df = self.sales.merge(
            self.stores[['store_id', 'city', 'channel']], on='store_id'
        ).merge(
            self.products[['product_id', 'unit_cost_aed']], on='product_id'
        )

        paid = df[df['payment_status'] == 'Paid']
        paid['revenue'] = paid['selling_price_aed'] * paid['qty']
        paid['margin'] = paid['revenue'] - (paid['unit_cost_aed'] * paid['qty'])

        agg = paid.groupby(['city', 'channel']).agg(
            revenue=('revenue', 'sum'),
            margin=('margin', 'sum'),
            orders=('order_id', 'count')
        ).reset_index()

        agg['AOV'] = agg['revenue'] / agg['orders']
        agg['margin_pct'] = (agg['margin'] / agg['revenue'] * 100).fillna(0)

        return agg

    # -----------------------------------------------------
    # PROFIT DENSITY (OPTIMIZATION HEATMAP)
    # -----------------------------------------------------
    def get_category_city_profit_density(self):
        df = self.sales.merge(
            self.products[['product_id', 'category', 'unit_cost_aed']], on='product_id'
        ).merge(
            self.stores[['store_id', 'city']], on='store_id'
        )

        paid = df[df['payment_status'] == 'Paid']
        paid['revenue'] = paid['selling_price_aed'] * paid['qty']
        paid['margin'] = paid['revenue'] - (paid['unit_cost_aed'] * paid['qty'])

        agg = paid.groupby(['category', 'city']).agg(
            revenue=('revenue', 'sum'),
            margin=('margin', 'sum')
        ).reset_index()

        agg['profit_density'] = (agg['margin'] / agg['revenue']).fillna(0)

        return agg

    # -----------------------------------------------------
    # BCG MATRIX (CATS / DOGS)
    # -----------------------------------------------------
    def get_bcg_matrix(self):
        df = self.sales[self.sales['payment_status'] == 'Paid'].merge(
            self.products[['product_id', 'category', 'unit_cost_aed']], on='product_id'
        )

        df['revenue'] = df['selling_price_aed'] * df['qty']
        df['margin'] = df['revenue'] - (df['unit_cost_aed'] * df['qty'])

        prod = df.groupby('product_id').agg(
            revenue=('revenue', 'sum'),
            margin=('margin', 'sum'),
            qty=('qty', 'sum')
        ).reset_index()

        prod['growth'] = prod['qty'].pct_change().fillna(0)

        rev_med = prod['revenue'].median()

        prod['BCG'] = np.select(
            [
                (prod['revenue'] > rev_med) & (prod['growth'] > 0),
                (prod['revenue'] <= rev_med) & (prod['growth'] > 0),
                (prod['revenue'] > rev_med) & (prod['growth'] <= 0)
            ],
            ['Star 🐱', 'Question ❓', 'Cash Cow 🐶'],
            default='Dog 🐭'
        )

        return prod

    # -----------------------------------------------------
    # INVENTORY METRICS (BUSINESS-READY)
    # -----------------------------------------------------
    def calculate_inventory_metrics(self):
        latest = self.inventory.sort_values('snapshot_date').groupby(
            ['product_id', 'store_id']
        ).last().reset_index()

        merged = latest.merge(
            self.products[['product_id', 'unit_cost_aed']], on='product_id'
        )

        return {
            'total_stock_units': merged['stock_on_hand'].sum(),
            'total_stock_value': (merged['stock_on_hand'] * merged['unit_cost_aed']).sum(),
            'low_stock_units': merged[merged['stock_on_hand'] <= merged['reorder_point']]['stock_on_hand'].sum(),
            'overstock_units': merged[merged['stock_on_hand'] > merged['reorder_point'] * 3]['stock_on_hand'].sum()
        }

# =========================================================
# A/B TESTING FRAMEWORK (DASHBOARD-COMPATIBLE)
# =========================================================

class ABTestingFramework:

    @staticmethod
    def _ttest(a, b):
        mean_a, mean_b = a.mean(), b.mean()
        var_a, var_b = a.var(), b.var()
        n_a, n_b = len(a), len(b)

        se = np.sqrt(var_a / n_a + var_b / n_b)
        t = (mean_b - mean_a) / se if se > 0 else 0
        p = np.exp(-0.717 * abs(t) - 0.416 * t**2)  # approximation

        lift = ((mean_b - mean_a) / mean_a * 100) if mean_a else 0

        return t, p, lift

    @staticmethod
    def compare_cities(df, metric):
        cities = df['city'].dropna().unique()
        if len(cities) < 2:
            return None

        a, b = cities[:2]
        da = df[df['city'] == a][metric].dropna()
        db = df[df['city'] == b][metric].dropna()

        t, p, lift = ABTestingFramework._ttest(da, db)

        return ABTestingFramework._format(a, b, da, db, t, p, lift)

    @staticmethod
    def compare_channels(df, metric):
        ch = df['channel'].dropna().unique()
        if len(ch) < 2:
            return None

        a, b = ch[:2]
        da = df[df['channel'] == a][metric].dropna()
        db = df[df['channel'] == b][metric].dropna()

        t, p, lift = ABTestingFramework._ttest(da, db)
        return ABTestingFramework._format(a, b, da, db, t, p, lift)

    @staticmethod
    def compare_metrics_by_discount(df, metric):
        low = df[df['discount_pct'] <= 10][metric]
        high = df[df['discount_pct'] >= 30][metric]

        t, p, lift = ABTestingFramework._ttest(low, high)
        return ABTestingFramework._format("Low Discount", "High Discount", low, high, t, p, lift)

    @staticmethod
    def _format(a, b, da, db, t, p, lift):
        return {
            "group_a": {"name": a, "mean": da.mean(), "n": len(da), "data": da},
            "group_b": {"name": b, "mean": db.mean(), "n": len(db), "data": db},
            "statistics": {"t_stat": t, "p_value": p},
            "conclusion": {
                "significant": p < 0.05,
                "lift_pct": lift,
                "recommendation": "Roll out B" if lift > 0 else "No clear winner"
            }
        }
