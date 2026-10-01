## Setup

### 1. Download the raw data
The source file (~23 MB) is not stored in this repo. Download it once:

```bash
# Windows (PowerShell)
Invoke-WebRequest -Uri "https://archive.ics.uci.edu/static/public/352/online+retail.zip" `
    -OutFile "data\online_retail.zip"
Expand-Archive -Path "data\online_retail.zip" -DestinationPath "data\online_retail_raw"
```

```bash
# Mac / Linux
curl -L "https://archive.ics.uci.edu/static/public/352/online+retail.zip" -o data/online_retail.zip
unzip data/online_retail.zip -d data/online_retail_raw
```

### 2. Install Python dependencies
```bash
pip install pandas scikit-learn openpyxl
```

### 3. Clean and prepare the data
```bash
python prepare_data.py
```
This outputs `data/customers.csv` (4,338 rows) and `data/transactions.csv` (~392k rows).

### 4. Build the dashboard
Open `POWER_BI_INSTRUCTIONS.md` and follow the step-by-step guide.
