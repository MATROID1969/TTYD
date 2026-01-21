# Insurance Talk – Recepteknél használt minták

=== RECEPTEK (példák) ===

1. Kérdés: 2024-ben hány CASCO szerződést kötöttek?
```python
import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme
apply_default_theme()
YEAR = 2024
MOD = "CASCO"

df_tmp = df.copy()
df_tmp["Szerzodeskotes_datuma"] = pd.to_datetime(
    df_tmp["Szerzodeskotes_datuma"], errors="coerce"
)

df_filtered = df_tmp[
    (df_tmp["Szerzodeskotes_datuma"].dt.year == YEAR) &
    (df_tmp["Szerzodes_modozat"] == MOD)
]

result = len(df_filtered)
```


2. Kérdés: 2024-ben hány CASCO szerződés szűnt meg?
```python
import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme
apply_default_theme()

# Paraméterek
YEAR = 2024
MOD = "CASCO"

# Dátummező biztos kezelése
df_tmp = df.copy()
df_tmp["Kockazatviselés_vege"] = pd.to_datetime(
    df_tmp["Kockazatviselés_vege"], errors="coerce"
)

# Szűrés: CASCO + 2024-ben megszűnt
df_terminated = df_tmp[
    (df_tmp["Szerzodes_modozat"] == MOD) &
    (df_tmp["Kockazatviselés_vege"].dt.year == YEAR)
]

# Eredmény
result = int(len(df_terminated))
```

3. Kérdés: 2024 év végén aktív CASCO szerződések hány százaléka szűnt meg 2025 év végéig? 
```python
import warnings; warnings.filterwarnings("ignore")
import pandas as pd

MOD = "CASCO"
BASE_DATE = pd.Timestamp("2024-12-31")
END_DATE  = pd.Timestamp("2025-12-31")

df_tmp = df.copy()
df_tmp["Szerzodeskotes_datuma"] = pd.to_datetime(df_tmp["Szerzodeskotes_datuma"], errors="coerce")
df_tmp["Kockazatviselés_vege"] = pd.to_datetime(df_tmp["Kockazatviselés_vege"], errors="coerce")

df_base = df_tmp[
    (df_tmp["Szerzodes_modozat"] == MOD) &
    (df_tmp["Szerzodeskotes_datuma"] <= BASE_DATE) &
    (
        df_tmp["Kockazatviselés_vege"].isna() |
        (df_tmp["Kockazatviselés_vege"] > BASE_DATE)
    )
]


df_terminated = df_base[
    df_base["Kockazatviselés_vege"].notna() &
    (df_base["Kockazatviselés_vege"] <= END_DATE)
]

result = round(len(df_terminated) / len(df_base) * 100, 2) if len(df_base) > 0 else 0.0
```

4. Kérdés 2023 márciusi aktív CASCO állomány hány % maradt 1 év múlva aktív?
```python
import warnings; warnings.filterwarnings("ignore")
import pandas as pd

MOD = "CASCO"
BASE_DATE = pd.Timestamp("2023-03-31")
END_DATE  = pd.Timestamp("2024-03-31")

# Dátummezők biztonságos kezelése
df_tmp = df.copy()
df_tmp["Szerzodeskotes_datuma"] = pd.to_datetime(
    df_tmp["Szerzodeskotes_datuma"], errors="coerce"
)
df_tmp["Kockazatviselés_vege"] = pd.to_datetime(
    df_tmp["Kockazatviselés_vege"], errors="coerce"
)


df_base = df_tmp[
    (df_tmp["Szerzodes_modozat"] == MOD) &
    (df_tmp["Szerzodeskotes_datuma"] <= BASE_DATE) &
    (
        df_tmp["Kockazatviselés_vege"].isna() |
        (df_tmp["Kockazatviselés_vege"] > BASE_DATE)
    )
]

base_n = len(df_base)


df_still_active = df_base[
    df_base["Kockazatviselés_vege"].isna() |
    (df_base["Kockazatviselés_vege"] > END_DATE)
]

active_n = len(df_still_active)

if base_n == 0:
    result = 0.0
else:
    result = round(active_n / base_n * 100, 2)
```

5. Kérdés Mennyi volt a 2024.01-es CASCO szerződések várható élettartama?

```python
import warnings; warnings.filterwarnings("ignore")
import pandas as pd

MOD = "CASCO"
START = pd.Timestamp("2024-01-01")
END   = pd.Timestamp("2024-01-31")
AS_OF_DATE = pd.Timestamp("2025-02-28")

df_tmp = df.copy()
df_tmp["Szerzodeskotes_datuma"] = pd.to_datetime(
    df_tmp["Szerzodeskotes_datuma"], errors="coerce"
)

df_filtered = df_tmp[
    (df_tmp["Szerzodes_modozat"] == MOD) &
    (df_tmp["Szerzodeskotes_datuma"] >= START) &
    (df_tmp["Szerzodeskotes_datuma"] <= END)
]

survivor_df = calc_survivor(df_filtered, AS_OF_DATE)
life_months = expected_trapezoid(survivor_df)
result = round(life_months / 12, 2)
```

6. Kérdés Rajzolj egy vonaldiagramot ami havi bontásban mutatja az új CASCO szerződések számát! 
```python
import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme, format_date_axis
apply_default_theme()
import matplotlib.pyplot as plt
import pandas as pd

MOD = "CASCO"

# --- DÁTUMMEZŐ ELŐKÉSZÍTÉSE ---
df_tmp = df.copy()
df_tmp["Szerzodeskotes_datuma"] = pd.to_datetime(
    df_tmp["Szerzodeskotes_datuma"], errors="coerce"
)

# --- CSAK CASCO ---
df_casco = df_tmp[df_tmp["Szerzodes_modozat"] == MOD]

# --- HAVI DARABSZÁM ---
monthly_counts = (
    df_casco
    .groupby(df_casco["Szerzodeskotes_datuma"].dt.to_period("M"))
    .size()
    .reset_index(name="Darab")
)

# Period → Timestamp (tengelyhez)
monthly_counts["Honap"] = monthly_counts["Szerzodeskotes_datuma"].dt.to_timestamp(how="start")

# --- ÁBRA ---
fig, ax = plt.subplots(figsize=(8,3))
ax.plot(monthly_counts["Honap"], monthly_counts["Darab"], marker="o")

ax.set_title("Új CASCO szerződések száma – havi bontásban")
ax.set_ylabel("Darab")

format_date_axis(ax)

result = fig
```

7. Kérdés Rajzolj egy vonaldiagramot, ami havi bontásban mutatja, hogy az adott hónapban kötött új CASCO szerződések hány százaléka aktív még?
```python
import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme, format_date_axis
apply_default_theme()
import matplotlib.pyplot as plt
import pandas as pd

MOD = "CASCO"
CURRENT_DATE = pd.Timestamp("2025-02-28")  # "MOST" a demo szerint

df_tmp = df.copy()

df_tmp["Szerzodeskotes_datuma"] = pd.to_datetime(
    df_tmp["Szerzodeskotes_datuma"], errors="coerce"
)
df_tmp["Kockazatviselés_vege"] = pd.to_datetime(
    df_tmp["Kockazatviselés_vege"], errors="coerce"
)

# csak CASCO + valid kötések
df_casco = df_tmp[
    (df_tmp["Szerzodes_modozat"] == MOD) &
    (df_tmp["Szerzodeskotes_datuma"].notna())
].copy()

df_casco["Honap"] = df_casco["Szerzodeskotes_datuma"].dt.to_period("M")

records = []
for m in sorted(df_casco["Honap"].dropna().unique()):
    sub = df_casco[df_casco["Honap"] == m]
    total = len(sub)
    if total == 0:
        pct = 0.0
    else:
        active = sub[
            sub["Kockazatviselés_vege"].isna() |
            (sub["Kockazatviselés_vege"] > CURRENT_DATE)
        ]
        pct = float(len(active) / total * 100)

    ts = m.to_timestamp(how="start")
    records.append((ts, pct))

df_plot = pd.DataFrame(records, columns=["Honap", "Aktiv_pct"])
df_plot["Honap"] = pd.to_datetime(df_plot["Honap"], errors="coerce")

fig, ax = plt.subplots(figsize=(8,3))
ax.plot(df_plot["Honap"], df_plot["Aktiv_pct"], marker="o")

ax.set_title("Új CASCO szerződések: még aktív arány (%) havi bontásban")
ax.set_ylabel("%")

format_date_axis(ax)

result = fig
```

8. Kérdés Rajzolj egy vonaldiagramot, ami havi bontásban mutatja, hogy az adott hónapban kötött szerződések hány százaléka aktív még minden módozatra?
```python
import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme, format_date_axis
apply_default_theme()
import matplotlib.pyplot as plt
import pandas as pd

CURRENT_DATE = pd.Timestamp("2025-02-28")  # demo „MOST”

df_tmp = df.copy()

df_tmp["Szerzodeskotes_datuma"] = pd.to_datetime(
    df_tmp["Szerzodeskotes_datuma"], errors="coerce"
)
df_tmp["Kockazatviselés_vege"] = pd.to_datetime(
    df_tmp["Kockazatviselés_vege"], errors="coerce"
)

# csak érvényes kötések
df_tmp = df_tmp[df_tmp["Szerzodeskotes_datuma"].notna()].copy()

df_tmp["Honap"] = df_tmp["Szerzodeskotes_datuma"].dt.to_period("M")

records = []

for (mod, honap), sub in df_tmp.groupby(["Szerzodes_modozat", "Honap"]):
    total = len(sub)
    if total == 0:
        pct = 0.0
    else:
        active = sub[
            sub["Kockazatviselés_vege"].isna() |
            (sub["Kockazatviselés_vege"] > CURRENT_DATE)
        ]
        pct = float(len(active) / total * 100)

    records.append({
        "Szerzodes_modozat": mod,
        "Honap": honap.to_timestamp(how="start"),
        "Aktiv_pct": pct
    })

df_plot = pd.DataFrame(records)
df_plot["Honap"] = pd.to_datetime(df_plot["Honap"], errors="coerce")

fig, ax = plt.subplots(figsize=(8,3))

for mod, sub in df_plot.groupby("Szerzodes_modozat"):
    ax.plot(sub["Honap"], sub["Aktiv_pct"], marker="o", label=mod)

ax.set_title("Új szerződések: még aktív arány (%) havi bontásban – termékenként")
ax.set_ylabel("%")
ax.legend(title="Termék")

format_date_axis(ax)

result = fig
```

9. Kérdés Melyik módozat értékesítése nőtt legjobban 2025-ben 2024-hez képest?
```python
import warnings; warnings.filterwarnings("ignore")
import pandas as pd

YEAR_1 = 2024
YEAR_2 = 2025

df_tmp = df.copy()

# Dátummező biztos kezelése
df_tmp["Szerzodeskotes_datuma"] = pd.to_datetime(
    df_tmp["Szerzodeskotes_datuma"], errors="coerce"
)

# Csak érvényes kötések
df_tmp = df_tmp[df_tmp["Szerzodeskotes_datuma"].notna()].copy()

# Éves darabszám módozatonként
counts = (
    df_tmp
    .assign(Year=df_tmp["Szerzodeskotes_datuma"].dt.year)
    .query("Year in [@YEAR_1, @YEAR_2]")
    .groupby(["Szerzodes_modozat", "Year"])
    .size()
    .unstack(fill_value=0)
)

# Biztonság: ha valamelyik év hiányzik
counts[YEAR_1] = counts.get(YEAR_1, 0)
counts[YEAR_2] = counts.get(YEAR_2, 0)

# Százalékos növekedés
def pct_growth(row):
    if row[YEAR_1] == 0:
        return None  # nincs bázis → nem értelmezhető
    return (row[YEAR_2] - row[YEAR_1]) / row[YEAR_1] * 100

counts["Növekedés_%"] = counts.apply(pct_growth, axis=1)

# Legnagyobb növekedésű módozat (csak ahol értelmezhető)
valid = counts.dropna(subset=["Növekedés_%"])
best_mod = str(valid["Növekedés_%"].idxmax())
best_pct = float(valid.loc[best_mod, "Növekedés_%"])

# Eredmény
result = {
    "legnagyobb_novekedes_modozat": str(best_mod),
    "legnagyobb_novekedes_szazalek": round(best_pct, 2),
    "novekedesek_modozatonkent": {
        str(idx): (None if pd.isna(val) else round(float(val), 2))
        for idx, val in counts["Növekedés_%"].items()
    }
}
```

10. Kérdés Rajzolj egy vonaldiagramot, ami évről évre mutatja különböző az adott évben kötött szerződések  átlagdíjait módozatonként
```python
import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme, format_date_axis
apply_default_theme()
import matplotlib.pyplot as plt
import pandas as pd

# Dátum biztos kezelése
df_tmp = df.copy()
df_tmp["Szerzodeskotes_datuma"] = pd.to_datetime(
    df_tmp["Szerzodeskotes_datuma"], errors="coerce"
)

# Csak érvényes kötések és díjak
df_tmp = df_tmp[
    df_tmp["Szerzodeskotes_datuma"].notna() &
    df_tmp["Allomany_dij"].notna()
].copy()

# Év képzése
df_tmp["Year"] = df_tmp["Szerzodeskotes_datuma"].dt.year

# Éves átlagdíj módozatonként
avg_premium = (
    df_tmp
    .groupby(["Year", "Szerzodes_modozat"])["Allomany_dij"]
    .mean()
    .reset_index()
)

# Plot előkészítés
fig, ax = plt.subplots(figsize=(8,3))

for mod, sub in avg_premium.groupby("Szerzodes_modozat"):
    ax.plot(
        sub["Year"],
        sub["Allomany_dij"],
        marker="o",
        label=mod
    )

ax.set_title("Éves átlagdíj az adott évben kötött szerződésekre")
ax.set_ylabel("Átlagdíj")
ax.set_xlabel("Év")
ax.legend()

# X tengely formázás (év → timestamp)
ax.set_xticks(sorted(avg_premium["Year"].unique()))
ax.set_xticklabels(sorted(avg_premium["Year"].unique()))

result = fig
```

11. Kérdés Rajzolj kördiagramot, ami az aktív CASCO szerződések díjfizetés módjainak eloszlását mutatja
```python
import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme
apply_default_theme()
import matplotlib.pyplot as plt
import pandas as pd

# Aktuális dátum (demo / most)
CURRENT_DATE = pd.Timestamp("2025-02-28")
MOD = "CASCO"

# Dátum biztos kezelése
df_tmp = df.copy()
df_tmp["Kockazatviselés_vege"] = pd.to_datetime(
    df_tmp["Kockazatviselés_vege"], errors="coerce"
)

# Aktív CASCO szerződések
df_active = df_tmp[
    (df_tmp["Szerzodes_modozat"] == MOD) &
    (
        df_tmp["Kockazatviselés_vege"].isna() |
        (df_tmp["Kockazatviselés_vege"] > CURRENT_DATE)
    )
]

# Díjfizetés mód eloszlás
counts = df_active["Dijfizetes_mod"].value_counts()

# Kördiagram
fig, ax = plt.subplots(figsize=(6,6))
ax.pie(
    counts.values,
    labels=counts.index,
    autopct="%1.1f%%",
    startangle=90
)
ax.set_title("Aktív CASCO szerződések díjfizetés mód szerinti megoszlása")

result = fig
```

12. Kérdés Mikor volt nagyobb a CASCO szerződések várható élettartam: 2024 januárban vagy 2023 januárban?
```python
import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme
apply_default_theme()
import pandas as pd

MOD = "CASCO"

# Vizsgálati dátumok
DATE_2023 = pd.Timestamp("2023-01-31")
DATE_2024 = pd.Timestamp("2024-01-31")

# CASCO szerződések
df_f = df[df["Szerzodes_modozat"] == MOD].copy()

# Dátummezők biztos kezelése
df_f["Szerzodeskotes_datuma"] = pd.to_datetime(
    df_f["Szerzodeskotes_datuma"], errors="coerce"
)
df_f["Kockazatviselés_vege"] = pd.to_datetime(
    df_f["Kockazatviselés_vege"], errors="coerce"
)

# 2023 január – survivor és várható élettartam
surv_2023 = calc_survivor(df_f, DATE_2023)
life_2023_years = expected_trapezoid(surv_2023) / 12

# 2024 január – survivor és várható élettartam
surv_2024 = calc_survivor(df_f, DATE_2024)
life_2024_years = expected_trapezoid(surv_2024) / 12

life_2023_years = round(life_2023_years, 2)
life_2024_years = round(life_2024_years, 2)

# Szöveges eredmény
if life_2024_years > life_2023_years:
    result = (
        f"2023 januárban a CASCO szerződések várható élettartama {life_2023_years} év volt, "
        f"2024 januárban pedig {life_2024_years} év. "
        f"A várható élettartam 2024 januárban volt nagyobb."
    )
elif life_2024_years < life_2023_years:
    result = (
        f"2023 januárban a CASCO szerződések várható élettartama {life_2023_years} év volt, "
        f"2024 januárban pedig {life_2024_years} év. "
        f"A várható élettartam 2023 januárban volt nagyobb."
    )
else:
    result = (
        f"A CASCO szerződések várható élettartama mind 2023 januárban, "
        f"mind 2024 januárban {life_2023_years} év volt."
    )
```

13. Kérdés Éves bontásban: az adott évben kötött CASCO szerződések hány százaléka szűnt meg 60 napon belül?
```python
import warnings; warnings.filterwarnings("ignore")
from matplotlib_theme import apply_default_theme, format_date
apply_default_theme()
import matplotlib.pyplot as plt
import pandas as pd

MOD = "CASCO"

# Másolat + dátumok
df_c = df[df["Szerzodes_modozat"] == MOD].copy()

df_c["Szerzodeskotes_datuma"] = pd.to_datetime(
    df_c["Szerzodeskotes_datuma"], errors="coerce"
)
df_c["Kockazatviselés_vege"] = pd.to_datetime(
    df_c["Kockazatviselés_vege"], errors="coerce"
)

# Csak értelmezhető kötési dátum
df_c = df_c[df_c["Szerzodeskotes_datuma"].notna()].copy()

# Év
df_c["Ev"] = df_c["Szerzodeskotes_datuma"].dt.year

records = []

for ev in sorted(df_c["Ev"].unique()):
    sub = df_c[df_c["Ev"] == ev]
    total = len(sub)

    if total == 0:
        continue

    # 60 napon belüli megszűnés
    terminated_60d = sub[
        sub["Kockazatviselés_vege"].notna() &
        (
            sub["Kockazatviselés_vege"]
            <= sub["Szerzodeskotes_datuma"] + pd.Timedelta(days=60)
        )
    ]

    pct = len(terminated_60d) / total * 100
    records.append((ev, pct))

df_plot = pd.DataFrame(records, columns=["Ev", "pct"])

# Oszlopdiagram
fig, ax = plt.subplots(figsize=(8,3))
ax.bar(df_plot["Ev"].astype(str), df_plot["pct"])

ax.set_title("60 napon belül megszűnt CASCO szerződések aránya (%)")
ax.set_ylabel("%")
ax.set_xlabel("Kötés éve")

result = fig
```

14. Kérdés CASCO szerződéseknél melyik díjfizetési módnál a legkisebb annak a valószínűsége, hogy 1 ében belül megszűnik a szerződés? 
```python
import warnings; warnings.filterwarnings("ignore")
import pandas as pd

MOD = "CASCO"
DAYS = 365

df_tmp = df.copy()

# Dátumok biztos kezelése
df_tmp["Szerzodeskotes_datuma"] = pd.to_datetime(
    df_tmp["Szerzodeskotes_datuma"], errors="coerce"
)
df_tmp["Kockazatviselés_vege"] = pd.to_datetime(
    df_tmp["Kockazatviselés_vege"], errors="coerce"
)

# CASCO + értelmezhető kötési dátum + díjfizetési mód
df_c = df_tmp[
    (df_tmp["Szerzodes_modozat"] == MOD) &
    df_tmp["Szerzodeskotes_datuma"].notna() &
    df_tmp["Dijfizetes_mod"].notna()
].copy()

# 1 éven belüli megszűnés flag
df_c["megszunt_1even_belul"] = (
    df_c["Kockazatviselés_vege"].notna() &
    (df_c["Kockazatviselés_vege"] <= df_c["Szerzodeskotes_datuma"] + pd.Timedelta(days=DAYS))
)

# Megszűnési ráta díjfizetés módonként (%)
rates = (
    df_c.groupby("Dijfizetes_mod")["megszunt_1even_belul"]
    .mean()
    .sort_values()
    * 100
)

# Legkisebb megszűnési ráta
best_method = str(rates.index[0]) if len(rates) > 0 else None
best_rate = float(rates.iloc[0]) if len(rates) > 0 else None

result = {
    "legkisebb_megszunesi_rata_dijfizetes_mod": best_method,
    "legkisebb_megszunesi_rata_szazalek": None if best_rate is None else round(best_rate, 2),
    "megszunesi_ratak_szazalek_dijfizetes_mod_szerint": {
        str(k): round(float(v), 2) for k, v in rates.items()
    }
}

```