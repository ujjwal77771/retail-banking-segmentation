"""
Compute RFM scores + K-Means clustering and print all metrics
for resume bullet points.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

SNAPSHOT_DATE = datetime(2023, 12, 31)

# ── Load data ──────────────────────────────────────────────────────────────────
txn = pd.read_csv("data/transactions.csv", parse_dates=["TransactionDate"])
cust = pd.read_csv("data/customers.csv")
print(f"Transactions loaded : {len(txn):,}")
print(f"Customers loaded    : {len(cust):,}")

# ── RFM Aggregation ────────────────────────────────────────────────────────────
rfm = txn.groupby("CustomerID").agg(
    Recency   = ("TransactionDate", lambda x: (SNAPSHOT_DATE - x.max()).days),
    Frequency = ("TransactionID",   "count"),
    Monetary  = ("Amount",          "sum")
).reset_index()

print(f"\nRFM Table Shape     : {rfm.shape}")
print(rfm.describe().round(2))

# ── Scale & Cluster ────────────────────────────────────────────────────────────
scaler = StandardScaler()
X = scaler.fit_transform(rfm[["Recency", "Frequency", "Monetary"]])

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
rfm["Cluster"] = kmeans.fit_predict(X)

# ── Quality Metrics ────────────────────────────────────────────────────────────
sil  = silhouette_score(X, rfm["Cluster"])
db   = davies_bouldin_score(X, rfm["Cluster"])
inertia = kmeans.inertia_

print(f"\n── Clustering Quality ──────────────────────")
print(f"  Silhouette Score         : {sil:.4f}  (1.0 = perfect separation)")
print(f"  Davies-Bouldin Index     : {db:.4f}  (0.0 = perfect, lower is better)")
print(f"  KMeans Inertia           : {inertia:,.0f}")

# ── Label Segments ─────────────────────────────────────────────────────────────
centroids = pd.DataFrame(
    scaler.inverse_transform(kmeans.cluster_centers_),
    columns=["Recency", "Frequency", "Monetary"]
)
print("\n── Raw Centroids (inverse-scaled) ──────────")
print(centroids.round(1))

# Rule: low Recency=recent, high Freq=active, high Monetary=valuable
segment_map = {}
for cid, c in centroids.iterrows():
    if c["Recency"] < 30 and c["Frequency"] > 50:
        segment_map[cid] = "Champions"
    elif c["Recency"] > 90 and c["Frequency"] > 30:
        segment_map[cid] = "At Risk / Churning"
    elif c["Frequency"] < 15:
        segment_map[cid] = "Low Value"
    else:
        segment_map[cid] = "Average / Developing"

rfm["Segment"] = rfm["Cluster"].map(segment_map)
print(f"\n  Segment Labels: {segment_map}")

# ── Segment Profile ────────────────────────────────────────────────────────────
profile = rfm.groupby("Segment").agg(
    Customers  = ("CustomerID",   "count"),
    Avg_Recency    = ("Recency",   "mean"),
    Avg_Frequency  = ("Frequency", "mean"),
    Avg_Monetary   = ("Monetary",  "mean"),
    Total_Revenue  = ("Monetary",  "sum")
).round(1).reset_index()

profile["Pct_Customers"] = (profile["Customers"] / profile["Customers"].sum() * 100).round(1)
profile["Revenue_Share_%"] = (profile["Total_Revenue"] / profile["Total_Revenue"].sum() * 100).round(1)

print("\n── Segment Breakdown ───────────────────────────────────────────────────")
print(profile.to_string(index=False))

# ── Churn Risk Financials ──────────────────────────────────────────────────────
at_risk = rfm[rfm["Segment"] == "At Risk / Churning"]
champs  = rfm[rfm["Segment"] == "Champions"]
print(f"\n── Key Business Metrics ────────────────────")
print(f"  Total customers analysed : {len(rfm):,}")
print(f"  At-Risk customers        : {len(at_risk):,}  ({len(at_risk)/len(rfm)*100:.1f}% of base)")
print(f"  Champions                : {len(champs):,}  ({len(champs)/len(rfm)*100:.1f}% of base)")
print(f"  Revenue at risk (At-Risk): INR {at_risk['Monetary'].sum():,.0f}")
print(f"  Champions revenue        : INR {champs['Monetary'].sum():,.0f}")
print(f"  Avg. days since last txn (At-Risk): {at_risk['Recency'].mean():.0f} days")
print(f"  Avg. txn freq (Champions): {champs['Frequency'].mean():.0f} txns/year")

# Save
rfm.to_csv("data/rfm_segments.csv", index=False)
print(f"\nSaved: data/rfm_segments.csv")
