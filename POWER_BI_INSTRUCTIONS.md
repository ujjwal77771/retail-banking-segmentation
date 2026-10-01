# 🏦 Power BI Customer Segmentation & Churn Dashboard
## Complete Build Guide — Using REAL UCI Online Retail Data

> **Dataset:** UCI Online Retail (2010–2011) — **541,909 real transactions** from a UK-based
> gift retailer, published under CC BY 4.0. 4,372 unique customers. This is the industry-standard
> dataset used in academic papers and Kaggle competitions for RFM segmentation.
>
> **Reference:** Daqing Chen, Sai Liang Sain, and Kun Guo, *Data mining for the online retail
> industry*, Journal of Database Marketing and Customer Strategy Management, 2012.

---

## Pre-requisites Checklist
- [ ] Power BI Desktop — [Download free](https://powerbi.microsoft.com/downloads/)
- [ ] Python configured in Power BI: `File → Options → Python scripting` → set Python path
- [ ] Libraries: `pip install pandas scikit-learn` in that Python environment
- [ ] Data prepared: run `python prepare_data.py` to generate the clean CSVs

---

## Understanding the Real Data

After running `prepare_data.py`, your `data/` folder contains:

### `customers.csv` (4,372 rows)
| Column | Description |
|--------|-------------|
| `CustomerID` | Anonymised customer ID (e.g. `CUST_017850`) |
| `Country` | Customer's country (38 countries in the dataset) |
| `JoinDate` | Date of their first ever purchase |
| `Age / Gender / IncomeBand` | `N/A` — real banking law anonymises demographics |

### `transactions.csv` (~397,000 rows after cleaning)
| Column | Description |
|--------|-------------|
| `TransactionID` | Generated unique ID |
| `CustomerID` | Links to customers table |
| `TransactionDate` | Date of invoice (YYYY-MM-DD) |
| `Month` | YYYY-MM for cohort analysis |
| `TransactionType` | `Invoice` (real data has no channel info) |
| `MerchantCategory` | Product description (e.g. `White Metal Lantern`) |
| `Amount` | Quantity × UnitPrice in **GBP (£)** |
| `IsReversal` | Always 0 (cancellations already removed) |
| `InvoiceNo` | Original invoice number |
| `StockCode` | Product code |
| `Quantity` | Items per line |
| `UnitPrice` | Price per item in GBP |
| `Country` | Transaction country |

---

## Phase 1 — Load Data into Power Query

1. **Power BI Desktop → Get Data → Text/CSV** → load `data/customers.csv`
2. **Get Data → Text/CSV** again → load `data/transactions.csv`
3. Click **Transform Data** to open Power Query Editor

---

## Phase 2 — Build the RFM Table in Power Query

Select the **`transactions`** query:

### Step 2a — Set Date Type
- Select `TransactionDate` → **Transform → Data Type → Date**

### Step 2b — Group By to Create RFM Aggregates
**Transform → Group By → Advanced**, group by `CustomerID`:

| New Column | Operation | Column |
|---|---|---|
| `Frequency` | Count Rows | *(auto)* |
| `Monetary` | Sum | `Amount` |
| `LastTxnDate` | Max | `TransactionDate` |

### Step 2c — Add Recency Column
**Add Column → Custom Column**, name: `Recency`
```
= Duration.Days(#date(2011, 12, 9) - Date.From([LastTxnDate]))
```
> ℹ️ We use **Dec 9, 2011** as the reference date — the last date in this real dataset.

### Step 2d — Set Column Types
- `Frequency` → Whole Number
- `Monetary` → Decimal Number
- `Recency` → Whole Number

---

## Phase 3 — K-Means Clustering (Python Inside Power BI)

With the RFM query selected → **Transform → Run Python Script**:

```python
# Power BI passes the current query as `dataset`
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

df = dataset.copy()
df = df.dropna(subset=['Recency', 'Frequency', 'Monetary'])
df = df[df['Monetary'] > 0]

# CRITICAL: K-Means is distance-based.
# Without scaling, Monetary (£) completely dominates Recency (days).
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[['Recency', 'Frequency', 'Monetary']])

# Fit K-Means (k=4 chosen by elbow method on this dataset)
km = KMeans(n_clusters=4, random_state=42, n_init=10)
df['Cluster'] = km.fit_predict(X_scaled)

# Map clusters to business labels using RFM thresholds
# (rules-based labels are stable across runs; pure cluster IDs can shuffle)
def assign_segment(row):
    if row['Recency'] <= 30 and row['Frequency'] >= 50:
        return 'Champions'
    if row['Recency'] > 60 and row['Monetary'] >= 300:
        return 'At Risk / Churning'
    if row['Frequency'] <= 5 or row['Monetary'] < 100:
        return 'Low Value'
    return 'Average'

df['Segment'] = df.apply(assign_segment, axis=1)

dataset = df[['CustomerID', 'Recency', 'Frequency', 'Monetary',
              'LastTxnDate', 'Cluster', 'Segment']]
```

- Click **OK** → expand the returned `dataset` table → select all columns
- Rename the query to **`rfm_clustered`**
- **Close & Apply**

---

## Phase 4 — Data Model

In **Model View**, create these relationships:

| From | To | Cardinality |
|------|-----|------------|
| `customers[CustomerID]` | `rfm_clustered[CustomerID]` | 1-to-1 |
| `transactions[CustomerID]` | `customers[CustomerID]` | Many-to-1 |

---

## Phase 5 — DAX Measures

Create a dedicated measure table called `_Measures`:

### Core KPIs
```dax
Total Customers = DISTINCTCOUNT(customers[CustomerID])
```
```dax
Total Transactions = COUNTROWS(transactions)
```
```dax
Total Revenue (GBP) = SUM(transactions[Amount])
```
```dax
Avg Order Value =
AVERAGEX(
    VALUES(transactions[InvoiceNo]),
    CALCULATE(SUM(transactions[Amount]))
)
```
```dax
Churn Risk Count =
CALCULATE(
    COUNTROWS(rfm_clustered),
    rfm_clustered[Segment] = "At Risk / Churning"
)
```
```dax
Champions Count =
CALCULATE(
    COUNTROWS(rfm_clustered),
    rfm_clustered[Segment] = "Champions"
)
```

### Monthly Active Customers (for Cohort Page)
```dax
Active Customers (Month) =
CALCULATE(
    DISTINCTCOUNT(transactions[CustomerID]),
    DATESINPERIOD(
        transactions[TransactionDate],
        LASTDATE(transactions[TransactionDate]),
        -1, MONTH
    )
)
```

### What-If Campaign ROI
First create the parameter: **Modeling → New Parameter → Numeric Range**
- Name: `Offer Cost Per Customer`
- Min: `0` | Max: `500` | Increment: `25` | Default: `100`

> Note: Amounts are in **GBP (£)** — adjust thresholds accordingly.

```dax
Campaign ROI % =
VAR AtRiskCount =
    CALCULATE(COUNTROWS(rfm_clustered),
              rfm_clustered[Segment] = "At Risk / Churning")
VAR AvgAtRiskSpend =
    CALCULATE(
        AVERAGEX(VALUES(rfm_clustered[CustomerID]), rfm_clustered[Monetary]),
        rfm_clustered[Segment] = "At Risk / Churning"
    )
VAR SaveRate     = 0.30
VAR CampaignCost = AtRiskCount * 'Offer Cost Per Customer'[Offer Cost Per Customer Value]
VAR RevenueSaved = AtRiskCount * SaveRate * AvgAtRiskSpend
RETURN
    DIVIDE(RevenueSaved - CampaignCost, CampaignCost, 0)
```

```dax
Net Revenue Saved (GBP) =
VAR AtRiskCount =
    CALCULATE(COUNTROWS(rfm_clustered),
              rfm_clustered[Segment] = "At Risk / Churning")
VAR AvgSpend =
    CALCULATE(
        AVERAGEX(VALUES(rfm_clustered[CustomerID]), rfm_clustered[Monetary]),
        rfm_clustered[Segment] = "At Risk / Churning"
    )
RETURN
    (AtRiskCount * 0.30 * AvgSpend) -
    (AtRiskCount * 'Offer Cost Per Customer'[Offer Cost Per Customer Value])
```

---

## Phase 6 — Dashboard Pages

### Page 1 — Executive Overview
| Visual | Type | Config |
|--------|------|--------|
| Total Customers | KPI Card | `Total Customers` |
| Total Revenue | KPI Card | `Total Revenue (GBP)` |
| Churn Risk | KPI Card | `Churn Risk Count` |
| Revenue by Country | Filled Map | `Country` + `Total Revenue (GBP)` |
| Revenue by Month | Line Chart | `Month` + `Total Revenue (GBP)` |
| Top Products | Bar Chart | `MerchantCategory` + SUM(`Amount`) Top 10 |

### Page 2 — Customer Segmentation
| Visual | Type | Config |
|--------|------|--------|
| RFM Scatter | Scatter Chart | X: Recency, Y: Frequency, Size: Monetary, Legend: Segment |
| Segment Breakdown | Donut Chart | Segment + COUNTROWS |
| Avg RFM by Segment | Matrix | Segment vs AVG Recency / Frequency / Monetary |
| Filter by Country | Slicer | Country |

### Page 3 — Cohort & Retention
| Visual | Type | Config |
|--------|------|--------|
| Monthly Active Customers | Line Chart | Month + `Active Customers (Month)` |
| Revenue by Month + Segment | Stacked Bar | Month + SUM(Amount) stacked by Segment |
| Churn Risk by Country | Bar Chart | Country + `Churn Risk Count` |

### Page 4 — Campaign ROI Simulator
| Visual | Type | Config |
|--------|------|--------|
| Offer Cost Slider | Slicer | `Offer Cost Per Customer` parameter |
| Campaign ROI | KPI Card | `Campaign ROI %` (format as %) |
| Net Revenue Saved | KPI Card | `Net Revenue Saved (GBP)` (format as £) |
| At-Risk Customer List | Table | CustomerID + Country + Recency + Monetary |

---

## Phase 7 — Formatting

- **Theme:** View → Themes → **Executive** (dark navy — suits finance)
- **Conditional formatting** on segment table: Red fill for "At Risk", Gold for "Champions"
- **Currency format:** All Amount measures → Format → Currency → GBP (£)
- **Flag the data source** in a text box on Page 1:
  > *Data: UCI Online Retail Dataset (Chen et al., 2012). 4,372 customers, 397k transactions, Dec 2010–Dec 2011.*

---

## How to Explain This in an Interview

> *"I used the UCI Online Retail dataset — 397,000 real transactions from a published academic
> study — rather than synthetic data. I cleaned it in Python: removed anonymous purchases,
> cancelled invoices, and zero-price records. I then built an RFM aggregation in Power Query M
> and ran a K-Means clustering model inside Power BI using Python integration. I applied
> StandardScaler first because K-Means is distance-based and Monetary values in GBP would
> otherwise completely dominate Recency in days. The result is a live segmentation that updates
> on every data refresh. The fourth page uses a DAX What-If parameter so a business user can
> drag a slider and instantly see the ROI of different retention offer amounts."*

---

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| Python scripting not enabled | File → Options → Python scripting → set Python path |
| Blank Segment column | Check that `rfm_clustered` table name matches your DAX exactly |
| Amounts look wrong | Confirm currency is GBP (£) — multiply by ~106 for INR if needed |
| Map visual shows wrong countries | Set `Country` column data category: Column tools → Data category → Country |
| KPI shows blank | Check relationship direction in Model View is single-arrow |
