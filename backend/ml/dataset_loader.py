"""
Real Q1 Benchmark Dataset Loader for TripSense-FairNet & Neuro-Symbolic RAG.
Downloads & prepares:
  1. CRUISEResearchGroup/Massive-STEPS-Sydney (real POI trajectories -> multi-user groups)
  2. osunlp/TravelPlanner (validation split -> constraint-grounded RAG evaluation)
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download, list_repo_files

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

CACHE_DIR = os.path.join(os.path.dirname(__file__), "data_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def get_hf_token() -> str:
    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        token_file = os.path.join(BASE_DIR, "HF_token.txt")
        if os.path.exists(token_file):
            import re
            txt = open(token_file, "r", encoding="utf-8").read()
            m = re.search(r"hf_[A-Za-z0-9]+", txt)
            if m:
                token = m.group(0)
    return token


def load_massive_steps_sydney(max_rows: int = 35000) -> pd.DataFrame:
    """
    Downloads and returns the tabular check-in parquet from CRUISEResearchGroup/Massive-STEPS-Sydney.
    """
    cache_pq = os.path.join(CACHE_DIR, "massive_steps_sydney_tabular.parquet")
    if os.path.exists(cache_pq):
        df = pd.read_parquet(cache_pq)
        return df.head(max_rows) if len(df) > max_rows else df

    token = get_hf_token()
    repo_id = "CRUISEResearchGroup/Massive-STEPS-Sydney"
    files = list_repo_files(repo_id=repo_id, repo_type="dataset", token=token or None)
    tabular_files = [f for f in files if "tabular" in f and f.endswith(".parquet")]
    if not tabular_files:
        tabular_files = [f for f in files if f.endswith(".parquet")]
    if not tabular_files:
        raise RuntimeError(f"No parquet files found in {repo_id}: {files}")

    dfs = []
    for tf in tabular_files:
        local_p = hf_hub_download(
            repo_id=repo_id,
            filename=tf,
            repo_type="dataset",
            token=token or None,
            local_dir=CACHE_DIR,
        )
        dfs.append(pd.read_parquet(local_p))

    df = pd.concat(dfs, ignore_index=True)
    df.to_parquet(cache_pq, index=False)
    print(f"[DatasetLoader] Loaded Massive-STEPS-Sydney tabular: {len(df)} rows, cols={list(df.columns)}")
    return df.head(max_rows) if len(df) > max_rows else df


def load_travelplanner_val(max_rows: int = 180) -> pd.DataFrame:
    """
    Downloads and returns the validation split of osunlp/TravelPlanner.
    """
    cache_pq = os.path.join(CACHE_DIR, "travelplanner_validation.parquet")
    if os.path.exists(cache_pq):
        df = pd.read_parquet(cache_pq)
        return df.head(max_rows)

    token = get_hf_token()
    repo_id = "osunlp/TravelPlanner"
    files = list_repo_files(repo_id=repo_id, repo_type="dataset", token=token or None)
    val_files = [f for f in files if "validation" in f and (f.endswith(".parquet") or f.endswith(".csv"))]
    if not val_files:
        # Check huggingface auto-converted parquet branch or CSV
        csv_files = [f for f in files if f.endswith(".csv")]
        val_files = [f for f in csv_files if "validation" in f] or csv_files

    if not val_files:
        raise RuntimeError(f"No validation file found in {repo_id}: {files}")

    target_file = val_files[0]
    local_p = hf_hub_download(
        repo_id=repo_id,
        filename=target_file,
        repo_type="dataset",
        token=token or None,
        local_dir=CACHE_DIR,
    )
    df = pd.read_parquet(local_p) if target_file.endswith(".parquet") else pd.read_csv(local_p)
    df.to_parquet(cache_pq, index=False)
    print(f"[DatasetLoader] Loaded TravelPlanner validation: {len(df)} rows, cols={list(df.columns)}")
    return df.head(max_rows)


def build_sydney_group_benchmark(
    df: pd.DataFrame,
    seed: int = 42,
    n_groups: int = 900
) -> Dict[str, Any]:
    """
    Constructs realistic multi-user travel group preference & POI interaction benchmark
    from real Massive-STEPS-Sydney user check-in trajectories.
    Each group consists of 2-4 real users who share destination context or overlapping venue visits.
    Split chronologically/deterministically into train (70%), val (15%), test (15%).
    """
    rng = np.random.default_rng(seed)

    # Normalize column names
    cols = {c.lower(): c for c in df.columns}
    user_col = cols.get("user_id") or cols.get("userid")
    venue_col = cols.get("venue_id") or cols.get("poi_id") or cols.get("name")
    cat_col = cols.get("venue_category") or cols.get("category") or "venue_category"
    name_col = cols.get("name") or venue_col
    lat_col = cols.get("latitude")
    lon_col = cols.get("longitude")

    work = df.dropna(subset=[user_col, venue_col]).copy()
    work["u_str"] = work[user_col].astype(str)
    work["v_str"] = work[venue_col].astype(str)

    # Unique venues table
    venue_agg = {
        name_col: "first",
        cat_col: "first" if cat_col in work.columns else "size",
    }
    if lat_col and lon_col:
        venue_agg[lat_col] = "first"
        venue_agg[lon_col] = "first"

    venues_df = work.groupby("v_str", as_index=False).agg(venue_agg)
    venues_df["popularity"] = work.groupby("v_str").size().reindex(venues_df["v_str"]).values

    # Keep venues with >= 2 check-ins and users with >= 4 check-ins for meaningful splits
    valid_venues = set(venues_df[venues_df["popularity"] >= 2]["v_str"])
    work = work[work["v_str"].isin(valid_venues)]
    user_counts = work["u_str"].value_counts()
    valid_users = list(user_counts[user_counts >= 4].index)
    work = work[work["u_str"].isin(valid_users)]

    venues_df = venues_df[venues_df["v_str"].isin(set(work["v_str"]))].reset_index(drop=True)
    venue_to_idx = {v: i for i, v in enumerate(venues_df["v_str"])}
    user_to_venues: Dict[str, List[int]] = {}
    for u, grp in work.groupby("u_str"):
        user_to_venues[u] = list(dict.fromkeys(venue_to_idx[v] for v in grp["v_str"]))

    # Simulate realistic crowd/eco/cost metadata deterministically from venue category & popularity
    max_pop = max(1, float(venues_df["popularity"].max()))
    venue_features = np.zeros((len(venues_df), 8), dtype=np.float32)
    cats = venues_df[cat_col].astype(str).tolist() if cat_col in venues_df.columns else ["Place"] * len(venues_df)
    indoor_keywords = ("museum", "gallery", "cafe", "coffee", "restaurant", "mall", "bar", "theater", "cinema", "shop", "bakery", "library")
    eco_keywords = ("park", "garden", "beach", "trail", "botanical", "harbor", "water", "museum", "walk", "art")

    lats = venues_df[lat_col].astype(float).values if lat_col in venues_df.columns else np.full(len(venues_df), -33.8688)
    lons = venues_df[lon_col].astype(float).values if lon_col in venues_df.columns else np.full(len(venues_df), 151.2093)
    center_lat, center_lon = float(np.median(lats)), float(np.median(lons))

    for idx, row in venues_df.iterrows():
        c_low = str(cats[idx]).lower()
        pop_norm = float(np.log1p(row["popularity"]) / np.log1p(max_pop))
        dist_deg = float(np.hypot(lats[idx] - center_lat, lons[idx] - center_lon))
        dist_norm = float(min(1.0, dist_deg / 0.15))
        is_indoor = 1.0 if any(k in c_low for k in indoor_keywords) else 0.0
        is_hidden = 1.0 if pop_norm < 0.45 else 0.0
        eco_score = 0.85 if any(k in c_low for k in eco_keywords) else (0.72 if is_indoor else 0.58)
        price_norm = 0.25 if ("park" in c_low or "beach" in c_low) else (0.55 if is_indoor else 0.40)
        rating_norm = float(np.clip(0.65 + 0.25 * (1.0 - 0.3 * pop_norm) + 0.1 * eco_score, 0.4, 0.98))
        sme_share = 0.85 if is_hidden > 0.5 else 0.50

        venue_features[idx] = [
            dist_norm,
            price_norm,
            pop_norm,         # crowd density proxy
            rating_norm,
            is_indoor,
            is_hidden,
            eco_score,
            sme_share,
        ]

    # Build Groups (mix of similar-taste friends & diverse-taste conflicting groups)
    users_list = list(user_to_venues.keys())
    venue_to_users: Dict[int, List[str]] = {}
    for u, vlist in user_to_venues.items():
        for v in vlist:
            venue_to_users.setdefault(v, []).append(u)

    co_visit_venues = [v for v, ulist in venue_to_users.items() if len(ulist) >= 2]
    groups = []

    for g_id in range(n_groups):
        if co_visit_venues and rng.random() < 0.78:
            # Grounded group: pick 2-4 users who genuinely co-visited at least 1 anchor venue
            anchor_v = int(rng.choice(co_visit_venues))
            pool = venue_to_users[anchor_v]
            k = int(min(len(pool), rng.integers(2, 5)))
            members = list(rng.choice(pool, size=k, replace=False))
            # Add occasional conflicting friend for realistic fairness challenge
            if len(members) < 4 and rng.random() < 0.45:
                extra = str(rng.choice(users_list))
                if extra not in members:
                    members.append(extra)
        else:
            k = int(rng.integers(2, 5))
            members = list(rng.choice(users_list, size=min(k, len(users_list)), replace=False))

        # Target positive POIs for the group (shared or union of late-sequence venues)
        # Hold out last check-ins of members as ground-truth targets, keep earlier check-ins as member history
        member_histories = {}
        target_pool = []
        for m in members:
            seq = user_to_venues[m]
            split_pt = max(2, int(len(seq) * 0.7))
            member_histories[m] = seq[:split_pt]
            target_pool.extend(seq[split_pt:])

        if not target_pool:
            continue

        # Prefer co-visited holdouts if available
        counts = pd.Series(target_pool).value_counts()
        pos_targets = list(counts.index[:min(5, len(counts))])

        groups.append({
            "group_id": g_id,
            "members": members,
            "member_histories": member_histories,
            "member_budgets": [float(rng.choice([0.25, 0.55, 0.90])) for _ in members],
            "pos_targets": [int(x) for x in pos_targets],
        })

    rng.shuffle(groups)
    n_total = len(groups)
    n_train = int(0.70 * n_total)
    n_val = int(0.15 * n_total)

    return {
        "venues_df": venues_df,
        "venue_features": venue_features,
        "venue_texts": [
            f"{row[name_col]} ({cats[i]}) - Sydney tourist attraction"
            for i, row in venues_df.iterrows()
        ],
        "popularity": venues_df["popularity"].values.astype(np.float32),
        "user_to_venues": user_to_venues,
        "train_groups": groups[:n_train],
        "val_groups": groups[n_train:n_train + n_val],
        "test_groups": groups[n_train + n_val:],
    }
