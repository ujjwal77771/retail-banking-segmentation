# Retail Banking Customer Segmentation & Churn Dashboard

A highly explainable, business-focused **Power BI** project designed for retail banking analytics. 
Instead of a black-box machine learning model, this project uses a classic **RFM (Recency, Frequency, Monetary)** model combined with K-Means clustering (via Python integrated directly into Power Query) to group customers based on their true spending behavior.

## 🎯 Business Problem
The bank has thousands of retail customers, but a limited marketing and retention budget. We need to instantly identify:
1. **The Champions:** Our most valuable, high-frequency customers.
2. **The Churn Risks:** High-value customers who suddenly stopped transacting over the last 90 days.
3. **The Low Value:** Customers who transact rarely and keep low balances.

## 🛠️ Tech Stack
*   **Python:** Data generation and K-Means Clustering (`pandas`, `scikit-learn`).
*   **Power BI:** Data modeling, Power Query (M), Advanced DAX.
*   **Business Logic:** RFM Analysis, Cohort Retention, What-If Scenario Analysis.

## 🚀 Advanced Features Used
1.  **Python in Power Query:** Clustering algorithms run natively inside Power BI's data prep layer.
2.  **Cohort Analysis (DAX):** Time-intelligence tracking to see customer retention drop-off month over month.
3.  **What-If Parameters:** A dynamic slider allowing the business user to model the ROI of a cash-back retention campaign.

---

## 📂 Project Structure
*   `generate_data.py`: Creates realistic banking datasets (`customers.csv` and `transactions.csv`) with hidden transaction patterns.
*   `POWER_BI_INSTRUCTIONS.md`: Complete, step-by-step guide with exact DAX formulas to recreate the dashboard.
*   `data/`: Directory where the raw CSVs are saved.

## 📊 How to explain this in an interview
> *"I built a Power BI dashboard to help the marketing team allocate their retention budget. Instead of a standard report, I integrated a Python script directly into Power Query that runs a K-Means clustering algorithm over the customers' Recency, Frequency, and Monetary values. This automatically groups them into 4 distinct behavioral segments. I then wrote advanced DAX measures to build a Cohort Retention Heatmap and a What-If parameter, so the marketing manager can use a slider to simulate the financial ROI of a cash-back campaign on the 'At-Risk' segment."*
