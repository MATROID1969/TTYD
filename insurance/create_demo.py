#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

REFERENCE_DATE_IN_DATA = "2025-02-13"
TARGET_TODAY = "2016-01-21"


INPUT_CSV = "data/data.csv"
OUTPUT_CSV = "data/data_demo.csv"

REFERENCE_DATE_IN_DATA = "2025-02-13"
TARGET_TODAY = "2016-01-21"

# betöltés
df = pd.read_csv(INPUT_CSV)

# eltolás kiszámítása
ref_date = pd.to_datetime(REFERENCE_DATE_IN_DATA)
target_date = pd.to_datetime(TARGET_TODAY)

delta = target_date - ref_date
delta_days = delta.days

print(f"Dátumeltolás: {delta_days} nap")

# dátum oszlopok felismerése (ISO formátum miatt biztonságos)
date_columns = []
for col in df.columns:
    try:
        parsed = pd.to_datetime(df[col], format="%Y-%m-%d", errors="raise")
        date_columns.append(col)
    except Exception:
        continue

print("Eltolt dátumoszlopok:", date_columns)

# eltolás alkalmazása
for col in date_columns:
    df[col] = pd.to_datetime(df[col]) + pd.to_timedelta(delta_days, unit="D")
    df[col] = df[col].dt.strftime("%Y-%m-%d")

# mentés
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print("Demo adatbázis elkészült:", OUTPUT_CSV)


# In[ ]:




