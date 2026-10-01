# Retail Banking Customer Segmentation & Churn Dashboard 🏦

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow?logo=powerbi&logoColor=black)
![scikit-learn](https://img.shields.io/badge/scikit--learn-KMeans-orange?logo=scikit-learn&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Data](https://img.shields.io/badge/Data-Real%20UCI%20Dataset-red)

Hey! This is one of my personal portfolio projects where I tried to build something that actually looks like a real analyst would use at a bank — not just another bar chart on dummy data.

The idea is simple: banks have thousands of customers but a limited retention budget. So *which* customers do you spend money on? I used **RFM analysis + K-Means clustering** to automatically group customers by behaviour, then built a Power BI dashboard with a live What-If slider so a marketing manager can drag it and instantly see the ROI of a cash-back campaign.

The cool part — the ML model runs **inside Power BI itself** via Python integration. No external pipeline needed.

---

## What does it actually do?

It takes **392,692 real transactions** from the UCI Online Retail dataset and:

1. Cleans the raw data (removes cancellations, anonymous purchases, zero-price items)
2. Calculates each customer's **Recency, Frequency, and Monetary (RFM)** values
3. Runs **K-Means clustering** (with StandardScaler normalisation — important because GBP amounts and days-since-last-purchase are on completely different scales) to find 4 natural customer groups
4. Labels each group with a business name: Champions, At Risk, Low Value, Average
5. Shows everything in a 4-page Power BI dashboard with an interactive ROI calculator

---

## The dataset

> **UCI Online Retail Dataset** — real transaction records from a UK-based gift retailer, published as part of academic research.
>
> Chen, D., Sain, S.L., & Guo, K. (2012). *Data mining for the online retail industry.* Journal of Database Marketing, 19(3), 197–208. UCI ML Repository (CC BY 4.0).

| Stat | Value |
|------|-------|
| Customers | 4,338 real customers |
| Transactions | 392,692 rows after cleaning |
| Countries | 37 (UK, Germany, France, ...) |
| Date range | Dec 2010 – Dec 2011 |
| Amount currency | GBP (£) |

Note: The dataset doesn't have demographics like age or gender — that's normal, real customer data is anonymised by law (GDPR/PCI-DSS).

---

## Project structure

```
retail-banking-segmentation/
│
├── prepare_data.py           ← run this first! cleans the real UCI data
├── generate_data.py          ← synthetic fallback (offline use)
├── POWER_BI_INSTRUCTIONS.md  ← step-by-step guide to build the dashboard
├── SETUP.md                  ← how to download the raw data file
│
└── data/
    ├── customers.csv          ← 4,338 real customers
    ├── transactions.csv       ← 392,692 real transactions
    └── rfm_segments.csv       ← pre-computed RFM + cluster labels
```

---

## Quick start

### Step 1 — Download the raw Excel (one time only)

```powershell
# Windows PowerShell
Invoke-WebRequest -Uri "https://archive.ics.uci.edu/static/public/352/online+retail.zip" `
    -OutFile "data\online_retail.zip"
Expand-Archive -Path "data\online_retail.zip" -DestinationPath "data\online_retail_raw"
```

```bash
# Mac / Linux
curl -L "https://archive.ics.uci.edu/static/public/352/online+retail.zip" -o data/online_retail.zip
unzip data/online_retail.zip -d data/online_retail_raw
```

### Step 2 — Install dependencies

```bash
pip install pandas scikit-learn openpyxl
```

### Step 3 — Clean and prepare the data

```bash
python prepare_data.py
```

### Step 4 — Open Power BI and follow the guide

Open `POWER_BI_INSTRUCTIONS.md` — it walks you through every single click.

---

## The 4 customer segments

| Segment | What it means | What to do with them |
|---------|--------------|---------------------|
| 🏆 **Champions** | Bought recently, buy often, spend the most | Reward them, ask for reviews, offer early access |
| ⚠️ **At Risk / Churning** | Used to buy a lot but went quiet (60+ days) | Send a personalised win-back offer ASAP |
| 💤 **Low Value** | Rarely buy, small basket size | Low priority — maybe a nudge campaign |
| 😐 **Average** | Solid but nothing special | Cross-sell, upsell, try to move them up |

---

## Dashboard pages

| Page | What's on it |
|------|-------------|
| Executive Overview | KPI cards, revenue by country map, monthly trend line |
| Customer Segmentation | RFM scatter plot (coloured by segment), segment breakdown donut |
| Cohort & Retention | Monthly active users, revenue by month stacked by segment |
| Campaign ROI Simulator | Slider → drag the offer cost → ROI updates live |

---

## Why the ML part actually works

The key thing I learned building this: **you can't just throw RFM values into K-Means raw.**

Monetary values are in the thousands (£ amounts) and Recency is in single/double digits (days). Without `StandardScaler`, the algorithm basically ignores Recency entirely because the scale difference is so massive. Normalising first is what makes the clusters actually meaningful.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[['Recency', 'Frequency', 'Monetary']])

km = KMeans(n_clusters=4, random_state=42, n_init=10)
df['Cluster'] = km.fit_predict(X_scaled)
```

---

## Tech stack

- **Python** — pandas, scikit-learn, openpyxl
- **Power BI Desktop** — Power Query (M), DAX measures, What-If parameters
- **ML** — K-Means clustering, StandardScaler normalisation
- **Analysis** — RFM segmentation, cohort retention, campaign ROI modelling

---

## Things I want to add later

- [ ] Elbow method / silhouette score plot to justify k=4
- [ ] CLTV (Customer Lifetime Value) regression model
- [ ] Connect to a live PostgreSQL database instead of CSVs
- [ ] Churn probability score using logistic regression
- [ ] Dashboard screenshots once the Power BI file is done

---

## License

MIT — see [LICENSE](LICENSE). Free to use, fork, or build on top of.

---

*Built by Harsh Raj Pandey — feel free to connect on [LinkedIn](https://linkedin.com/in/) or raise an issue if something's broken!*
