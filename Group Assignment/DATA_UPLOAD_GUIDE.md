# 📤 Custom Dataset Upload Guide

## Overview
The UAE Promo Pulse Dashboard now supports uploading your own datasets in addition to using pre-built example data. This guide will help you prepare and upload your data correctly.

---

## 🚀 Quick Start

### Option 1: Using Pre-Built Dataset (Default)
1. Launch the dashboard
2. The sidebar defaults to **"📁 Pre-Built Dataset"**
3. Click "🚀 Launch Simulation" when ready
4. All features are immediately available

### Option 2: Using Custom Data
1. Launch the dashboard
2. In the sidebar, select **"📤 Upload Custom Data"**
3. Upload the 4 required CSV files (see formats below)
4. Optionally upload an Issues CSV
5. Click "🚀 Launch Simulation" when ready

---

## 📋 Required CSV Files & Format

### 1. **Products CSV**
Contains product/SKU information.

**Required Columns:**
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| product_id | String | Unique product identifier | P0001 |
| category | String | Product category | Electronics |
| brand | String | Brand name | Samsung |
| unit_cost_aed | Float | Cost per unit in AED | 150.50 |

**Optional Columns:**
- base_price_aed: Base selling price
- tax_rate: Tax rate percentage
- launch_flag: Product status (New/Regular)

**Sample Data:**
```csv
product_id,category,brand,unit_cost_aed
P0001,Electronics,Samsung,150.50
P0002,Fashion,Nike,45.75
P0003,Home & Kitchen,Carrefour,25.00
```

---

### 2. **Stores CSV**
Contains store/location information.

**Required Columns:**
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| store_id | String | Unique store identifier | S001 |
| city | String | City name | Dubai |
| channel | String | Sales channel | App |

**Optional Columns:**
- fulfillment_type: Own/3PL

**Valid Values for 'channel':**
- App
- Web
- Marketplace

**Valid Cities:**
- Dubai
- Abu Dhabi
- Sharjah

**Sample Data:**
```csv
store_id,city,channel
S001,Dubai,App
S002,Abu Dhabi,Web
S003,Sharjah,Marketplace
```

---

### 3. **Sales CSV**
Contains transactional/order data.

**Required Columns:**
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| order_id | String | Unique order identifier | ORD000001 |
| product_id | String | Product ID (link to Products) | P0001 |
| store_id | String | Store ID (link to Stores) | S001 |
| qty | Integer | Quantity ordered | 2 |
| selling_price_aed | Float | Price per unit in AED | 199.99 |

**Optional Columns:**
- order_time: Timestamp (YYYY-MM-DD HH:MM:SS)
- discount_pct: Discount percentage (0-100)
- payment_status: Paid/Failed/Refunded
- return_flag: Y/N

**Sample Data:**
```csv
order_id,product_id,store_id,qty,selling_price_aed
ORD000001,P0001,S001,2,199.99
ORD000002,P0002,S002,1,89.99
ORD000003,P0003,S001,5,50.00
```

---

### 4. **Inventory CSV**
Contains stock information.

**Required Columns:**
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| product_id | String | Product ID (link to Products) | P0001 |
| store_id | String | Store ID (link to Stores) | S001 |
| stock_on_hand | Integer | Current stock quantity | 150 |

**Optional Columns:**
- snapshot_date: Date of inventory snapshot (YYYY-MM-DD)
- reorder_point: Minimum stock level for reorder
- lead_time_days: Days to receive new stock

**Sample Data:**
```csv
product_id,store_id,stock_on_hand
P0001,S001,150
P0002,S002,75
P0003,S001,200
```

---

### 5. **Issues CSV (Optional)**
Contains data quality issues found in your dataset.

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| issue_id | String | Issue identifier |
| issue_type | String | Type of issue |
| description | String | Issue description |
| severity | String | High/Medium/Low |

**Sample Data:**
```csv
issue_id,issue_type,description
ISS001,Missing Value,Missing discount_pct in order ORD000005
ISS002,Duplicate,Duplicate order_id ORD000010
```

---

## ✅ Data Validation Checklist

Before uploading, ensure:

### Data Quality
- [ ] No critical missing values in required columns
- [ ] All product_ids in Sales exist in Products CSV
- [ ] All store_ids in Sales exist in Stores CSV
- [ ] All product_ids in Inventory exist in Products CSV
- [ ] All store_ids in Inventory exist in Stores CSV
- [ ] All numeric fields contain valid numbers (no text in price columns)
- [ ] Quantities are positive integers

### Format Requirements
- [ ] Files are in CSV format (.csv extension)
- [ ] UTF-8 encoding
- [ ] First row contains column headers
- [ ] No empty rows in the middle of data
- [ ] Consistent data types per column

### Business Logic
- [ ] Channel values are: App, Web, or Marketplace
- [ ] Cities are standardized (no "dubai" vs "Dubai")
- [ ] Prices are in AED
- [ ] Percentages are 0-100
- [ ] Dates follow YYYY-MM-DD format

---

## 🔧 Data Preparation Tips

### Using Excel/Google Sheets
1. Prepare your data in Excel or Google Sheets
2. Save as CSV (comma-separated values)
3. Ensure column names match exactly (case-sensitive)
4. Remove any empty columns
5. Export/Download as CSV

### Handling Missing Values
- For **numeric** fields: Use 0 or average value
- For **categorical** fields: Use "Unknown" or most common value
- For **optional** fields: Leave blank (will be handled automatically)

### Standardizing City Names
```
BEFORE: Dubai, DUBAI, dubai, Dubayy
AFTER:  Dubai

BEFORE: Abu Dhabi, ABU DHABI, AbuDhabi
AFTER:  Abu Dhabi

BEFORE: Sharjah, SHARJAH, Sharja
AFTER:  Sharjah
```

### Data Sampling
If your data is very large (>1M rows):
1. Consider splitting into monthly/quarterly datasets
2. Sample 10-20% of data for testing
3. Use date range filters for specific periods

---

## 📊 Example Dataset Structure

Here's a minimal complete dataset:

**products.csv**
```csv
product_id,category,brand,unit_cost_aed
P001,Electronics,Samsung,150
P002,Fashion,Nike,40
```

**stores.csv**
```csv
store_id,city,channel
S001,Dubai,App
S002,Dubai,Web
```

**sales.csv**
```csv
order_id,product_id,store_id,qty,selling_price_aed
ORD001,P001,S001,2,200
ORD002,P002,S002,1,80
```

**inventory.csv**
```csv
product_id,store_id,stock_on_hand
P001,S001,100
P001,S002,50
P002,S001,75
P002,S002,60
```

---

## 🐛 Common Issues & Solutions

### Error: "Products missing columns: {'unit_cost_aed'}"
**Solution:** Make sure your Products CSV has exactly these columns:
- product_id
- category
- brand
- unit_cost_aed

### Error: "Stores missing columns: {'city', 'channel'}"
**Solution:** Ensure your Stores CSV has all required columns spelled exactly:
- store_id, city, channel

### Error: "Products file not uploaded"
**Solution:** All 4 files (Products, Stores, Sales, Inventory) must be uploaded. Issues CSV is optional.

### Dashboard shows no data
**Possible causes:**
- Foreign key mismatch (e.g., product_id in Sales not in Products)
- Empty CSV files
- Special characters in IDs

**Solution:** Verify all IDs are consistent across files

### Graphs not displaying
**Possible causes:**
- Insufficient data (< 10 records)
- All data filtered out by preset selections
- Missing required columns

**Solution:** Try "Custom" preset with broader filters

---

## 🎯 Best Practices

1. **Start Small:** Begin with a small dataset (100-1000 rows) to test
2. **Validate First:** Check data before uploading
3. **Use Consistent IDs:** Keep product_id and store_id formats consistent
4. **Document Issues:** Use the Issues CSV to document known data quality problems
5. **Backup Original:** Keep original data separate from cleaned version
6. **Test After Upload:** Verify all dashboard features work with your data

---

## 📞 Support

For issues with:
- **Data format:** Check the column names and data types above
- **Dashboard features:** Try switching to Pre-Built Dataset to confirm it's data-related
- **Performance:** Reduce data size if dataset is >1M rows

---

## 🔄 Switching Between Data Sources

You can easily switch between Pre-Built and Custom data:
1. In the sidebar, select different option under "Select Data Source"
2. If switching to custom data, re-upload the files
3. If switching to pre-built, no action needed (default)
4. Dashboard will automatically reload with new data source

**Note:** Simulation results are preserved until you change data source or clear cache.
