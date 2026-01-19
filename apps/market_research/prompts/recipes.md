# Market research Talk – Recepteknél használt minták

=== RECEPTEK (példák) ===


1. Kérdés: Hány nő válaszolt?
```python
# Demográfiai darabszám – nem szerinti bontás

df_filtered = df[df["Nem"] == "Nő"].copy()
result = int(len(df_filtered))
```


2. Kérdés: Milyen gyakran fogyasztanak csokoládét a válaszadók?
```python
# Kategorikus eloszlás – csokoládéfogyasztás gyakorisága

col = "Milyen gyakran fogyaszt Ön táblás csokoládét, csokoládészeletet?"

dist = (
    df[col]
    .dropna()
    .value_counts(normalize=True)
    .mul(100)
    .round(1)
)

result = dist
```


3. Kérdés: Rajzolj egy sávdiagramot, hogy milyen gyakran fogyasztanak csokoládét az emberek?
```python
# Kategorikus eloszlás vizualizálása – csokoládéfogyasztás gyakorisága

import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme
apply_default_theme()

import matplotlib.pyplot as plt

col = "Milyen gyakran fogyaszt Ön táblás csokoládét, csokoládészeletet?"

dist = (
    df[col]
    .dropna()
    .value_counts(normalize=True)
    .mul(100)
    .round(1)
)

fig, ax = plt.subplots(figsize=(8,3))
dist.plot(kind="bar", ax=ax)

ax.set_ylabel("Százalék (%)")
ax.set_xlabel("")
ax.set_title("Csokoládéfogyasztás gyakorisága")

result = fig
```


4 Kérdés: Hányan járnak Burger King-be?
```python
# Multi-select kérdés – egy adott válasz darabszáma

import ast

col = "A következő gyorsétterem láncok közül melyikben étkezett az elmúlt 1 évben?"
target = "Burger King"

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

series_lists = df[col].dropna().apply(to_list)

result = int(series_lists.apply(lambda lst: target in lst).sum())

```


5 Kérdés: Rajzold egy eloszlást a gyorséttermek népszerűsége alapján
```python
# Multi-select eloszlás vizualizálása – gyorséttermek népszerűsége

import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme
apply_default_theme()
import matplotlib.pyplot as plt
import ast

col = "A következő gyorsétterem láncok közül melyikben étkezett az elmúlt 1 évben?"
exclude_values = [
    "Egyikben sem étkeztem az elmúlt 1 évben, de régebben igen",
    "Ezek közül egyik gyorsétterem láncot sem ismerem",
    "Sohasem étkeztem ezekben a gyorséttermekben",
]

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

series_lists = df[col].dropna().apply(to_list)

# respondent-level: egy válaszadó max 1x számítson márkánként
exploded = series_lists.apply(lambda lst: list(set(lst))).explode()

# entitás-elemzés: exclude_values kiszűrése
valid = exploded.dropna()
valid = valid[~valid.isin(exclude_values)]

counts = valid.value_counts()

TOP_N = 15
counts_top = counts.head(TOP_N).sort_values()

fig, ax = plt.subplots(figsize=(8,4))
counts_top.plot(kind="barh", ax=ax)
ax.set_xlabel("Válaszadók száma")
ax.set_ylabel("")
ax.set_title(f"Gyorséttermek népszerűsége (penetráció, Top {TOP_N})")

result = fig
```


6 Kérdés: A budapesti férfi lakosok közül hányan kedvelik a Burger Kinget?
```python
# Demográfiai szűrés + multi-select darabszám (javított mezőnevekkel)

import ast

gender_col = "Nem"
location_col = "Településtípus"
fastfood_col = "A következő gyorsétterem láncok közül melyikben étkezett az elmúlt 1 évben?"
target = "Burger King"

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

df_sub = df[(df[gender_col] == "Férfi") & (df[location_col] == "Budapest")].copy()

series_lists = df_sub[fastfood_col].dropna().apply(to_list)

result = int(series_lists.apply(lambda lst: target in lst).sum())

```

7. Kérdés: Melyik országba terveznek legtöbben utazni a diplomások közül?
```python
import ast

EDU_VALUE = "Főiskolai, egyetemi diploma"
EDU_COL = "Mi a legmagasabb befejezett iskolai végzettséged?"
COUNTRY_COL = "Melyik országba tervezi ezt a külföldi utazást ezen a nyáron?"

exclude_values = [
    "Még nem döntöttem, döntöttük el, hogy melyik országba megyek / megyünk nyaralni",
    "Nem tervezek külföldi utazást",
]

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

df_sub = df[df[EDU_COL] == EDU_VALUE].copy()

series_lists = df_sub[COUNTRY_COL].dropna().apply(to_list)

exploded = series_lists.apply(lambda lst: list(set(lst))).explode()
valid = exploded.dropna()
valid = valid[~valid.isin(exclude_values)]

counts = valid.value_counts()

result = str(counts.idxmax()) if len(counts) else ""

```


8. Kérdés: Rajzolj egy sávdiagramot, ami a gyorséttermek népszerűségét mutatja!
```python
import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme
apply_default_theme()
import matplotlib.pyplot as plt
import ast

col = "A következő gyorsétterem láncok közül melyikben étkezett az elmúlt 1 évben?"
exclude_values = [
    "Egyikben sem étkeztem az elmúlt 1 évben, de régebben igen",
    "Ezek közül egyik gyorsétterem láncot sem ismerem",
    "Sohasem étkeztem ezekben a gyorséttermekben",
]

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

series_lists = df[col].dropna().apply(to_list)

# respondent-level penetráció
exploded = series_lists.apply(lambda lst: list(set(lst))).explode()

valid = exploded.dropna()
valid = valid[~valid.isin(exclude_values)]

counts = valid.value_counts()

TOP_N = 15
counts_top = counts.head(TOP_N).sort_values()

fig, ax = plt.subplots(figsize=(8,4))
counts_top.plot(kind="barh", ax=ax)
ax.set_xlabel("Válaszadók száma")
ax.set_ylabel("")
ax.set_title(f"Gyorséttermek népszerűsége (penetráció, Top {TOP_N})")

result = fig

```