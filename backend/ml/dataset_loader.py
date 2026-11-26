"""
Dataset Loader & Zero-Leakage Multi-City + Multi-Dataset Benchmark Builder for TripSense.

Datasets:
  1. CRUISEResearchGroup/Massive-STEPS-{Sydney, Melbourne, Tokyo, New-York, Istanbul, Sao-Paulo}
     Real Foursquare sequential check-in trails across 5 continents used to build chronological,
     zero-leakage multi-member travel group benchmarks (2-5 members per group).
  2. CRUISEResearchGroup/TripWorld (2026 Out-of-Town Cross-City Benchmark)
     Real out-of-town traveler behaviors enriched with Google Maps POI metadata & ratings,
     where hometown histories (c_h) predict unfamiliar destination targets (c_o).
  3. osunlp/TravelPlanner (validation split, 180 tasks)
     Real benchmark for evaluating the Neuro-Symbolic Verifier on budget & constraints.
"""

import os
import re
import json
import math
import hashlib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

CACHE_DIR = os.path.join(os.path.dirname(__file__), "data_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _slugify_city(city: str) -> str:
    return city.strip().lower().replace("-", "_").replace(" ", "_")


def _get_hf_token() -> Optional[str]:
    tok = os.getenv("HF_TOKEN", "").strip()
    if tok and tok.startswith("hf_"):
        return tok
    token_file = os.path.join(BASE_DIR, "HF_token.txt")
    if os.path.exists(token_file):
        with open(token_file, "r", encoding="utf-8") as f:
            txt = f.read()
            m = re.search(r"(hf_[A-Za-z0-9]+)", txt)
            if m:
                return m.group(1)
    return None


def load_massive_steps_city(city: str = "Sydney", max_rows: int = 30000) -> pd.DataFrame:
    """
    Loads CRUISEResearchGroup/Massive-STEPS-{city} tabular check-in data,
    caching cleanly as parquet in data_cache/ for deterministic fast reloads.
    """
    slug = _slugify_city(city)
    local_parquet = os.path.join(CACHE_DIR, f"massive_steps_{slug}_tabular.parquet")
    if os.path.exists(local_parquet):
        df = pd.read_parquet(local_parquet)
        if len(df) > max_rows:
            df = df.iloc[:max_rows].copy()
        return df

    from huggingface_hub import HfApi, hf_hub_download

    hf_token = _get_hf_token()
    repo_id = f"CRUISEResearchGroup/Massive-STEPS-{city}"
    api = HfApi(token=hf_token)
    files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")

    candidates = [
        f for f in files
        if ("tabular" in f.lower() or "checkin" in f.lower() or f.lower().endswith(".csv") or f.lower().endswith(".parquet"))
        and ("train" in f.lower() or "checkins" in f.lower() or slug in f.lower() or f.endswith(".parquet") or f.endswith(".csv"))
    ]
    if not candidates:
        candidates = [f for f in files if f.lower().endswith((".parquet", ".csv"))]
    if not candidates:
        raise FileNotFoundError(f"No tabular CSV/Parquet files found in {repo_id}: {files}")

    candidates.sort(key=lambda x: (0 if "tabular" in x.lower() else 1, 0 if "checkin" in x.lower() else 1, len(x)))
    chosen = candidates[0]
    print(f"[DatasetLoader] Downloading {repo_id} -> {chosen}...", flush=True)
    local_file = hf_hub_download(
        repo_id=repo_id,
        filename=chosen,
        repo_type="dataset",
        local_dir=CACHE_DIR,
        token=hf_token,
    )

    if local_file.endswith(".parquet"):
        df = pd.read_parquet(local_file)
    else:
        df = pd.read_csv(local_file)

    col_map = {}
    if "userid" in df.columns and "user_id" not in df.columns:
        col_map["userid"] = "user_id"
    if "venueid" in df.columns and "venue_id" not in df.columns:
        col_map["venueid"] = "venue_id"
    if "lat" in df.columns and "latitude" not in df.columns:
        col_map["lat"] = "latitude"
    if "lon" in df.columns and "longitude" not in df.columns:
        col_map["lon"] = "longitude"
    if "lng" in df.columns and "longitude" not in df.columns:
        col_map["lng"] = "longitude"
    if col_map:
        df = df.rename(columns=col_map)

    required_fill = {
        "venue_category": "General Venue",
        "name": "Unnamed Venue",
        "trail_id": "0",
        "latitude": 0.0,
        "longitude": 0.0,
    }
    for col, val in required_fill.items():
        if col not in df.columns:
            df[col] = val

    df = df.dropna(subset=["user_id", "venue_id"]).copy()
    if len(df) > max_rows:
        df = df.iloc[:max_rows].copy()
    df.to_parquet(local_parquet, index=False)
    print(f"[DatasetLoader] Cached {len(df)} rows for {city} -> {local_parquet}", flush=True)
    return df


def load_massive_steps_sydney(max_rows: int = 30000) -> pd.DataFrame:
    """Backward-compatible helper loading Sydney check-ins."""
    return load_massive_steps_city("Sydney", max_rows=max_rows)


def load_travelplanner_val() -> pd.DataFrame:
    """Loads osunlp/TravelPlanner validation split (180 tasks)."""
    local_parquet = os.path.join(CACHE_DIR, "travelplanner_validation.parquet")
    if os.path.exists(local_parquet):
        return pd.read_parquet(local_parquet)

    local_csv = os.path.join(CACHE_DIR, "validation.csv")
    if os.path.exists(local_csv):
        df = pd.read_csv(local_csv)
        df.to_parquet(local_parquet, index=False)
        return df

    from huggingface_hub import hf_hub_download

    hf_token = _get_hf_token()
    path = hf_hub_download(
        repo_id="osunlp/TravelPlanner",
        filename="validation.csv",
        repo_type="dataset",
        local_dir=CACHE_DIR,
        token=hf_token,
    )
    df = pd.read_csv(path)
    df.to_parquet(local_parquet, index=False)
    return df


def _category_priors(category: str) -> Dict[str, float]:
    """Domain-grounded tourism category priors for cost, indoor flag, eco & SME share."""
    cat = str(category or "").lower()
    is_indoor = 1.0 if any(k in cat for k in (
        "museum", "gallery", "cafe", "coffee", "restaurant", "mall", "shop",
        "bar", "theater", "cinema", "library", "aquarium", "hotel", "bakery",
        "station", "book", "art", "food", "ramen", "sushi", "pub", "izakaya"
    )) else 0.0

    if any(k in cat for k in ("park", "garden", "beach", "trail", "lake", "mountain", "nature", "scenic", "lookout", "forest", "shrine")):
        price_base, eco_base, sme_base = 0.12, 0.90, 0.80
    elif any(k in cat for k in ("museum", "historic", "temple", "mosque", "church", "art", "landmark", "palace", "cultural", "castle")):
        price_base, eco_base, sme_base = 0.28, 0.84, 0.78
    elif any(k in cat for k in ("market", "street", "bakery", "cafe", "tea", "noodle", "diner", "food", "ramen", "bistro", "restaurant")):
        price_base, eco_base, sme_base = 0.38, 0.68, 0.86
    elif any(k in cat for k in ("mall", "department", "hotel", "resort", "casino", "nightclub", "steakhouse", "airport")):
        price_base, eco_base, sme_base = 0.78, 0.38, 0.32
    elif any(k in cat for k in ("station", "platform", "subway", "bus", "ferry", "train", "tram")):
        price_base, eco_base, sme_base = 0.18, 0.88, 0.55
    else:
        price_base, eco_base, sme_base = 0.44, 0.62, 0.62

    return {
        "is_indoor": is_indoor,
        "price_base": price_base,
        "eco_base": eco_base,
        "sme_base": sme_base,
    }


def _clean_cat_text(raw_cats: Any, schema_str: Any) -> str:
    if isinstance(raw_cats, (list, np.ndarray)) and len(raw_cats) > 0:
        parts = [str(c).strip() for c in raw_cats if c]
        if parts:
            return ", ".join(parts[:3])
    s = str(schema_str or "General Venue").replace("schema:", "").strip()
    # Split CamelCase e.g. TrainStation -> Train Station
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
    return s or "General Venue"


def build_tripworld_group_benchmark(
    dest_qid: str = "Q35765",
    dest_name: str = "Osaka (TripWorld Out-of-Town)",
    num_groups: int = 220,
    seed: int = 77,
    max_pois: int = 7500,
) -> Dict[str, Any]:
    """
    Constructs a strictly zero-leakage Out-of-Town Group Tourist Benchmark from
    CRUISEResearchGroup/TripWorld (Osaka metro Q35765 by default):
      - Every member's taste embedding is built strictly from their HOMETOWN check-ins (c_h).
      - Ground-truth group targets are real OUT-OF-TOWN destination POIs (c_o) in dest_qid.
      - Uses authentic Google Maps ratings, review/check-in counts, and place categories from pois.parquet.
    """
    cache_pkl = os.path.join(CACHE_DIR, f"tripworld_{_slugify_city(dest_qid)}_{num_groups}_{seed}.pkl")
    if os.path.exists(cache_pkl):
        import pickle
        return pickle.load(open(cache_pkl, "rb"))

    from huggingface_hub import hf_hub_download

    hf_token = _get_hf_token()
    beh_path = os.path.join(CACHE_DIR, "travel_behaviors.parquet")
    pois_path = os.path.join(CACHE_DIR, "pois.parquet")
    if not os.path.exists(beh_path):
        beh_path = hf_hub_download("CRUISEResearchGroup/TripWorld", "travel_behaviors.parquet", repo_type="dataset", local_dir=CACHE_DIR, token=hf_token)
    if not os.path.exists(pois_path):
        pois_path = hf_hub_download("CRUISEResearchGroup/TripWorld", "pois.parquet", repo_type="dataset", local_dir=CACHE_DIR, token=hf_token)

    print(f"[TripWorldLoader] Building Out-of-Town Benchmark for {dest_name} ({dest_qid})...", flush=True)
    beh = pd.read_parquet(beh_path)
    sub = beh[beh["r_o"] == dest_qid].copy()
    sub = sub.sort_values("user_id").reset_index(drop=True)

    pois_df = pd.read_parquet(
        pois_path,
        columns=[
            "fsq_place_id", "locality", "venue_schema", "n_checkins",
            "google_name", "google_rating", "google_categories",
        ],
    )
    poi_lookup = pois_df.set_index("fsq_place_id").to_dict("index")

    # Collect valid travelers with >= 3 known hometown venues and >= 1 known destination venue
    user_home_vids: Dict[str, List[str]] = {}
    user_dest_vids: Dict[str, List[str]] = {}
    user_dest_cats: Dict[str, set] = {}

    for _, row in sub.iterrows():
        uid = str(row["user_id"])
        ch = row["c_h"]
        co = row["c_o"]
        h_vids = []
        for item in ch:
            vid = str(item.get("venue_id", ""))
            if vid in poi_lookup and (not h_vids or h_vids[-1] != vid):
                h_vids.append(vid)
        o_vids = []
        for item in co:
            vid = str(item.get("venue_id", ""))
            if vid in poi_lookup and (not o_vids or o_vids[-1] != vid):
                o_vids.append(vid)
        if len(h_vids) >= 3 and len(o_vids) >= 1:
            user_home_vids[uid] = h_vids[-18:]
            user_dest_vids[uid] = list(dict.fromkeys(o_vids))
            cats = set()
            for v in o_vids:
                cats.add(_clean_cat_text(poi_lookup[v].get("google_categories"), poi_lookup[v].get("venue_schema")))
            user_dest_cats[uid] = cats

    # Collect catalog: all referenced home+dest venues + top popular destination venues up to max_pois
    ref_vids = set()
    for uid in sorted(user_home_vids.keys()):
        ref_vids.update(user_home_vids[uid])
        ref_vids.update(user_dest_vids[uid])

    dest_pois_df = pois_df[pois_df["locality"] == dest_qid].sort_values("n_checkins", ascending=False)
    for vid in dest_pois_df["fsq_place_id"].tolist():
        if len(ref_vids) >= max_pois:
            break
        ref_vids.add(str(vid))

    all_vids = sorted(ref_vids)
    vid_to_idx = {v: i for i, v in enumerate(all_vids)}

    # Destination-only candidate pool indices so groups rank destination POIs cleanly
    dest_only_indices = [
        vid_to_idx[v] for v in all_vids
        if poi_lookup[v].get("locality") == dest_qid
    ]
    max_log_pop = math.log1p(float(dest_pois_df["n_checkins"].max())) if len(dest_pois_df) > 0 else 5.0

    num_venues = len(all_vids)
    venue_feats = np.zeros((num_venues, 8), dtype=np.float32)
    venue_records: List[Dict[str, Any]] = []

    for idx, vid in enumerate(all_vids):
        meta = poi_lookup[vid]
        cat_txt = _clean_cat_text(meta.get("google_categories"), meta.get("venue_schema"))
        gname = meta.get("google_name")
        name_txt = str(gname).strip() if (gname is not None and str(gname).strip() and str(gname) != "None") else f"{cat_txt} Stop"
        priors = _category_priors(cat_txt)

        v_hash = (int(hashlib.md5(str(vid).encode("utf-8")).hexdigest()[:8], 16) % 1000) / 1000.0
        dist_norm = float(np.clip(0.18 + 0.50 * v_hash, 0.05, 0.92))

        pop_raw = float(meta.get("n_checkins") or 1.0)
        pop_norm = float(min(1.0, math.log1p(pop_raw) / max(1e-6, max_log_pop)))

        raw_rat = meta.get("google_rating")
        if raw_rat is not None and not pd.isna(raw_rat):
            rating_norm = float(np.clip((float(raw_rat) - 2.0) / 3.0, 0.25, 0.98))
        else:
            rating_norm = float(np.clip(0.55 + 0.30 * pop_norm + (v_hash - 0.5) * 0.12, 0.25, 0.98))

        price_norm = float(np.clip(priors["price_base"] + (v_hash - 0.5) * 0.14, 0.05, 0.98))
        is_indoor = priors["is_indoor"]
        is_hidden = 1.0 if pop_norm <= 0.35 else 0.0
        eco_score = float(np.clip(priors["eco_base"] + 0.08 * is_hidden + (0.5 - v_hash) * 0.08, 0.15, 0.98))
        sme_share = float(np.clip(priors["sme_base"] + 0.10 * is_hidden - 0.12 * pop_norm + (v_hash - 0.5) * 0.08, 0.15, 0.96))

        venue_feats[idx] = [
            dist_norm, price_norm, pop_norm, rating_norm,
            is_indoor, is_hidden, eco_score, sme_share,
        ]
        venue_records.append({
            "venue_idx": idx,
            "venue_id": str(vid),
            "name": name_txt,
            "category": cat_txt,
            "city": dest_name,
            "price_norm": round(price_norm, 4),
            "pop_norm": round(pop_norm, 4),
            "eco_score": round(eco_score, 4),
            "sme_share": round(sme_share, 4),
            "is_hidden": bool(is_hidden > 0.5),
            "is_indoor": bool(is_indoor > 0.5),
        })

    # Group assembly over real out-of-town travelers with overlapping destination interests
    eligible_users = sorted(user_home_vids.keys())
    dest_venue_to_users: Dict[int, List[str]] = {}
    for uid in eligible_users:
        for vid in user_dest_vids[uid]:
            v_idx = vid_to_idx[vid]
            dest_venue_to_users.setdefault(v_idx, []).append(uid)

    shared_targets = sorted([v for v, us in dest_venue_to_users.items() if len(us) >= 2])
    cat_to_users: Dict[str, List[str]] = {}
    for uid in eligible_users:
        for c in user_dest_cats[uid]:
            cat_to_users.setdefault(c, []).append(uid)

    rng = np.random.RandomState(seed)
    all_users_arr = np.array(eligible_users, dtype=object)
    groups: List[Dict[str, Any]] = []

    for g_idx in range(num_groups):
        g_size = 2 + (g_idx % 4)
        if shared_targets and g_idx % 3 != 2:
            anchor_target = int(shared_targets[rng.randint(len(shared_targets))])
            co_users = dest_venue_to_users[anchor_target]
            if len(co_users) >= g_size:
                chosen_idx = rng.choice(len(co_users), size=g_size, replace=False)
                members = [co_users[i] for i in chosen_idx]
            else:
                members = list(co_users)
                anchor_cat = venue_records[anchor_target]["category"]
                pool = [u for u in cat_to_users.get(anchor_cat, eligible_users) if u not in members]
                while len(members) < g_size and len(pool) > 0:
                    members.append(pool.pop(rng.randint(len(pool))))
                while len(members) < g_size:
                    cand = str(all_users_arr[rng.randint(len(all_users_arr))])
                    if cand not in members:
                        members.append(cand)
        else:
            lead = str(all_users_arr[rng.randint(len(all_users_arr))])
            members = [lead]
            lead_cats = sorted(user_dest_cats[lead])
            shared_pool = [u for u in cat_to_users.get(lead_cats[rng.randint(len(lead_cats))], []) if u != lead] if lead_cats else []
            while len(members) < g_size and shared_pool:
                pick = shared_pool.pop(rng.randint(len(shared_pool)))
                if pick not in members:
                    members.append(pick)
            while len(members) < g_size:
                cand = str(all_users_arr[rng.randint(len(all_users_arr))])
                if cand not in members:
                    members.append(cand)
            anchor_target = vid_to_idx[user_dest_vids[lead][rng.randint(len(user_dest_vids[lead]))]]

        pos_targets_set = {anchor_target}
        for u in members:
            for vid in user_dest_vids[u][:2]:
                if len(pos_targets_set) < 3:
                    pos_targets_set.add(vid_to_idx[vid])
        pos_targets = sorted(pos_targets_set)

        member_histories: List[List[int]] = []
        member_budgets: List[float] = []
        user_features: List[List[float]] = []
        for m_i, u in enumerate(members):
            # Strict cross-region zero leakage: ONLY hometown check-ins c_h!
            h_idxs = [vid_to_idx[v] for v in user_home_vids[u]]
            member_histories.append(h_idxs)
            past_prices = [float(venue_feats[v, 1]) for v in h_idxs]
            mean_past_p = float(np.mean(past_prices))
            budget = float(np.clip(mean_past_p + (0.18 if m_i % 3 == 2 else (-0.15 if m_i % 3 == 0 else 0.0)), 0.18, 0.94))
            member_budgets.append(round(budget, 4))
            hist_div = float(min(1.0, len(set(venue_records[v]["category"] for v in h_idxs)) / 6.0))
            flex = float(np.clip(0.38 + 0.45 * budget + 0.15 * hist_div, 0.20, 0.95))
            user_features.append([budget, hist_div, flex])

        groups.append({
            "group_id": f"tripworld_{_slugify_city(dest_qid)}_{g_idx:04d}",
            "city": dest_name,
            "group_size": len(members),
            "members": members,
            "member_histories": member_histories,
            "member_budgets": member_budgets,
            "user_features": user_features,
            "pos_targets": pos_targets,
        })

    out = {
        "city": dest_name,
        "dest_qid": dest_qid,
        "num_rows": int(sum(len(user_dest_vids[u]) + len(user_home_vids[u]) for u in eligible_users)),
        "num_users": int(len(eligible_users)),
        "num_venues": int(num_venues),
        "dest_candidate_indices": dest_only_indices,
        "venues": venue_records,
        "venue_feats": venue_feats,
        "groups": groups,
    }
    import pickle
    pickle.dump(out, open(cache_pkl, "wb"))
    print(f"[TripWorldLoader] Cached {len(groups)} out-of-town groups | {num_venues} POIs -> {cache_pkl}", flush=True)
    return out


def build_city_group_benchmark(
    df: pd.DataFrame,
    num_groups: int = 850,
    seed: int = 42,
    city_name: str = "Sydney",
) -> Dict[str, Any]:
    """
    Constructs a chronological, zero-leakage multi-member group recommendation benchmark
    from real check-in trails. Held-out positive targets for group G are STRICTLY excluded
    from member histories used to form user taste vectors.
    """
    rng = np.random.RandomState(seed)

    work = df.copy()
    if "timestamp" in work.columns:
        work["_ts"] = pd.to_datetime(work["timestamp"], errors="coerce")
        work = work.sort_values(["_ts", "trail_id", "venue_id"], na_position="last").reset_index(drop=True)

    venues_df = work.drop_duplicates("venue_id").reset_index(drop=True)
    venue_ids = venues_df["venue_id"].tolist()
    vid_to_idx = {vid: idx for idx, vid in enumerate(venue_ids)}
    num_venues = len(venues_df)

    pop_counts = work["venue_id"].value_counts().to_dict()
    max_log_pop = math.log1p(max(pop_counts.values())) if pop_counts else 1.0

    lat_med = float(pd.to_numeric(venues_df["latitude"], errors="coerce").dropna().median() or 0.0)
    lon_med = float(pd.to_numeric(venues_df["longitude"], errors="coerce").dropna().median() or 0.0)

    venue_feats = np.zeros((num_venues, 8), dtype=np.float32)
    venue_records: List[Dict[str, Any]] = []

    for idx, row in venues_df.iterrows():
        vid = row["venue_id"]
        cat = str(row.get("venue_category", "General Venue"))
        priors = _category_priors(cat)

        lat = float(row.get("latitude", lat_med) or lat_med)
        lon = float(row.get("longitude", lon_med) or lon_med)
        dist_deg = math.sqrt((lat - lat_med) ** 2 + (lon - lon_med) ** 2)
        dist_norm = float(min(1.0, dist_deg / 0.18))

        pop_raw = float(pop_counts.get(vid, 1))
        pop_norm = float(min(1.0, math.log1p(pop_raw) / max(1e-6, max_log_pop)))

        v_hash = (int(hashlib.md5(str(vid).encode("utf-8")).hexdigest()[:8], 16) % 1000) / 1000.0
        price_norm = float(np.clip(priors["price_base"] + (v_hash - 0.5) * 0.14, 0.05, 0.98))
        rating_norm = float(np.clip(0.55 + 0.30 * pop_norm + (v_hash - 0.5) * 0.12, 0.25, 0.98))
        is_indoor = priors["is_indoor"]
        is_hidden = 1.0 if pop_norm <= 0.35 else 0.0
        eco_score = float(np.clip(priors["eco_base"] + 0.08 * is_hidden + (0.5 - v_hash) * 0.08, 0.15, 0.98))
        sme_share = float(np.clip(priors["sme_base"] + 0.10 * is_hidden - 0.12 * pop_norm + (v_hash - 0.5) * 0.08, 0.15, 0.96))

        venue_feats[idx] = [
            dist_norm, price_norm, pop_norm, rating_norm,
            is_indoor, is_hidden, eco_score, sme_share,
        ]
        venue_records.append({
            "venue_idx": idx,
            "venue_id": str(vid),
            "name": str(row.get("name", f"Venue {idx}")),
            "category": cat,
            "city": str(row.get("venue_city", city_name)),
            "price_norm": round(price_norm, 4),
            "pop_norm": round(pop_norm, 4),
            "eco_score": round(eco_score, 4),
            "sme_share": round(sme_share, 4),
            "is_hidden": bool(is_hidden > 0.5),
            "is_indoor": bool(is_indoor > 0.5),
        })

    work["v_idx"] = work["venue_id"].map(vid_to_idx)
    user_seq: Dict[Any, List[int]] = {}
    user_cats: Dict[Any, set] = {}
    for uid, grp in work.groupby("user_id", sort=False):
        seq = [int(v) for v in grp["v_idx"].tolist() if pd.notna(v)]
        dedup = []
        for v in seq:
            if not dedup or dedup[-1] != v:
                dedup.append(v)
        if len(dedup) >= 6:
            user_seq[uid] = dedup
            user_cats[uid] = set(grp["venue_category"].astype(str).tolist())

    eligible_users = sorted(user_seq.keys(), key=lambda x: str(x))
    if len(eligible_users) < 6:
        user_seq = {}
        user_cats = {}
        for uid, grp in work.groupby("user_id", sort=False):
            seq = list(dict.fromkeys(int(v) for v in grp["v_idx"].tolist() if pd.notna(v)))
            if len(seq) >= 3:
                user_seq[uid] = seq
                user_cats[uid] = set(grp["venue_category"].astype(str).tolist())
        eligible_users = sorted(user_seq.keys(), key=lambda x: str(x))

    cat_to_users: Dict[str, List[Any]] = {}
    for uid in eligible_users:
        for c in sorted(user_cats[uid]):
            cat_to_users.setdefault(c, []).append(uid)

    user_history_pool: Dict[Any, List[int]] = {}
    user_future_pool: Dict[Any, List[int]] = {}
    for uid in eligible_users:
        seq = user_seq[uid]
        split_at = max(2, int(len(seq) * 0.72))
        hist = seq[:split_at]
        fut = [v for v in seq[split_at:] if v not in hist]
        if not fut:
            fut = [seq[-1]]
            hist = seq[:-1]
        user_history_pool[uid] = hist[-20:]
        user_future_pool[uid] = fut

    groups: List[Dict[str, Any]] = []
    fut_venue_to_users: Dict[int, List[Any]] = {}
    for uid, futs in user_future_pool.items():
        for v in futs:
            fut_venue_to_users.setdefault(v, []).append(uid)

    popular_shared_targets = sorted([v for v, us in fut_venue_to_users.items() if len(us) >= 2])
    all_users_arr = np.array(eligible_users, dtype=object)

    for g_idx in range(num_groups):
        g_size = 2 + (g_idx % 4)

        if popular_shared_targets and g_idx % 3 != 2:
            anchor_target = int(popular_shared_targets[rng.randint(len(popular_shared_targets))])
            co_users = fut_venue_to_users[anchor_target]
            if len(co_users) >= g_size:
                chosen_idx = rng.choice(len(co_users), size=g_size, replace=False)
                members = [co_users[i] for i in chosen_idx]
            else:
                members = list(co_users)
                anchor_cat = venue_records[anchor_target]["category"]
                pool = [u for u in cat_to_users.get(anchor_cat, eligible_users) if u not in members]
                while len(members) < g_size and len(pool) > 0:
                    pick = pool.pop(rng.randint(len(pool)))
                    members.append(pick)
                while len(members) < g_size:
                    cand = all_users_arr[rng.randint(len(all_users_arr))]
                    if cand not in members:
                        members.append(cand)
        else:
            lead = all_users_arr[rng.randint(len(all_users_arr))]
            members = [lead]
            lead_cats = sorted(user_cats[lead])
            shared_pool = []
            if lead_cats:
                shared_pool = [u for u in cat_to_users.get(lead_cats[rng.randint(len(lead_cats))], []) if u != lead]
            while len(members) < g_size and shared_pool:
                pick = shared_pool.pop(rng.randint(len(shared_pool)))
                if pick not in members:
                    members.append(pick)
            while len(members) < g_size:
                cand = all_users_arr[rng.randint(len(all_users_arr))]
                if cand not in members:
                    members.append(cand)
            anchor_target = int(user_future_pool[lead][rng.randint(len(user_future_pool[lead]))])

        pos_targets_set = {anchor_target}
        for u in members:
            for fv in user_future_pool[u][:2]:
                if len(pos_targets_set) < 3:
                    pos_targets_set.add(int(fv))
        pos_targets = sorted(pos_targets_set)
        pos_set = set(pos_targets)

        member_histories: List[List[int]] = []
        member_budgets: List[float] = []
        user_features: List[List[float]] = []
        for m_i, u in enumerate(members):
            clean_hist = [v for v in user_history_pool[u] if v not in pos_set]
            if not clean_hist:
                clean_hist = [v for v in user_seq[u][:2] if v not in pos_set] or [0]
            member_histories.append(clean_hist)

            past_prices = [float(venue_feats[v, 1]) for v in clean_hist]
            mean_past_p = float(np.mean(past_prices))
            budget = float(np.clip(mean_past_p + (0.18 if m_i % 3 == 2 else (-0.15 if m_i % 3 == 0 else 0.0)), 0.18, 0.94))
            member_budgets.append(round(budget, 4))

            hist_div = float(min(1.0, len(set(venue_records[v]["category"] for v in clean_hist)) / 6.0))
            flex = float(np.clip(0.38 + 0.45 * budget + 0.15 * hist_div, 0.20, 0.95))
            user_features.append([budget, hist_div, flex])

        groups.append({
            "group_id": f"{_slugify_city(city_name)}_grp_{g_idx:04d}",
            "city": city_name,
            "group_size": len(members),
            "members": [str(u) for u in members],
            "member_histories": member_histories,
            "member_budgets": member_budgets,
            "user_features": user_features,
            "pos_targets": pos_targets,
        })

    return {
        "city": city_name,
        "num_rows": int(len(work)),
        "num_users": int(len(eligible_users)),
        "num_venues": int(num_venues),
        "venues": venue_records,
        "venue_feats": venue_feats,
        "groups": groups,
    }


def build_sydney_group_benchmark(df: pd.DataFrame, num_groups: int = 850, seed: int = 42) -> Dict[str, Any]:
    """Backward-compatible helper building the Sydney group benchmark."""
    return build_city_group_benchmark(df, num_groups=num_groups, seed=seed, city_name="Sydney")
