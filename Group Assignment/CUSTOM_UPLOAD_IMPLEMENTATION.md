# 🎯 Custom Dataset Upload Feature - Implementation Guide

## Overview
The UAE Promo Pulse Dashboard has been enhanced with the ability to upload and analyze custom datasets. Users can now choose between pre-built sample data or their own datasets.

---

## ✨ What's New

### Features Added

#### 1. **Data Source Selection** (Sidebar)
- Radio button to choose between "📁 Pre-Built Dataset" or "📤 Upload Custom Data"
- Default to pre-built dataset for ease of use
- Seamless switching between data sources

#### 2. **File Upload Interface**
- Drag-and-drop upload for 4 required CSV files:
  - 📦 Products
  - 🏪 Stores
  - 🛍️ Sales
  - 📊 Inventory
- Optional upload for Issues CSV (for data quality tracking)
- Organized upload layout with 2-column file picker

#### 3. **Data Validation**
- Automatic validation of required columns
- Checks for missing or misnamed columns
- Clear error messages if validation fails
- User-friendly guidance on what's expected

#### 4. **Dataset Information Display**
- Expandable section showing dataset statistics
- Displays: Product count, Store count, Order count, Inventory records
- Indicates which data source is being used
- Helps users verify data was loaded correctly

#### 5. **Error Handling**
- Graceful error messages
- Stops processing if required files are missing
- Provides helpful next steps for users

---

## 🏗️ Architecture

### New Functions Added to `app.py`

#### `load_custom_datasets()`
```python
def load_custom_datasets(products_file, stores_file, sales_file, inventory_file, issues_file=None):
    """Load custom datasets from uploaded files"""
```
- **Purpose:** Load CSV files from file uploader objects
- **Validates:** Required columns and data structure
- **Returns:** Tuple of dataframes or error message
- **Error Handling:** Returns specific error messages for debugging

### Modified Functions

#### `main()` Function
- Added data source selection logic at the start
- Conditional data loading based on user selection
- Session state management for data persistence
- Enhanced UI with dataset information

### Session State Management
- `st.session_state.dark_mode`: Persists across reruns
- File uploader keys unique for state management
- Data preserved during simulation runs

---

## 📊 CSV File Specifications

### Required Columns

**Products**
```
product_id, category, brand, unit_cost_aed
```

**Stores**
```
store_id, city, channel
```

**Sales**
```
order_id, product_id, store_id, qty, selling_price_aed
```

**Inventory**
```
product_id, store_id, stock_on_hand
```

### Optional Columns

**Products**: base_price_aed, tax_rate, launch_flag
**Stores**: fulfillment_type
**Sales**: order_time, discount_pct, payment_status, return_flag
**Inventory**: snapshot_date, reorder_point, lead_time_days
**Issues**: issue_id, issue_type, description, severity

---

## 🚀 Usage Workflow

### For Users - Using Pre-Built Data
1. Launch dashboard: `streamlit run app.py`
2. Default "📁 Pre-Built Dataset" is selected
3. All features immediately available
4. Click "🚀 Launch Simulation" in sidebar

### For Users - Using Custom Data
1. Launch dashboard: `streamlit run app.py`
2. In sidebar, select "📤 Upload Custom Data"
3. Upload 4 required CSV files
4. See validation status (✅ or ❌)
5. Dataset information shows row counts
6. Click "🚀 Launch Simulation" in sidebar

### For Developers - Testing Custom Upload
1. Run sample generator: `python create_sample_dataset.py`
2. This creates: sample_products.csv, sample_stores.csv, sample_sales.csv, sample_inventory.csv
3. Upload these files to test the feature
4. All dashboard features should work normally

---

## 📁 New Files Created

### 1. `DATA_UPLOAD_GUIDE.md`
Comprehensive user guide for:
- Quick start instructions
- CSV file format specifications
- Data validation checklist
- Example data structures
- Common issues and solutions
- Best practices

### 2. `create_sample_dataset.py`
Utility script to generate sample datasets:
- Creates 5 sample CSV files
- Realistic data with proper relationships
- 1000 orders, 50 products, 18 stores
- 30 days of inventory snapshots
- Optional issue tracking

**To run:**
```bash
python create_sample_dataset.py
```

**Output files:**
- sample_products.csv
- sample_stores.csv
- sample_sales.csv
- sample_inventory.csv
- sample_issues.csv

---

## 🔧 Technical Implementation Details

### Data Flow

```
User Selection
     ↓
┌─────────────────────────┐
│  Pre-Built Data?        │
├──────────┬──────────────┤
│   YES    │      NO      │
↓          ↓
load_data() → load_custom_datasets()
     ↓              ↓
     └──────┬───────┘
            ↓
    initialize_simulator()
            ↓
    Display Dashboard
```

### Validation Logic

```python
Required Columns Check:
  ✓ All required columns present?
    ↓ YES: Continue
    ↓ NO: Return error with missing columns
  
Data Integrity Check:
  ✓ Foreign keys valid? (product_id, store_id exist)
  ✓ No critical nulls in required fields?
  ✓ Data types correct?
    ↓ YES: Load data
    ↓ NO: Return specific error
```

### Error Messages

Clear error hierarchy:
1. **Column Validation Error**: "Products missing columns: {'unit_cost_aed'}"
2. **File Upload Error**: "Please upload all required files"
3. **Data Load Error**: "Error loading files: [specific error]"
4. **Foreign Key Error**: Handled during simulator initialization

---

## 🎨 UI/UX Enhancements

### Sidebar Organization
```
📊 Data Source
├─ Select Data Source (Radio)
└─ Upload Section (Conditional)
   ├─ Products, Stores (Column 1)
   ├─ Sales, Inventory (Column 2)
   └─ Issues (Optional)

🎛️ Control Panel
├─ Quick Presets
├─ Time Period
├─ Filters
└─ Simulation Lab
```

### Dashboard Info Section
- Expandable "📊 Dataset Information"
- Shows: Product count, Store count, Orders, Inventory records
- Indicates data source (Pre-built vs Custom)
- Helps users verify data loaded correctly

### Visual Feedback
- ✅ Success messages when data loads
- ❌ Error messages with guidance
- ⚠️ Warning messages for missing required files
- 💡 Info messages with helpful tips

---

## ✅ Testing Checklist

### Functional Testing

**Pre-Built Data:**
- [ ] Default loads without errors
- [ ] All KPI cards display
- [ ] Dashboard tabs work
- [ ] Simulation runs successfully
- [ ] Download buttons work

**Custom Data Upload:**
- [ ] File upload interface appears
- [ ] Can upload all 4 required files
- [ ] Validation error shown for missing columns
- [ ] Success message after upload
- [ ] All features work with custom data
- [ ] Dataset info displays correct counts

**Data Validation:**
- [ ] Error for missing Products file
- [ ] Error for missing Stores file
- [ ] Error for missing Sales file
- [ ] Error for missing Inventory file
- [ ] Issues file optional works
- [ ] Column mismatch error is clear

**UI/UX:**
- [ ] Smooth switching between data sources
- [ ] File upload layout is clear
- [ ] Error messages are helpful
- [ ] Dataset info expander works
- [ ] Sidebar organization is logical
- [ ] Responsive on different screen sizes

### Edge Cases

- [ ] Upload very small dataset (10 rows)
- [ ] Upload very large dataset (1M+ rows)
- [ ] Upload with missing optional columns
- [ ] Upload with extra columns
- [ ] Upload with different encoding
- [ ] Upload with special characters
- [ ] Re-upload after switching back to pre-built

---

## 🚨 Troubleshooting

### Common Issues

**"Products missing columns: {'unit_cost_aed'}"**
- Solution: Add unit_cost_aed column to products CSV

**"Please upload all required files"**
- Solution: Make sure all 4 files are uploaded (Issues is optional)

**No data visible in dashboard**
- Check: Foreign key relationships between tables
- Check: Preset filters haven't filtered out all data
- Try: "Custom" preset with broader filters

**Simulation fails**
- Check: Data quality issues (negative stock, invalid dates)
- Try: Pre-built data to confirm dashboard works
- Check: CSV file encoding is UTF-8

---

## 📈 Future Enhancements

Potential features for future versions:
1. **Data Cleaning Integration**
   - Auto-clean data using cleaner.py
   - Suggest fixes for common issues

2. **Data Preview**
   - Show sample of uploaded data before processing
   - Display data quality metrics

3. **Multi-File Upload**
   - Zip file upload with multiple CSVs
   - Directory monitoring

4. **Data Transformation**
   - Interactive column mapping
   - Data type inference
   - Automatic deduplication

5. **Export Capabilities**
   - Export processed data as CSV
   - Export analysis results
   - Schedule recurring reports

---

## 📞 Support & Documentation

### Documentation Files
- `DATA_UPLOAD_GUIDE.md` - User guide for uploading data
- `create_sample_dataset.py` - Generate test data
- This file - Implementation documentation

### Code Comments
All new functions include:
- Docstrings explaining purpose
- Parameter descriptions
- Return value documentation
- Error handling documentation

---

## 🔐 Security Considerations

Current implementation:
- File uploads handled by Streamlit (secure)
- No file storage - data kept in memory
- CSV validation before processing
- No code execution from uploaded files

Best practices for users:
- Only upload CSV files
- Verify file sources
- Avoid uploading sensitive personally identifiable information
- Use with trusted data sources only

---

## 📝 Summary

The custom dataset upload feature provides a seamless way for users to:
- ✅ Use pre-built sample data instantly
- ✅ Upload their own datasets easily
- ✅ Get validation feedback quickly
- ✅ Access full dashboard features with custom data
- ✅ Switch between data sources effortlessly

The implementation maintains all existing functionality while adding new capabilities, with clear error handling and user-friendly interfaces.
