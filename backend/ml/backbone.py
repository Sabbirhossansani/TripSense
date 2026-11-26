"""
Pretrained Multimodal & Semantic Backbone Encoder for TripSense.
Supports:
  - openai/clip-vit-base-patch32 (512-d, Vision-Language CLIP)
  - google/siglip-base-patch16-224 (768-d, Google SigLIP)
  - BAAI/bge-base-en-v1.5 (768-d, Dense Retrieval Text Encoder)
Encodes TripSense POIs, Active-Learning Swipe Deck cards, and multi-city POIs.
"""

import os
import re
import json
import numpy as np
import torch
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "data_cache")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

SWIPE_CARDS_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "card-street-food",
        "title": "Chittagong Mezban & Old Dhaka Night Food Lanes",
        "category": "Food",
        "badge": "Culinary Trail",
        "tag": "Local SME Kitchens",
        "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=900&q=80",
        "description": "Slow-cooked spiced Mezban beef, smoky charcoal kebabs, traditional Bakarkhani, and bustling heritage food alleys.",
        "text_prompt": "authentic local street food spicy traditional mezban curry night market culinary adventure",
    },
    {
        "id": "card-coral-beach",
        "title": "Inani Coral Coast & Sunset Horizons",
        "category": "Beach",
        "badge": "Coastal Serenity",
        "tag": "Ocean & Sunset",
        "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=80",
        "description": "Volcanic coral boulders along golden sand beaches, gentle sea breeze, and quiet low-tide coastal walks.",
        "text_prompt": "golden sandy ocean beach waves coral stones sunset peaceful coastal shoreline",
    },
    {
        "id": "card-swamp-forest",
        "title": "Ratargul Rowboat Canopy & Emerald Wetlands",
        "category": "Nature",
        "badge": "Zero-Emission Eco",
        "tag": "Biodiversity",
        "image": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=900&q=80",
        "description": "Gliding in silent wooden rowboats beneath submerged rainforest canopies and migratory wetland sanctuaries.",
        "text_prompt": "freshwater swamp forest wooden rowboat lush green rainforest canopy nature wildlife eco tour",
    },
    {
        "id": "card-mughal-heritage",
        "title": "Mughal Forts, Pink Palaces & Colorful Minarets",
        "category": "Historical",
        "badge": "Living History",
        "tag": "Architecture",
        "image": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=900&q=80",
        "description": "17th-century red-sandstone fortresses, riverside Nawab palaces, and 1870 floral mosques rich with stories.",
        "text_prompt": "historic mughal fort palace mosque minarets ancient heritage architecture photography",
    },
    {
        "id": "card-hill-trek",
        "title": "Boga Lake Cloud Trails & Mountain Peaks",
        "category": "Adventure",
        "badge": "Alpine Expedition",
        "tag": "Active Trekking",
        "image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=900&q=80",
        "description": "High-altitude crater lakes, mist-wrapped mountain ridges, suspension bridges, and indigenous village homestays.",
        "text_prompt": "mountain trekking misty peaks crater lake hiking adventure suspension bridge",
    },
    {
        "id": "card-tea-sanctuary",
        "title": "Sreemangal Seven-Layer Tea & Quiet Lakeside",
        "category": "Relaxation",
        "badge": "Slow Travel",
        "tag": "Mindful Escape",
        "image": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=900&q=80",
        "description": "Rolling organic tea gardens, unhurried afternoon brews, and tranquil bamboo lakeside pavilions.",
        "text_prompt": "peaceful tea garden green slopes calm lakeside relaxation coffee slow travel",
    },
    {
        "id": "card-tribal-museum",
        "title": "Ethnological Galleries & Folk Weaving Studios",
        "category": "Culture",
        "badge": "Rain-Safe Indoor",
        "tag": "Artisan Crafts",
        "image": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?auto=format&fit=crop&w=900&q=80",
        "description": "Curated indoor cultural museums, handloom Jamdani workshops, and living stories of diverse hill communities.",
        "text_prompt": "cultural museum indigenous crafts handloom art exhibition indoor gallery heritage",
    },
    {
        "id": "card-coastal-cycling",
        "title": "Marine Drive E-Bike & Cave Canyon Explorer",
        "category": "Adventure",
        "badge": "Low-Carbon Thrill",
        "tag": "Offbeat Route",
        "image": "https://images.unsplash.com/photo-1541625602330-2277a4c46182?auto=format&fit=crop&w=900&q=80",
        "description": "Cycling along dramatic ocean cliffs, exploring rainforest stream caves, and discovering hidden valleys.",
        "text_prompt": "coastal cycling road adventure caves waterfalls outdoor active exploration",
    },
    {
        "id": "card-art-cafe",
        "title": "Acoustic Folk Rooftops & Organic Kitchens",
        "category": "Food",
        "badge": "Fair-Trade Dining",
        "tag": "Cozy Indoor",
        "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=80",
        "description": "Zero-waste farm-to-table Bengal fusion dining, live acoustic Baul evenings, and cozy rain-safe lounges.",
        "text_prompt": "cozy artisan cafe organic restaurant live acoustic music warm indoor dining lounge",
    },
    {
        "id": "card-bird-wetland",
        "title": "Baikka Beel Dawn Birding & Butterfly Park",
        "category": "Nature",
        "badge": "Hidden Gem",
        "tag": "Quiet Wildlife",
        "image": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=900&q=80",
        "description": "Silent dawn observation towers over lotus marshes, fluttering butterfly sanctuaries, and zero city noise.",
        "text_prompt": "wetland migratory birds lotus marsh peaceful nature sanctuary butterflies quiet sunrise",
    },
    {
        "id": "card-river-promenade",
        "title": "Karnaphuli Waterfront & Bamboo Eco Lounges",
        "category": "Relaxation",
        "badge": "Zero-Plastic",
        "tag": "Breeze & Calm",
        "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=900&q=80",
        "description": "Gentle evening sea breezes along clean riverfronts and zero-plastic handcrafted bamboo pavilions.",
        "text_prompt": "riverfront sunset breeze bamboo eco lounge calm evening promenade relax",
    },
    {
        "id": "card-marine-museum",
        "title": "Oceanarium Tunnels & Liberation War Archives",
        "category": "Culture",
        "badge": "All-Weather",
        "tag": "Curated Indoor",
        "image": "https://images.unsplash.com/photo-1566127444979-b3d2b654e3d7?auto=format&fit=crop&w=900&q=80",
        "description": "Deep-sea coral reef tunnels and award-winning architectural heritage galleries immune to tropical rain.",
        "text_prompt": "indoor aquarium marine exhibits modern architectural history museum cultural center",
    },
]


def _resolve_hf_token() -> str:
    tok = os.getenv("HF_TOKEN", "").strip()
    if tok and tok.startswith("hf_"):
        return tok
    tf = os.path.join(BASE_DIR, "HF_token.txt")
    if os.path.exists(tf):
        m = re.search(r"(hf_[A-Za-z0-9]+)", open(tf, "r", encoding="utf-8").read())
        if m:
            return m.group(1)
    return ""


class SigLIPBackbone:
    """
    Wraps pretrained foundation encoders (CLIP, SigLIP, BGE) to produce
    L2-normalized semantic embeddings for POIs and Swipe Cards.
    """

    PREFERRED_MODELS = [
        "openai/clip-vit-base-patch32",
        "google/siglip-base-patch16-224",
        "BAAI/bge-base-en-v1.5",
    ]

    def __init__(self, model_name: str = None, device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.requested_model = model_name
        self.model_name = None
        self.model = None
        self.tokenizer = None
        self.emb_dim = 512
        self._load_backbone()

    def _load_backbone(self):
        from transformers import AutoTokenizer, AutoModel
        hf_token = _resolve_hf_token() or None

        candidates = [self.requested_model] if self.requested_model else self.PREFERRED_MODELS
        for candidate in candidates:
            try:
                print(f"[Backbone] Loading {candidate} on {self.device}...", flush=True)
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(candidate, local_files_only=True)
                    self.model = AutoModel.from_pretrained(candidate, local_files_only=True).to(self.device)
                except Exception:
                    self.tokenizer = AutoTokenizer.from_pretrained(candidate, token=hf_token)
                    self.model = AutoModel.from_pretrained(candidate, token=hf_token).to(self.device)
                self.model.eval()
                self.model_name = candidate

                with torch.no_grad():
                    test_vec = self.encode_texts(["Sydney harbor museum"], batch_size=1)
                    self.emb_dim = int(test_vec.shape[1])
                print(f"[Backbone] Loaded {candidate} cleanly (dim={self.emb_dim}, device={self.device})", flush=True)
                return
            except Exception as e:
                print(f"[Backbone] Warning: failed to load {candidate}: {e}", flush=True)

        raise RuntimeError(f"Could not load pretrained backbone model(s): {candidates}")

    @torch.no_grad()
    def encode_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encodes list of texts into L2-normalized float32 embeddings."""
        all_vecs = []
        mlow = (self.model_name or "").lower()
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            max_len = 64 if "siglip" in mlow else (128 if "bge" in mlow else 77)
            inputs = self.tokenizer(
                batch,
                padding="max_length" if ("siglip" in mlow or "clip" in mlow) else True,
                truncation=True,
                max_length=max_len,
                return_tensors="pt",
            ).to(self.device)

            if hasattr(self.model, "get_text_features"):
                feats = self.model.get_text_features(**inputs)
                if not isinstance(feats, torch.Tensor):
                    feats = feats.pooler_output if hasattr(feats, "pooler_output") else feats[0]
            else:
                out = self.model(**inputs)
                if "bge" in mlow:
                    # Standard BGE CLS token normalized embedding
                    feats = out.last_hidden_state[:, 0]
                elif hasattr(out, "pooler_output") and out.pooler_output is not None:
                    feats = out.pooler_output
                else:
                    feats = out.last_hidden_state[:, 0]

            feats = torch.nn.functional.normalize(feats.float(), p=2, dim=-1)
            all_vecs.append(feats.cpu().numpy())

        return np.vstack(all_vecs).astype(np.float32)


def encode_and_save_tripsense_artifacts(backbone: SigLIPBackbone = None) -> Tuple[str, np.ndarray, np.ndarray]:
    """
    Encodes all TripSense POIs and the 12 Swipe Cards with the pretrained backbone
    and saves compact .npz artifact files for fast runtime inference.
    """
    if backbone is None:
        backbone = SigLIPBackbone()

    bd_path = os.path.join(BASE_DIR, "backend", "app", "data", "bangladesh_spots.json")
    global_path = os.path.join(BASE_DIR, "backend", "data", "global_spots.json")

    spots = []
    seen = set()
    for p in [bd_path, global_path]:
        if os.path.exists(p):
            for item in json.load(open(p, "r", encoding="utf-8")):
                if item["id"] not in seen:
                    spots.append(item)
                    seen.add(item["id"])

    poi_texts = [
        f"{s.get('name', '')} | Category: {s.get('category', '')} | City: {s.get('city', '')} | "
        f"Tags: {', '.join(s.get('tags', []))} | {s.get('description', '')}"
        for s in spots
    ]
    poi_ids = np.array([int(s["id"]) for s in spots], dtype=np.int32)
    poi_embs = backbone.encode_texts(poi_texts, batch_size=32)

    poi_out = os.path.join(ARTIFACTS_DIR, "poi_embeddings.npz")
    np.savez_compressed(
        poi_out,
        poi_ids=poi_ids,
        embeddings=poi_embs,
        model_name=np.array([backbone.model_name]),
    )

    swipe_texts = [
        f"{c['title']} | Category: {c['category']} | {c['text_prompt']} | {c['description']}"
        for c in SWIPE_CARDS_CATALOG
    ]
    swipe_ids = np.array([c["id"] for c in SWIPE_CARDS_CATALOG])
    swipe_cats = np.array([c["category"] for c in SWIPE_CARDS_CATALOG])
    swipe_embs = backbone.encode_texts(swipe_texts, batch_size=16)

    swipe_out = os.path.join(ARTIFACTS_DIR, "swipe_embeddings.npz")
    np.savez_compressed(
        swipe_out,
        card_ids=swipe_ids,
        categories=swipe_cats,
        embeddings=swipe_embs,
        model_name=np.array([backbone.model_name]),
    )

    print(f"[Backbone] Saved {len(poi_ids)} POI embeddings -> {poi_out}")
    print(f"[Backbone] Saved {len(swipe_ids)} Swipe embeddings -> {swipe_out}")
    return backbone.model_name, poi_embs, swipe_embs
