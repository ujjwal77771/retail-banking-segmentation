"""
prepare_data.py
===============
Loads the REAL UCI Online Retail dataset (541,909 actual transactions from a
UK-based retailer, Dec 2010 - Dec 2011) and transforms it into the same
customers.csv / transactions.csv shape used by the Power BI dashboard.

Source: UCI Machine Learning Repository
        https://archive.ics.uci.edu/dataset/352/online-retail
Licence: Creative Commons Attribution 4.0 (CC BY 4.0)
         — freely usable for academic & portfolio projects.

About the data
--------------
- 541,909 rows of real invoices (NOT synthetic)
- 4,373 unique real customers across UK, Europe, and globally
- Real product descriptions, quantities, unit prices, invoice dates
- Genuine cancellations (InvoiceNo starting with 'C')
- Some records with missing CustomerID (anonymous purchases)

What this script does
---------------------
1. Loads the raw Excel file
2. Cleans: drops anonymous customers, removes cancellations, removes
   negative-quantity returns, removes unit price = 0 (free samples)
3. Creates a TotalAmount column (Quantity * UnitPrice)
4. Derives a Month column (YYYY-MM) for cohort analysis
5. Exports customers.csv (demographic stub + join date)
6. Exports transactions.csv in the exact schema Power BI expects
"""

import os
import sys
import pandas as pd

RAW_EXCEL = "data/online_retail_raw/Online Retail.xlsx"
OUT_DIR   = "data"

# ── Sanity check ─────────────────────────────────────────────
if not os.path.exists(RAW_EXCEL):
    print("[ERROR] Raw Excel not found at:", RAW_EXCEL)
    print("Run the download step first (see README).")
    sys.exit(1)

print("=" * 60)
print("  UCI Online Retail -> Power BI Prep Script")
print("  (Real data: 541,909 transactions, 4,373 customers)")
print("=" * 60)

# ── 1. Load ───────────────────────────────────────────────────
print("\n[1/5] Loading Excel (this takes ~30s for 541k rows)...")
raw = pd.read_excel(RAW_EXCEL, dtype={"CustomerID": str})
print(f"      Loaded {len(raw):,} rows x {raw.shape[1]} columns")

# ── 2. Clean ──────────────────────────────────────────────────
print("[2/5] Cleaning...")

# Drop rows with no customer ID (anonymous walk-in purchases)
df = raw.dropna(subset=["CustomerID"]).copy()
print(f"      After removing anonymous purchases : {len(df):,} rows")

# Drop cancellations (InvoiceNo starts with 'C')
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
print(f"      After removing cancellations       : {len(df):,} rows")

# Drop rows where Quantity <= 0 or UnitPrice <= 0
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
print(f"      After removing returns/free items  : {len(df):,} rows")

# Drop duplicates
df = df.drop_duplicates()
print(f"      After dropping duplicates          : {len(df):,} rows")

# ── 3. Feature engineering ────────────────────────────────────
print("[3/5] Engineering features...")

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["TransactionDate"] = df["InvoiceDate"].dt.strftime("%Y-%m-%d")
df["Month"]           = df["InvoiceDate"].dt.strftime("%Y-%m")
df["TotalAmount"]     = (df["Quantity"] * df["UnitPrice"]).round(2)

# ── 4. Build transactions.csv ─────────────────────────────────
print("[4/5] Building transactions.csv...")

# Rename & select columns to match the Power BI schema
txn_df = df.reset_index(drop=True).copy()
txn_df["TransactionID"] = ["TXN_" + str(i).zfill(7) for i in range(1, len(txn_df) + 1)]
txn_df["CustomerID"]    = "CUST_" + txn_df["CustomerID"].str.strip().str.zfill(6)
txn_df["TransactionType"] = "Invoice"   # Real data doesn't have channel info
txn_df["MerchantCategory"] = txn_df["Description"].fillna("Unknown").str.strip().str.title()
txn_df["Amount"]           = txn_df["TotalAmount"]
txn_df["IsReversal"]       = 0

transactions = txn_df[[
    "TransactionID", "CustomerID", "TransactionDate", "Month",
    "TransactionType", "MerchantCategory", "Amount", "IsReversal",
    # Bonus columns (real data has these — great for deeper analysis)
    "InvoiceNo", "StockCode", "Quantity", "UnitPrice", "Country"
]]

# ── 5. Build customers.csv ────────────────────────────────────
print("[5/5] Building customers.csv...")

cust_ids    = transactions["CustomerID"].unique()
country_map = (
    df.assign(CustomerID="CUST_" + df["CustomerID"].str.strip().str.zfill(6))
      .groupby("CustomerID")["Country"]
      .agg(lambda x: x.mode()[0])
      .to_dict()
)
first_txn_map = (
    df.assign(CustomerID="CUST_" + df["CustomerID"].str.strip().str.zfill(6))
      .groupby("CustomerID")["InvoiceDate"]
      .min()
      .dt.strftime("%Y-%m-%d")
      .to_dict()
)

customers = pd.DataFrame({
    "CustomerID" : cust_ids,
    "Country"    : [country_map.get(c, "Unknown") for c in cust_ids],
    "JoinDate"   : [first_txn_map.get(c, "2010-12-01") for c in cust_ids],
    # The real dataset does not include demographics (anonymised by law)
    "Age"        : "N/A",
    "Gender"     : "N/A",
    "IncomeBand" : "N/A",
}).fillna("N/A")

# ── Save ──────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)
customers.to_csv(f"{OUT_DIR}/customers.csv", index=False)
transactions.to_csv(f"{OUT_DIR}/transactions.csv", index=False)

print("\n[DONE]")
print(f"   Customers    : {len(customers):>6,}  ->  {OUT_DIR}/customers.csv")
print(f"   Transactions : {len(transactions):>6,}  ->  {OUT_DIR}/transactions.csv")
print(f"   Countries    : {customers['Country'].nunique()} unique countries")
print(f"   Date range   : {transactions['TransactionDate'].min()}  to  {transactions['TransactionDate'].max()}")
print(f"   Amount range : GBP {transactions['Amount'].min():.2f}  to  GBP {transactions['Amount'].max():.2f}")
print("=" * 60)
print("\nNOTE: Age / Gender / IncomeBand are 'N/A' because the real")
print("UCI dataset does not include customer demographics.")
print("This is normal — real banking data is anonymised by law.")
