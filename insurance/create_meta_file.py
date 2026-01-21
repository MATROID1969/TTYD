#!/usr/bin/env python
# coding: utf-8

# In[19]:


import pandas as pd
import json
import ast
from pathlib import Path

INPUT_CSV = "data/data_source.csv"
CLEAN_CSV = "data/data.csv"
OUTPUT_JSON = "prompts/meta_context.json"


def canonicalize_dataframe(df: pd.DataFrame, meta: dict) -> pd.DataFrame:
    fields = {f["name"]: f for f in meta["fields"]}
    clean = pd.DataFrame()

    for col in df.columns:  # 🔁 eredeti sorrend
        if col not in fields:
            continue

        spec = fields[col]
        series = df[col]

        if spec["type"] == "date":
            clean[col] = pd.to_datetime(series, errors="coerce", format="mixed")

        elif spec["type"] == "numeric":
            clean[col] = pd.to_numeric(series, errors="coerce")

        elif spec["type"] == "id":
            clean[col] = series.astype(str)

        else:
            clean[col] = series

    return clean



def is_usable_for_analysis(series: pd.Series) -> bool:
    s = series.dropna()
    if s.empty:
        return False
    return s.nunique() > 1


def to_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        s = x.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                v = ast.literal_eval(s)
                if isinstance(v, list):
                    return v
            except Exception:
                pass
        return [x]
    return []

def looks_like_string_id(series: pd.Series) -> bool:
    s = series.dropna().astype(str)
    if s.empty:
        return False
    return (
        s.str.fullmatch(r"\d+").mean() >= 0.95
        and s.nunique() / len(s) >= 0.98
    )


def looks_like_id(series: pd.Series) -> bool:
    s = series.dropna()
    if s.empty:
        return False
    # nagyon sok egyedi érték + nincs értelmes "mennyiségi" skála
    return s.nunique() / len(s) >= 0.98


def is_date_series(series: pd.Series) -> bool:
    """
    Heurisztika: ha az első 50 nem-null érték nagy része parse-olható dátummá,
    akkor date mezőnek tekintjük.
    """
    s = series.dropna().astype(str).head(50)

    if s.empty:
        return False

    # ha a minta túlnyomó része csak számjegy, ne tekintsük automatikusan dátumnak
    digit_ratio = s.str.fullmatch(r"\d+").mean()
    if digit_ratio >= 0.9:
        return False
    
    # próbáljuk parse-olni
#    parsed = pd.to_datetime(s, errors="coerce", infer_datetime_format=True)
    parsed = pd.to_datetime(s, errors="coerce", format="mixed")

    
    # ha a mintában legalább 90% parse-olható, tekintsük dátumnak
    ok_ratio = parsed.notna().mean()
    return ok_ratio >= 0.9



def is_exclude_value(v: str) -> bool:
    v_low = v.lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in v_low:
            return True
    return False


EXCLUDE_KEYWORDS = [
    "nem", "nincs", "egyik", "soha", "sosem",
    "nem szoktam", "nem tervez", "nem képzelhető",
    "nem döntött", "egyéb"
]

df = pd.read_csv(INPUT_CSV, sep=";", encoding="utf-8")

meta = {
    "dataset": "insurance",
    "row_semantics": "1 sor = 1 szerződés",
    "source": INPUT_CSV,
    "fields": []
}

for col in df.columns:
    series = df[col]
    non_null = series.dropna().head(50)
    
    if not is_usable_for_analysis(series):
        continue

    is_list = False
    for v in non_null:
        if isinstance(v, list):
            is_list = True
            break
        if isinstance(v, str) and v.strip().startswith("[") and v.strip().endswith("]"):
            is_list = True
            break

    # NUMERIKUS


    if is_date_series(series):
        parsed = pd.to_datetime(series, errors="coerce", format="mixed")

        

        min_dt = parsed.min()
        max_dt = parsed.max()

        field = {
            "name": col,
            "type": "date",
            "min": str(min_dt.date()) if pd.notna(min_dt) else None,
            "max": str(max_dt.date()) if pd.notna(max_dt) else None,
        }
        
    elif looks_like_string_id(series):
        field = {"name": col, "type": "id"}
    
    elif pd.api.types.is_numeric_dtype(series) and looks_like_id(series):
        field = {"name": col, "type": "id"}
    
    elif pd.api.types.is_numeric_dtype(series):
        if series.min() == series.max():
            continue  # konstans numeric → kuka
        field = {
            "name": col,
            "type": "numeric",
            "min": float(series.min()),
            "max": float(series.max())
        }
    
    elif is_list:
        exploded = series.dropna().apply(to_list).explode()
        values = sorted(set(v for v in exploded if pd.notna(v)))

        exclude_values = [v for v in values if is_exclude_value(str(v))]
        entity_values = [v for v in values if v not in exclude_values]

        field = {
            "name": col,
            "type": "list",
            "item_type": "categorical",
            "values": entity_values + exclude_values,  # teljes lista
            "exclude_values": exclude_values
        }

    else:
        values = sorted(set(v for v in series.dropna().unique()))
        field = {
            "name": col,
            "type": "categorical",
            "values": values
        }

    meta["fields"].append(field)


with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)





clean_df = canonicalize_dataframe(df, meta)
for f in meta["fields"]:
    if f["type"] == "date":
        col = f["name"]
        clean_df[col] = clean_df[col].dt.strftime("%Y-%m-%d")

clean_df.to_csv(CLEAN_CSV, index=False, encoding="utf-8")


print("Kész:", OUTPUT_JSON)


# In[ ]:




