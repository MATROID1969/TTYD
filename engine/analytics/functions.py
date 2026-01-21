# =============================================================
# Survivor függvények (változatlan logika)
# =============================================================

import pandas as pd
import numpy as np



def calc_survivor(df_filtered: pd.DataFrame, vegdatum: pd.Timestamp, max_honap: int = 36):
    """
    Gyorsított survivor: suffix-sum a hónap hisztogramokra (O(n + H)).
    S_i = darab, ahol HONAP_KULONBSEG >= i
    A_i = darab, ahol HONAP_TELT_EL    >= i
    Survivor(i) = S_i / A_i
    """
    if df_filtered.empty:
        return pd.DataFrame({"Honap_szam": [], "Survivor": []})

    df = df_filtered.copy()

    start = pd.to_datetime(df["Szerzodeskotes_datuma"], errors="coerce")
    end = pd.to_datetime(df["Kockazatviselés_vege"], errors="coerce")

    mask_valid_start = start.notna() & (start < vegdatum)
    if not mask_valid_start.any():
        return pd.DataFrame({"Honap_szam": [], "Survivor": []})

    start = start[mask_valid_start]
    end = end[mask_valid_start]

    tel = (vegdatum.year - start.dt.year) * 12 + (vegdatum.month - start.dt.month)

    min_veg_vagy_lej = end.where(end.notna() & (end < vegdatum), other=vegdatum)
    dur = (min_veg_vagy_lej.dt.year - start.dt.year) * 12 + (min_veg_vagy_lej.dt.month - start.dt.month)

    tel = tel.clip(lower=0).astype(int).to_numpy()
    dur = dur.clip(lower=0).astype(int).to_numpy()

    if tel.size == 0:
        return pd.DataFrame({"Honap_szam": [], "Survivor": []})
    H = int(min(tel.max(), max_honap))
    if H <= 0:
        return pd.DataFrame({"Honap_szam": [], "Survivor": []})

    tel_c = np.minimum(tel, H + 1)
    dur_c = np.minimum(dur, H + 1)
    bins = H + 2

    cnt_tel = np.bincount(tel_c, minlength=bins)
    cnt_dur = np.bincount(dur_c, minlength=bins)

    at_risk = np.cumsum(cnt_tel[::-1])[::-1]
    survived = np.cumsum(cnt_dur[::-1])[::-1]

    idx = np.arange(1, H + 1)
    A = at_risk[idx]
    S = survived[idx]

    with np.errstate(divide='ignore', invalid='ignore'):
        surv = np.divide(S, A, out=np.zeros_like(S, dtype=float), where=A > 0)

    return pd.DataFrame({"Honap_szam": idx, "Survivor": surv})


def expected_trapezoid(df_surv):
    """Várható élettartam trapezoid integrálással (hónapban)"""
    if df_surv.empty or "Survivor" not in df_surv.columns:
        return 0.0
    return np.trapezoid(df_surv["Survivor"], dx=1)


def conditional_one_year_retention(df_filtered, survivor_df, vegdatum):
    """Kiszámolja, hogy a most aktív szerződések hány százaléka lesz még aktív 1 év múlva."""
    df_tmp = df_filtered.copy()

    df_tmp["Szerzodeskotes_datuma"] = pd.to_datetime(df_tmp["Szerzodeskotes_datuma"], errors="coerce")
    df_tmp["Kockazatviselés_vege"] = pd.to_datetime(df_tmp["Kockazatviselés_vege"], errors="coerce")

    def month_diff(start, end):
        if pd.isna(start) or pd.isna(end):
            return np.nan
        rd = relativedelta(end, start)
        return rd.years * 12 + rd.months

    df_tmp["Eltelt_honap"] = df_tmp["Szerzodeskotes_datuma"].apply(
        lambda d: month_diff(d, vegdatum)
    ).astype("Int64")

    df_tmp = df_tmp[
        (df_tmp["Kockazatviselés_vege"].isna()) |
        (df_tmp["Kockazatviselés_vege"] > vegdatum)
    ]

    surv_lookup = dict(zip(survivor_df["Honap_szam"], survivor_df["Survivor"]))
    cond_probs = []

    for h in df_tmp["Eltelt_honap"].dropna():
        if (h in surv_lookup) and ((h + 12) in surv_lookup):
            cond_probs.append(surv_lookup[h + 12] / surv_lookup[h])
        else:
            cond_probs.append(np.nan)

    return np.nanmean(cond_probs) * 100


def _month_diff_floor(start, end):
    """Egyszerű hónap-különbség relativedelta-val."""
    if pd.isna(start) or pd.isna(end):
        return np.nan
    rd = relativedelta(end, start)
    return rd.years * 12 + rd.months


def compute_lemor_series_by_age(df_in: pd.DataFrame, asof_date: pd.Timestamp, max_honap: int = 36):
    """
    Lemorzsolódás (aktív arány) kor-szeletek szerint az adott vizsgálati dátumra.
    """
    if df_in.empty:
        return pd.DataFrame({"Lag": [], "Aktiv_arany": []})

    df = df_in.copy()
    df["Szerzodeskotes_datuma"] = pd.to_datetime(df["Szerzodeskotes_datuma"], errors="coerce")
    df["Kockazatviselés_vege"] = pd.to_datetime(df["Kockazatviselés_vege"], errors="coerce")

    df = df[df["Szerzodeskotes_datuma"] <= asof_date].copy()
    if df.empty:
        return pd.DataFrame({"Lag": [], "Aktiv_arany": []})

    df["AGE"] = df["Szerzodeskotes_datuma"].apply(
        lambda d: _month_diff_floor(d, asof_date)
    ).astype("Int64")

    is_active_asof = df["Kockazatviselés_vege"].isna() | (df["Kockazatviselés_vege"] >= asof_date)

    rows = []
    for age in range(0, max_honap):
        mask = df["AGE"] == age
        denom = int(mask.sum())
        if denom == 0:
            continue
        num = int((is_active_asof & mask).sum())
        ratio = num / denom if denom > 0 else np.nan
        rows.append({"Lag": -(age + 1), "Aktiv_arany": ratio})

    out = pd.DataFrame(rows).sort_values("Lag")
    return out


