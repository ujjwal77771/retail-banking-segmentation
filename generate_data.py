import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

print("Generating realistic bank transaction data...")

# Set random seed for reproducibility
np.random.seed(42)

# Parameters
NUM_CUSTOMERS = 5000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2023, 12, 31)

# 1. Generate Customers
cust_ids = [f"CUST_{str(i).zfill(5)}" for i in range(1, NUM_CUSTOMERS + 1)]
ages = np.random.randint(18, 75, NUM_CUSTOMERS)
genders = np.random.choice(['M', 'F', 'Other'], NUM_CUSTOMERS, p=[0.55, 0.43, 0.02])
cities = np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Pune', 'Hyderabad', 'Chennai'], NUM_CUSTOMERS)

# Assign hidden segments to create realistic data patterns
# 0: Champions (high freq, recent, high value)
# 1: Churning (high past freq, nothing recent)
# 2: New/Low Value (low freq, recent, low value)
# 3: Average (medium everything)
segments = np.random.choice([0, 1, 2, 3], NUM_CUSTOMERS, p=[0.15, 0.20, 0.25, 0.40])

customers = pd.DataFrame({
    'CustomerID': cust_ids,
    'Age': ages,
    'Gender': genders,
    'City': cities,
    'Hidden_Segment': segments
})

# 2. Generate Transactions
transactions = []
txn_id_counter = 1

print("Simulating 12 months of transaction history...")

for _, row in customers.iterrows():
    cid = row['CustomerID']
    seg = row['Hidden_Segment']
    
    if seg == 0: # Champions
        num_txns = np.random.randint(50, 150)
        max_date = END_DATE - timedelta(days=np.random.randint(0, 10)) # Very recent
        amounts = np.random.lognormal(mean=7.0, sigma=1.0, size=num_txns)
    elif seg == 1: # Churning
        num_txns = np.random.randint(30, 100)
        max_date = END_DATE - timedelta(days=np.random.randint(60, 180)) # Stopped months ago
        amounts = np.random.lognormal(mean=6.5, sigma=1.0, size=num_txns)
    elif seg == 2: # Low Value
        num_txns = np.random.randint(5, 20)
        max_date = END_DATE - timedelta(days=np.random.randint(0, 30))
        amounts = np.random.lognormal(mean=5.0, sigma=0.8, size=num_txns)
    else: # Average
        num_txns = np.random.randint(20, 60)
        max_date = END_DATE - timedelta(days=np.random.randint(0, 45))
        amounts = np.random.lognormal(mean=6.0, sigma=1.0, size=num_txns)
        
    # Generate random dates for this customer up to their max_date
    date_range = (max_date - START_DATE).days
    
    for i in range(num_txns):
        if date_range > 0:
            random_days = np.random.randint(0, date_range)
            txn_date = START_DATE + timedelta(days=random_days)
            
            # Txn type
            txn_type = np.random.choice(['POS', 'UPI', 'ATM', 'Bill Pay', 'E-Comm'], p=[0.3, 0.4, 0.1, 0.1, 0.1])
            
            transactions.append({
                'TransactionID': f"TXN_{str(txn_id_counter).zfill(7)}",
                'CustomerID': cid,
                'TransactionDate': txn_date.strftime("%Y-%m-%d"),
                'Amount': round(amounts[i], 2),
                'TransactionType': txn_type
            })
            txn_id_counter += 1

txn_df = pd.DataFrame(transactions)

# Clean up customers table (drop hidden segment)
customers = customers.drop(columns=['Hidden_Segment'])

# Create outputs directory
os.makedirs("data", exist_ok=True)
customers.to_csv("data/customers.csv", index=False)
txn_df.to_csv("data/transactions.csv", index=False)

print(f"Done! Generated {len(customers):,} customers and {len(txn_df):,} transactions.")
print(f"Files saved to data/customers.csv and data/transactions.csv")
