# 🎨 Visual Guide - Custom Dataset Upload

## 🖼️ User Interface Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  🇦🇪 UAE Promo Pulse Dashboard                          🌓 ☀️  │
│  AI-Powered Promotional Decision Intelligence                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📊 Dataset Information                                    [∨]   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 📦 Products: 300  │  🏪 Stores: 18                       │    │
│  │ 🛍️ Orders: 32,500  │  📋 Inventory: 2,700               │    │
│  │ Data Source: Pre-built Dataset                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  💼 Executive Suite    ⚙️ Operations Command Center              │
│  [Selected]                                                      │
├─────────────────────────────────────────────────────────────────┤
│  SIDEBAR                    │  MAIN CONTENT                     │
│  ─────────────────────────  │  ─────────────────────────────────│
│  📊 Data Source             │  💵 Revenue      📊 Margin        │
│  ┌─────────────────────────┐│  8.2M AED        18.5%            │
│  │ ○ Pre-Built Dataset     ││  📦 SKUs         🏪 Stores       │
│  │ ● Upload Custom Data    ││  300             18              │
│  └─────────────────────────┘│  🔄 Returns                      │
│                             │  4.2%                            │
│  ⚡ Quick Presets           │                                   │
│  ┌─────────────────────────┐│  📈 Trends   🗺️ Geographic       │
│  │ [Custom        ▼]       ││  [Tabs...]                       │
│  └─────────────────────────┘│                                   │
│                             │                                   │
│  📅 Time Period             │                                   │
│  ┌─────────────────────────┐│                                   │
│  │ [Date Range Selector]   ││                                   │
│  └─────────────────────────┘│                                   │
│                             │                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📤 Upload Flow Diagram

```
START
  ↓
SELECT DATA SOURCE
  ├─────────────────┬──────────────────┐
  │                 │                  │
  v                 v                  v
OPTION A         OPTION B           OPTION C
Pre-Built        Upload Custom      Generate Sample
  │                 │                  │
  │            Upload Files:           │
  │            ┌─────────────────┐     │
  │            │ Products CSV    │     v
  │            │ Stores CSV      │   RUN: python
  │            │ Sales CSV       │   create_sample_
  │            │ Inventory CSV   │   dataset.py
  │            │ Issues CSV (opt)│     │
  │            └─────────────────┘     │
  │                 │                  │
  │            VALIDATE               │
  │            ├─ Required columns?   │
  │            ├─ Valid data types?   │
  │            ├─ Check foreign keys? │
  │                 │                  │
  │                 v                  |
  │            Valid? ──NO──→ ERROR MSG
  │                 │          RETRY
  │                 │
  │           ┌─────YES─────┐
  │           │             │
  └───────────┼─────────────┘
              │
              v
        LOAD DATA
              │
              v
        INITIALIZE SIMULATOR
              │
              v
        DISPLAY DASHBOARD
              │
              v
            END
```

---

## 📋 File Upload Interface

```
┌─────────────────────────────────────────────────┐
│  📊 Data Source                                 │
├─────────────────────────────────────────────────┤
│                                                   │
│  Select Data Source:                            │
│  ○ 📁 Pre-Built Dataset                         │
│  ● 📤 Upload Custom Data                        │
│                                                   │
│  Upload Required Files:                         │
│  ⓘ Upload CSV files for: Products, Stores,     │
│    Sales, and Inventory                         │
│                                                   │
│  ┌─────────────────────┬─────────────────────┐  │
│  │ 📦 Products CSV     │ 🏪 Stores CSV       │  │
│  │ [Choose file] ✓     │ [Choose file] ✓     │  │
│  ├─────────────────────┼─────────────────────┤  │
│  │ 🛍️ Sales CSV        │ 📊 Inventory CSV    │  │
│  │ [Choose file] ✓     │ [Choose file] ✓     │  │
│  └─────────────────────┴─────────────────────┘  │
│                                                   │
│  📋 Issues CSV (Optional)                       │
│  [Choose file]                                   │
│                                                   │
│  ✅ Custom data loaded successfully!            │
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   USER INTERFACE                        │
│              (Streamlit Dashboard)                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        v                         v
   ┌─────────┐            ┌──────────────┐
   │Pre-Built│            │Upload Custom │
   │ Data    │            │   Data       │
   │CSV Files│            │  Files       │
   └────┬────┘            └──────┬───────┘
        │                        │
        │                   load_custom_datasets()
        │                   ├─ Read CSV files
        │                   ├─ Validate columns
        │                   └─ Return dataframes
        │                        │
        └────────────┬───────────┘
                     │
                     v
        ┌────────────────────────┐
        │   DATAFRAMES CREATED   │
        ├────────────────────────┤
        │ products               │
        │ stores                 │
        │ sales                  │
        │ inventory              │
        │ issues                 │
        └────────────┬───────────┘
                     │
                     v
        ┌────────────────────────┐
        │  initialize_simulator()│
        │   Create PromoSimulator│
        │   with data            │
        └────────────┬───────────┘
                     │
                     v
        ┌────────────────────────┐
        │  DASHBOARD DISPLAY     │
        ├────────────────────────┤
        │ • KPI Cards            │
        │ • Charts & Graphs      │
        │ • Filters & Presets    │
        │ • Simulation Features  │
        └────────────────────────┘
```

---

## ✅ Validation Pipeline

```
INPUT: CSV Files
  ↓
STEP 1: File Reading
  ├─ Products file → pd.read_csv()
  ├─ Stores file → pd.read_csv()
  ├─ Sales file → pd.read_csv()
  ├─ Inventory file → pd.read_csv()
  └─ Issues file → pd.read_csv() (optional)
  ↓
STEP 2: Column Validation
  ├─ Products required: product_id, category, brand, unit_cost_aed
  ├─ Stores required: store_id, city, channel
  ├─ Sales required: order_id, product_id, store_id, qty, selling_price_aed
  ├─ Inventory required: product_id, store_id, stock_on_hand
  └─ Issues optional: any columns
  ↓
CHECK: Missing Columns?
  ├─ NO  → Continue to Step 3
  └─ YES → Return Error & Stop
  ↓
STEP 3: Data Type Checking
  ├─ Numeric fields: Convert if needed
  ├─ String fields: Standardize if needed
  ├─ Date fields: Parse if present
  └─ Handle NaN values gracefully
  ↓
CHECK: Critical Errors?
  ├─ NO  → Return success tuple
  └─ YES → Return error message
  ↓
OUTPUT: (dataframes, error_msg) or Error
```

---

## 🎯 CSV Column Requirements Matrix

```
┌────────────────┬──────────────────────────────────────┐
│ FILE           │ REQUIRED COLUMNS                     │
├────────────────┼──────────────────────────────────────┤
│ Products       │ • product_id                         │
│                │ • category                           │
│                │ • brand                              │
│                │ • unit_cost_aed                      │
├────────────────┼──────────────────────────────────────┤
│ Stores         │ • store_id                           │
│                │ • city                               │
│                │ • channel                            │
├────────────────┼──────────────────────────────────────┤
│ Sales          │ • order_id                           │
│                │ • product_id (FK to Products)       │
│                │ • store_id (FK to Stores)           │
│                │ • qty                                │
│                │ • selling_price_aed                  │
├────────────────┼──────────────────────────────────────┤
│ Inventory      │ • product_id (FK to Products)       │
│                │ • store_id (FK to Stores)           │
│                │ • stock_on_hand                      │
├────────────────┼──────────────────────────────────────┤
│ Issues         │ Optional - any columns               │
│ (Optional)     │                                      │
└────────────────┴──────────────────────────────────────┘

FK = Foreign Key relationship required
```

---

## 📊 Data Model Relationships

```
PRODUCTS
┌─────────────────┐
│ product_id (PK) │
│ category        │
│ brand           │
│ unit_cost_aed   │
└────────┬────────┘
         │
    ┌────┴─────────────┐
    │ (1:N)            │ (1:N)
    ↓                  ↓
SALES            INVENTORY
┌──────────────────┐  ┌──────────────────┐
│ order_id (PK)    │  │ product_id (FK)  │
│ product_id (FK)──┼──→ store_id (FK)    │
│ store_id (FK)    │  │ stock_on_hand    │
│ qty              │  │ reorder_point    │
│ selling_price    │  │ lead_time_days   │
└────────┬─────────┘  └──────────────────┘
         │
         ↓
    STORES
    ┌──────────────┐
    │ store_id(PK) │
    │ city         │
    │ channel      │
    └──────────────┘
```

---

## 🎨 Dashboard Features by Data Source

```
┌──────────────────┬─────────────────┬─────────────────┐
│ FEATURE          │ PRE-BUILT DATA  │ CUSTOM DATA     │
├──────────────────┼─────────────────┼─────────────────┤
│ KPI Cards        │ ✅              │ ✅              │
│ Trends Charts    │ ✅              │ ✅              │
│ Geographic Maps  │ ✅              │ ✅              │
│ Product Matrix   │ ✅              │ ✅              │
│ Simulations      │ ✅              │ ✅              │
│ Inventory Mgmt   │ ✅              │ ✅              │
│ Risk Analysis    │ ✅              │ ✅              │
│ Data Quality     │ ✅              │ ✅              │
│ Preset Filters   │ ✅              │ ✅              │
│ Custom Filters   │ ✅              │ ✅              │
│ Scenario Builder │ ✅              │ ✅              │
│ Export Reports   │ ✅              │ ✅              │
└──────────────────┴─────────────────┴─────────────────┘

✅ = Feature available with both data sources
```

---

## 🚀 User Journey Map

```
FIRST TIME USER
├─ Visit Dashboard
├─ See "Pre-Built Dataset" (default selected)
├─ Click "🚀 Launch Simulation"
├─ Explore all features with sample data
├─ Understand dashboard capabilities
└─ [Decision Point]
   ├─ → Want to test with own data?
   │    ├─ Generate sample: python create_sample_dataset.py
   │    └─ Upload via UI
   │
   └─ → Want to upload real data?
        ├─ Prepare CSV files
        ├─ Select "📤 Upload Custom Data"
        ├─ Upload 4 files
        └─ Explore with real data


RETURNING USER (WITH OWN DATA)
├─ Visit Dashboard
├─ Select "📤 Upload Custom Data"
├─ Upload CSV files (remember previous files)
├─ Dashboard loads immediately
├─ Run simulations & analysis
└─ Export results
```

---

## 📈 Error Handling Tree

```
User Uploads Files
    ↓
Try to read CSV files
    ├─ File not found? → "File doesn't exist"
    ├─ Invalid CSV? → "Not a valid CSV file"
    └─ Read OK ✓
        ↓
Validate required columns
    ├─ Products missing unit_cost_aed? 
    │  → "Products missing columns: {'unit_cost_aed'}"
    ├─ Stores missing city?
    │  → "Stores missing columns: {'city'}"
    ├─ Sales missing order_id?
    │  → "Sales missing columns: {'order_id'}"
    ├─ Inventory missing stock_on_hand?
    │  → "Inventory missing columns: {'stock_on_hand'}"
    └─ All valid? ✓
        ↓
Check data integrity
    ├─ Empty dataframe?
    │  → "No data in file"
    └─ Data OK? ✓
        ↓
    Load Success ✅
    "Custom data loaded successfully!"
```

---

## 🔄 State Management

```
SESSION STATE
┌──────────────────────────────────┐
│ Streamlit Session State Object   │
├──────────────────────────────────┤
│ dark_mode: bool                  │ ← Toggle theme
│ sim_results: tuple               │ ← Simulation output
│ uploaded_data: tuple             │ ← Custom data loaded
│ data_source: str                 │ ← Current source
└──────────────────────────────────┘

File Uploader State
├─ products_upload: UploadedFile
├─ stores_upload: UploadedFile
├─ sales_upload: UploadedFile
├─ inventory_upload: UploadedFile
└─ issues_upload: UploadedFile (optional)

Data Persistence
├─ Pre-built: Cached via @st.cache_data
├─ Custom: Stored in session until refresh
└─ Simulation: Persisted in st.session_state
```

---

## 📊 Dashboard Layout Zones

```
┌────────────────────────────────────────────────┐
│            HEADER ZONE                         │  Configurable
│ Title | Subtitle | Dark Mode Toggle           │  Height: 80px
├────────────────────────────────────────────────┤
│           INFO ZONE                            │  Expandable
│ Dataset Statistics & Source Info              │  Height: 50px
├────────────────────────────────────────────────┤
│        METRICS ZONE                            │  Fixed
│ 5 KPI Cards: Revenue|Margin|SKUs|Stores|Return│ Height: 80px
├────────────────────────────────────────────────┤
│       CONTROLS ZONE                            │  Fixed
│ View Toggle (Executive|Operations)            │  Height: 40px
├────────────────────────────────────────────────┤
│          MAIN ZONE                             │  Dynamic
│ Tab content (Charts, Tables, Analysis)        │  Height: 600px+
│ ┌─────────────────────────────────────────┐   │
│ │ Trends | Geographic | Categories | ...  │   │
│ ├─────────────────────────────────────────┤   │
│ │ [Charts and Visualizations]             │   │
│ │ [Interactive elements]                  │   │
│ │ [Data tables]                           │   │
│ └─────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

---

## 🎯 Quick Reference Card

```
╔════════════════════════════════════════╗
║  CUSTOM DATA UPLOAD QUICK REFERENCE    ║
╠════════════════════════════════════════╣
║                                        ║
║ DEFAULT: Pre-Built Data               ║
║ SWITCH: Select "📤 Upload Custom Data"║
║                                        ║
║ UPLOAD: 4 Required CSV Files           ║
║ ├─ Products                            ║
║ ├─ Stores                              ║
║ ├─ Sales                               ║
║ └─ Inventory                           ║
║                                        ║
║ OPTIONAL: Issues CSV                  ║
║                                        ║
║ REQUIRED COLUMNS:                      ║
║ ├─ Products: product_id, category,     ║
║ │            brand, unit_cost_aed      ║
║ ├─ Stores: store_id, city, channel    ║
║ ├─ Sales: order_id, product_id,       ║
║ │         store_id, qty,               ║
║ │         selling_price_aed            ║
║ └─ Inventory: product_id, store_id,   ║
║              stock_on_hand             ║
║                                        ║
║ VALIDATE: All IDs must match           ║
║ GENERATE: python create_sample_dataset.py
║ START: streamlit run app.py            ║
║                                        ║
╚════════════════════════════════════════╝
```

---

This visual guide helps users understand the flow, architecture, and usage of the custom dataset upload feature at a glance!
