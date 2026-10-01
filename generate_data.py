"""
generate_data.py
================
Generates realistic retail banking data for the Customer Segmentation & Churn Dashboard.
Produces: data/customers.csv  (5,000 rows)
          data/transactions.csv (~230,000 rows)

The data contains HIDDEN segment patterns so K-Means has genuine signal to find:
  - Segment 0 – Champions     (15%): High freq, recent, high monetary
  - Segment 1 – At-Risk/Churn (20%): High past freq, nothing recent (60-180 day gap)
  - Segment 2 – Low Value     (25%): Low freq, recent, low amounts
  - Segment 3 – Average       (40%): Medium on all three dimensions
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 55)
print("  Retail Banking Data Generator")
print("=" * 55)

# ── Reproducibility ──────────────────────────────────────────
np.random.seed(42)

# ── Config ───────────────────────────────────────────────────
NUM_CUSTOMERS = 5_000
START_DATE    = datetime(2023, 1, 1)
END_DATE      = datetime(2023, 12, 31)

CITIES         = ['Mumbai', 'Delhi', 'Bangalore', 'Pune', 'Hyderabad', 'Chennai',
                   'Kolkata', 'Ahmedabad', 'Jaipur', 'Surat']
CITY_WEIGHTS   = [0.20, 0.18, 0.15, 0.10, 0.10, 0.08, 0.07, 0.05, 0.04, 0.03]

TXN_TYPES      = ['UPI', 'POS', 'E-Comm', 'ATM', 'Bill Pay', 'NEFT/RTGS']
TXN_WEIGHTS    = [0.38, 0.28, 0.14, 0.09, 0.07, 0.04]

INCOME_BANDS   = ['Low', 'Middle', 'Upper-Middle', 'High']
OCCUPATIONS    = ['Salaried', 'Self-Employed', 'Student', 'Retired', 'Business Owner']

# ── 1. Generate Customers ─────────────────────────────────────
print("\n[1/3] Generating customer master data...")

cust_ids    = [f"CUST_{str(i).zfill(5)}" for i in range(1, NUM_CUSTOMERS + 1)]
ages        = np.random.randint(21, 72, NUM_CUSTOMERS)
genders     = np.random.choice(['Male', 'Female', 'Other'], NUM_CUSTOMERS, p=[0.54, 0.44, 0.02])
cities      = np.random.choice(CITIES, NUM_CUSTOMERS, p=CITY_WEIGHTS)
incomes     = np.random.choice(INCOME_BANDS, NUM_CUSTOMERS, p=[0.25, 0.45, 0.20, 0.10])
occupations = np.random.choice(OCCUPATIONS, NUM_CUSTOMERS, p=[0.50, 0.20, 0.10, 0.10, 0.10])
join_days   = np.random.randint(0, 3 * 365, NUM_CUSTOMERS)   # joined within last 3 years
join_dates  = [START_DATE - timedelta(days=int(d)) for d in join_days]

# Hidden segment label (stripped before saving — gives K-Means real patterns to find)
segments = np.random.choice([0, 1, 2, 3], NUM_CUSTOMERS, p=[0.15, 0.20, 0.25, 0.40])

customers = pd.DataFrame({
    'CustomerID':    cust_ids,
    'Age':           ages,
    'Gender':        genders,
    'City':          cities,
    'IncomeBand':    incomes,
    'Occupation':    occupations,
    'JoinDate':      [d.strftime("%Y-%m-%d") for d in join_dates],
    'Hidden_Segment': segments          # will be dropped before export
})

# ── 2. Generate Transactions ──────────────────────────────────
print("[2/3] Simulating 12 months of transaction history (this may take ~30 sec)...")

MERCHANT_CATEGORIES = {
    'UPI':       ['Grocery', 'Food Delivery', 'Utilities', 'Petrol', 'Misc'],
    'POS':       ['Retail', 'Restaurant', 'Pharmacy', 'Electronics', 'Clothing'],
    'E-Comm':    ['Amazon', 'Flipkart', 'Myntra', 'Nykaa', 'Electronics'],
    'ATM':       ['Cash Withdrawal'],
    'Bill Pay':  ['Electricity', 'Mobile Recharge', 'OTT', 'Insurance', 'Gas'],
    'NEFT/RTGS': ['Rent Transfer', 'Salary Credit', 'Investment', 'Loan EMI']
}

records = []
txn_counter = 1

for _, row in customers.iterrows():
    cid = row['CustomerID']
    seg = row['Hidden_Segment']

    # Segment-specific behaviour parameters
    if seg == 0:    # Champions
        n_txns    = np.random.randint(60, 150)
        recency   = np.random.randint(0, 10)          # transacted very recently
        mu, sigma = 7.2, 0.9                           # high amounts (lognormal)
    elif seg == 1:  # At-Risk / Churning
        n_txns    = np.random.randint(30, 90)
        recency   = np.random.randint(65, 180)         # last txn was months ago
        mu, sigma = 6.5, 1.0
    elif seg == 2:  # Low Value
        n_txns    = np.random.randint(5, 18)
        recency   = np.random.randint(0, 30)
        mu, sigma = 5.0, 0.8                           # low amounts
    else:           # Average
        n_txns    = np.random.randint(20, 55)
        recency   = np.random.randint(0, 45)
        mu, sigma = 6.1, 1.0

    latest_txn_date = END_DATE - timedelta(days=recency)
    date_span       = max((latest_txn_date - START_DATE).days, 1)
    amounts         = np.random.lognormal(mean=mu, sigma=sigma, size=n_txns).round(2)

    for i in range(n_txns):
        txn_date    = START_DATE + timedelta(days=int(np.random.randint(0, date_span)))
        txn_type    = np.random.choice(TXN_TYPES, p=TXN_WEIGHTS)
        merchant    = np.random.choice(MERCHANT_CATEGORIES[txn_type])
        is_reversal = np.random.random() < 0.02   # 2% reversal rate

        records.append({
            'TransactionID':      f"TXN_{str(txn_counter).zfill(7)}",
            'CustomerID':         cid,
            'TransactionDate':    txn_date.strftime("%Y-%m-%d"),
            'Month':              txn_date.strftime("%Y-%m"),
            'TransactionType':    txn_type,
            'MerchantCategory':   merchant,
            'Amount':             amounts[i] if not is_reversal else -round(amounts[i] * 0.9, 2),
            'IsReversal':         int(is_reversal),
        })
        txn_counter += 1

txn_df = pd.DataFrame(records)

# ── 3. Save Outputs ───────────────────────────────────────────
print("[3/3] Saving CSVs...")
os.makedirs("data", exist_ok=True)

customers_export = customers.drop(columns=["Hidden_Segment"])
customers_export.to_csv("data/customers.csv", index=False)
txn_df.to_csv("data/transactions.csv", index=False)

print("\n[DONE]")
print(f"   Customers    : {len(customers_export):>7,}  ->  data/customers.csv")
print(f"   Transactions : {len(txn_df):>7,}  ->  data/transactions.csv")
print(f"   Date range   : {START_DATE.date()}  to  {END_DATE.date()}")
print("=" * 55)
