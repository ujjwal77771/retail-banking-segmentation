# Power BI Build Instructions

Follow these exact steps to build the Axis BIU-level dashboard from scratch.

## Phase 1: Data Import & Python Integration
1. Open Power BI Desktop.
2. Click **Get Data -> Text/CSV** and load `data/customers.csv`.
3. Click **Get Data -> Text/CSV** and load `data/transactions.csv`.
4. Click **Transform Data** to open Power Query Editor.
5. In Power Query, click on the `transactions` query.
6. We need to aggregate it to RFM. Go to **Transform -> Group By**:
   - Group by: `CustomerID`
   - New Column 1: `Frequency`, Operation: `Count Rows`
   - New Column 2: `Monetary`, Operation: `Sum`, Column: `Amount`
   - New Column 3: `MaxDate`, Operation: `Max`, Column: `TransactionDate`
7. Add a Custom Column for **Recency**:
   - Formula: `Duration.Days(#date(2023,12,31) - Date.From([MaxDate]))`
8. Now, the Elite Flex. In the Transform ribbon, click **Run Python script**. Paste this exact code:

```python
# 'dataset' holds the input data from Power BI
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Drop missing
df = dataset.dropna(subset=['Recency', 'Frequency', 'Monetary'])

# Scale data
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df[['Recency', 'Frequency', 'Monetary']])

# Run K-Means
kmeans = KMeans(n_clusters=4, random_state=42)
df['Cluster'] = kmeans.fit_predict(scaled_features)

# Assign readable labels based on business logic
# (Note: Cluster IDs might shuffle, you can map them dynamically or just return the ID for now)
def label_segment(row):
    if row['Recency'] < 30 and row['Frequency'] > 50: return 'Champions'
    if row['Recency'] > 90 and row['Frequency'] > 30: return 'At Risk / Churning'
    if row['Frequency'] < 10: return 'Low Value'
    return 'Average'

df['Segment'] = df.apply(label_segment, axis=1)
dataset = df
```
9. Expand the table that the Python script returns. Click **Close & Apply**.

## Phase 2: Data Modeling
1. Go to the **Model View** (the relationship web icon on the left).
2. Drag `CustomerID` from `customers` to `CustomerID` in your new clustered table to create a 1-to-1 relationship.

## Phase 3: The "What-If" Scenario Parameter
1. Go to the **Modeling** ribbon -> **New Parameter** -> **Numeric Range**.
2. Name it: `Retention Offer Cost`.
3. Minimum: `0`, Maximum: `2000`, Increment: `100`, Default: `500`.
4. Create a New Measure for ROI:
```dax
Campaign ROI = 
VAR TotalAtRisk = CALCULATE(COUNTROWS(customers), 'transactions'[Segment] = "At Risk / Churning")
VAR ExpectedSaveRate = 0.30 // Assume 30% of people we give the offer to will stay
VAR AverageValue = CALCULATE(AVERAGE('transactions'[Monetary]), 'transactions'[Segment] = "At Risk / Churning")
VAR CostOfCampaign = TotalAtRisk * 'Retention Offer Cost'[Retention Offer Cost Value]
VAR RevenueSaved = (TotalAtRisk * ExpectedSaveRate) * AverageValue
RETURN RevenueSaved - CostOfCampaign
```

## Phase 4: Building the Visuals
1. **The Executive Overview**: 
   - Add KPI Cards for: Total Customers, Total Transactions, Average Monetary Value.
2. **The Segmentation Scatter Plot**: 
   - Add a Scatter Chart. 
   - X-Axis: `Recency`, Y-Axis: `Frequency`. 
   - Bubble Size: `Monetary`. 
   - Legend: `Segment` (from your Python script output).
3. **The What-If Dashboard**:
   - Put the `Retention Offer Cost` slider on the page.
   - Put a KPI Card showing `Campaign ROI`.
   - As you drag the slider, the ROI updates instantly.

## How to talk about this in the interview:
"I didn't just build a static report. I ran a K-Means clustering algorithm *inside* Power Query using Python to properly segment the customers based on distance from the centroid, rather than arbitrary business rules. Then, I used DAX What-If parameters so the marketing head can simulate the profitability of different cash-back retention offers before actually launching the campaign."
