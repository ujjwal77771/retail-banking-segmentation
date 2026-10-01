# 🏦 Retail Banking Customer Segmentation & Churn Dashboard

> **Portfolio Project for Finance / Data Analytics Roles**
> Demonstrates: Python · scikit-learn · Power BI · Advanced DAX · RFM Analysis · K-Means Clustering

---

## 🎯 Business Problem

A retail bank has **5,000 active customers** and a fixed marketing budget. The question is:

> *"Which customers should we spend retention money on, and how much is that worth?"*

Without segmentation, the marketing team either treats everyone the same (wasteful) or relies on
gut-feel (error-prone). This dashboard provides a data-driven answer in seconds.

---

## 🔬 Methodology: RFM + K-Means

**RFM** stands for:

| Feature | Definition | High = Good? |
|---------|-----------|:---:|
| **R**ecency | Days since last transaction | ❌ (lower is better) |
| **F**requency | Total number of transactions | ✅ |
| **M**onetary | Total spend (₹) | ✅ |

K-Means clustering (k=4) groups customers into four behavioural segments by their distance from
cluster centroids in RFM space. Features are **StandardScaler-normalized** first — a critical step
because Recency (in days) and Monetary (in ₹) operate on completely different scales.

---

## 📂 Project Structure

```
retail-banking-segmentation/
│
├── generate_data.py          # Synthetic data generator (run this first)
├── POWER_BI_INSTRUCTIONS.md  # Full step-by-step build guide
├── README.md                 # This file
│
└── data/
    ├── customers.csv         # 5,000 customers with demographics
    └── transactions.csv      # ~230,000 transactions over 12 months
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Generation | Python 3, NumPy, pandas |
| Machine Learning | scikit-learn (KMeans, StandardScaler) |
| Data Viz / BI | Power BI Desktop |
| Query Language | Power Query M |
| Business Logic | DAX (Advanced — What-If parameters, DATESINPERIOD, AVERAGEX) |

---

## 🚀 Key Features

### 1. Python K-Means Inside Power Query
The clustering model runs **natively inside Power BI's data refresh pipeline** via the
`Run Python Script` step. This means every time the data refreshes, the segments update
automatically — no external ML pipeline needed.

### 2. Four-Page Dashboard Architecture
| Page | Purpose |
|------|---------|
| Executive Overview | C-suite KPIs: total customers, transactions, MAU trend |
| Customer Segmentation | RFM scatter plot coloured by segment, segment profile table |
| Cohort & Churn Analysis | Monthly active user retention, churn by city/channel |
| Campaign ROI Simulator | Interactive What-If slider for retention offer budget |

### 3. What-If Campaign ROI Slider (Advanced DAX)
A dynamic parameter slider lets the marketing head type in a ₹ offer cost per at-risk customer.
The DAX engine instantly recalculates:
- Total campaign spend
- Expected revenue saved (at an assumed 30% save rate)
- Net ROI as a percentage

---

## ⚡ Quick Start

```bash
# 1. Generate the data
python generate_data.py

# 2. Open Power BI Desktop
# 3. Follow POWER_BI_INSTRUCTIONS.md step by step
```

---

## 📊 Customer Segments (What K-Means Discovers)

| Segment | Recency | Frequency | Monetary | Strategy |
|---------|---------|-----------|----------|---------|
| **Champions** | < 30 days | High (50+) | High | Loyalty rewards, premium products |
| **At Risk / Churning** | > 60 days | Medium-High | Medium-High | Win-back offer, personal call |
| **Low Value** | Recent | Low (< 12) | Low | Activation nudges, UPI cashback |
| **Average** | Medium | Medium | Medium | Cross-sell, FD/RD offers |

---

## 💬 Interview Talking Points

> *"The core insight is that K-Means alone doesn't label clusters — you have to map them to business
> meaning. I wrote a `StandardScaler` normalization step first, then used RFM thresholds to assign
> readable names. On the Power BI side, I used DAX What-If parameters and `AVERAGEX` to build a
> live ROI simulator so a non-technical marketing manager can make budget decisions directly in the
> report without needing to run any code."*

---

## 🔮 Possible Extensions

- [ ] Add CLTV (Customer Lifetime Value) prediction using a regression model
- [ ] Pull live data from a PostgreSQL or Azure SQL database instead of CSVs
- [ ] Schedule automated refresh in Power BI Service with a gateway
- [ ] Add a churn probability score using logistic regression in the Python step

---

*Dataset is fully synthetic. All customer IDs, amounts, and behavioural patterns were
programmatically generated for portfolio demonstration purposes.*
