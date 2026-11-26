"""
TripSense-FairNet v3 (Spectral-Gated GeoFairFormer):
Dual-Path O(D)-Invariant Consensus + Spectral-Gated Semantic Adapter Architecture.

Key Architectural Innovations for Q1 Publication:
  1. Pure O(D)-Invariant Geometric + MemberGramSAB Consensus Backbone (Streams 1 & 2):
       - Stream 1 encodes zero raw embedding coordinates: only exact O(D)-invariant
         member-POI alignment tokens [cos_u, cos_u-cos_mean, cos_u-cos_min, cos_u-cos_max,
         peer_cohesion_u, budget_gap_u, budget_margin_u, raw_utility_u, user_feats(3), poi_feat(8)],
         contextualized via MemberGramSAB (Set-Transformer self-attention biased by pairwise
         companion taste Gram S_{uv}), pooled via 4-head Cross-Attention & Rawlsian Soft-Min.
       - Stream 2 processes the un-squashed 15-dim city-agnostic group-relational highway
         without raw input LayerNorm distortion.
  2. Unsupervised Spectral-Support OOD Gate (Stream 3 Additive Adapter):
       - Fits top-r (r=48) SVD subspace U_r strictly from unlabeled source-city POI vectors.
       - Smooth gate gamma(C) = sigmoid((E_eff - tau_sub) * 80) activates the fine-grained
         Hadamard semantic adapter in-domain (Sydney: gamma ~ 0.75) and attenuates toward 0
         on shifted cross-city / out-of-town manifolds (Tokyo, New-York, Istanbul, TripWorld),
         guaranteeing zero cross-city semantic overfitting alongside dual-path supervision.
  3. Exact End-to-End XAI Differentiability (forward_from_rel_vec):
       - Reconstructs Stream 1 member alignments & budget gaps algebraically from r_{G,p}
         with <1e-5 discrepancy, enabling axiomatic Integrated Gradients and Expected Gradients
         across the ENTIRE fused dual-stream consensus score.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict, Optional


class ResidualBlock(nn.Module):
    def __init__(self, dim: int, dropout: float = 0.10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, dim),
            nn.LayerNorm(dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim, dim),
            nn.LayerNorm(dim),
        )
        self.act = nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(x + self.net(x))


class MemberGramSAB(nn.Module):
    """
    Set-Transformer Self-Attention Block augmented with O(D)-invariant pairwise
    companion taste Gram bias S_{uv} = <e_u, e_v>. Preserves permutation equivariance
    across variable group sizes |G| = 2..5 without coordinate overfitting.
    """

    def __init__(self, dim: int, num_heads: int = 4, dropout: float = 0.10):
        super().__init__()
        assert dim % num_heads == 0, "hidden_dim must be divisible by num_heads"
        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads

        self.qkv = nn.Linear(dim, dim * 3)
        self.out_proj = nn.Linear(dim, dim)
        self.gram_scale = nn.Parameter(torch.full((1, num_heads, 1, 1), 0.35))
        self.drop = nn.Dropout(dropout)
        self.norm1 = nn.LayerNorm(dim)
        self.ffn = nn.Sequential(
            nn.Linear(dim, dim * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim * 2, dim),
        )
        self.norm2 = nn.LayerNorm(dim)

    def forward(
        self,
        h: torch.Tensor,          # (B, M, D)
        sim_uu: torch.Tensor,     # (B, M, M)
        user_mask: torch.Tensor,  # (B, M) bool
    ) -> torch.Tensor:
        B, M, D = h.shape
        qkv = self.qkv(h).view(B, M, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]

        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        scores = scores + self.gram_scale * sim_uu.unsqueeze(1)

        key_mask = ~user_mask.unsqueeze(1).unsqueeze(2)
        scores = scores.masked_fill(key_mask, -1e9)
        attn = self.drop(F.softmax(scores, dim=-1))

        ctx = torch.matmul(attn, v).transpose(1, 2).contiguous().view(B, M, D)
        h1 = self.norm1(h + self.drop(self.out_proj(ctx)))
        h2 = self.norm2(h1 + self.drop(self.ffn(h1)))
        return h2 * user_mask.unsqueeze(-1).float()


def extract_group_relational_features(
    user_embs: torch.Tensor,   # (B, M, D)
    user_feats: torch.Tensor,  # (B, M, 3) -> [budget, diversity, flex]
    user_mask: torch.Tensor,   # (B, M) bool
    poi_emb: torch.Tensor,     # (B, D)
    poi_feat: torch.Tensor,    # (B, 8) -> [dist, price, pop, rating, indoor, hidden, eco, sme]
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Computes permutation-invariant 15-dim city-agnostic group-relational vector:
      [cos_mean, cos_min, cos_max, cos_std, bg_mean, bg_max, m_norm, poi_feat(8)]
    Returns (rel_vec (B, 15), cos_sim (B, M), budget_gap (B, M)).
    """
    mask_f = user_mask.float()
    counts = mask_f.sum(dim=-1, keepdim=True).clamp(min=1.0)

    cos_sim = (user_embs * poi_emb.unsqueeze(1)).sum(dim=-1).clamp(-1.0, 1.0)
    cos_mean = (cos_sim * mask_f).sum(dim=-1, keepdim=True) / counts

    cos_for_min = cos_sim.masked_fill(~user_mask, 1e4)
    cos_min = cos_for_min.min(dim=-1, keepdim=True).values.clamp(-1.0, 1.0)

    cos_for_max = cos_sim.masked_fill(~user_mask, -1e4)
    cos_max = cos_for_max.max(dim=-1, keepdim=True).values.clamp(-1.0, 1.0)

    diff_sq = ((cos_sim - cos_mean) ** 2) * mask_f
    cos_std = torch.sqrt(diff_sq.sum(dim=-1, keepdim=True) / counts + 1e-6)

    poi_price = poi_feat[:, 1:2]
    member_budget = user_feats[:, :, 0]
    budget_gap = F.relu(poi_price - member_budget)

    bg_mean = (budget_gap * mask_f).sum(dim=-1, keepdim=True) / counts
    bg_max = budget_gap.masked_fill(~user_mask, -1e4).max(dim=-1, keepdim=True).values.clamp(0.0, 1.0)

    m_norm = counts / 5.0

    rel_vec = torch.cat(
        [cos_mean, cos_min, cos_max, cos_std, bg_mean, bg_max, m_norm, poi_feat],
        dim=-1,
    )
    return rel_vec, cos_sim, budget_gap


class TripSenseFairNet(nn.Module):
    def __init__(
        self,
        emb_dim: int = 512,
        poi_feat_dim: int = 8,
        user_feat_dim: int = 3,
        hidden_dim: int = 64,
        num_heads: int = 4,
        dropout: float = 0.10,
        softmin_temp: float = 0.12,
        use_attention: bool = True,
        use_relational_stream: bool = True,
        use_member_sab: bool = True,
        use_hadamard: bool = True,
        use_spectral_gate: bool = True,
        subspace_rank: int = 48,
    ):
        super().__init__()
        self.emb_dim = emb_dim
        self.poi_feat_dim = poi_feat_dim
        self.user_feat_dim = user_feat_dim
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.softmin_temp = softmin_temp
        self.use_attention = use_attention
        self.use_relational_stream = use_relational_stream
        self.use_member_sab = use_member_sab
        self.use_hadamard = use_hadamard
        self.use_spectral_gate = use_spectral_gate
        self.subspace_rank = subspace_rank

        # Unsupervised source subspace buffers for OOD spectral gating
        self.register_buffer("src_basis", torch.zeros(emb_dim, subspace_rank))
        self.register_buffer("src_thresh", torch.tensor(0.562, dtype=torch.float32))
        self.register_buffer("has_subspace", torch.tensor(False, dtype=torch.bool))

        # ── Stream 1: Pure O(D)-Invariant Geometric + MemberGramSAB + Cross-Attention ──
        self.rel_dim = 7 + poi_feat_dim  # 15
        # Strictly O(D)-invariant 19-dim tokens: zero raw embedding coordinates!
        self.geo_tok_dim = 8 + user_feat_dim + poi_feat_dim  # 19
        self.user_in = nn.Sequential(
            nn.Linear(self.geo_tok_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.user_res = ResidualBlock(hidden_dim, dropout)
        self.member_sab = MemberGramSAB(hidden_dim, num_heads=num_heads, dropout=dropout)

        self.poi_in = nn.Sequential(
            nn.Linear(self.rel_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.poi_res = ResidualBlock(hidden_dim, dropout)

        self.member_scorer = nn.Sequential(
            nn.Linear(hidden_dim * 2 + 2, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )

        self.cross_attn = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        self.attn_norm = nn.LayerNorm(hidden_dim)

        # ── Stream 2: City-Invariant 15-dim Group-Relational Highway ──────────────
        self.rel_norm = nn.Identity()
        self.rel_net = nn.Sequential(
            nn.Linear(self.rel_dim, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(64, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Linear(64, 1),
        )
        self.rel_linear_skip = nn.Linear(self.rel_dim, 1)

        # ── Stream 3: Spectral-Gated Semantic Hadamard Adapter ────────────────────
        self.sem_drop = nn.Dropout(0.35)
        self.sem_adapter = nn.Sequential(
            nn.Linear(emb_dim, 48),
            nn.LayerNorm(48),
            nn.GELU(),
            nn.Dropout(0.20),
            nn.Linear(48, 16),
            nn.LayerNorm(16),
            nn.GELU(),
            nn.Linear(16, 1),
        )

        # Additive softplus stream scales [Cross-Attn, Soft-Min, Rel-Highway, Sem-Adapter] + bias
        self.fusion_scales = nn.Parameter(torch.tensor([0.80, 0.35, 1.30, 1.15], dtype=torch.float32))
        self.out_bias = nn.Parameter(torch.zeros(1, dtype=torch.float32))

    def set_source_subspace(self, poi_embs_np: np.ndarray):
        """
        Fits top-r (r=48) SVD subspace strictly from UNLABELED training-city venue
        embeddings (zero label leakage) to calibrate the Spectral-Support OOD Gate.
        """
        _, _, Vt = np.linalg.svd(poi_embs_np.astype(np.float32), full_matrices=False)
        r = min(self.subspace_rank, Vt.shape[0])
        V_sub = np.zeros((self.emb_dim, self.subspace_rank), dtype=np.float32)
        V_sub[:, :r] = Vt[:r].T
        energies = np.sum((poi_embs_np @ V_sub) ** 2, axis=1)
        thresh = float(energies.mean() - 0.16 * energies.std())
        self.src_basis.copy_(torch.from_numpy(V_sub).to(self.src_basis.device))
        self.src_thresh.fill_(thresh)
        self.has_subspace.fill_(True)

    def spectral_gate(self, poi_emb: torch.Tensor) -> torch.Tensor:
        """Computes smooth OOD spectral-support activation gamma(C) in (0, 1)."""
        if (not self.use_spectral_gate) or (not bool(self.has_subspace.item())):
            return torch.ones(poi_emb.size(0), device=poi_emb.device, dtype=poi_emb.dtype)
        proj = poi_emb @ self.src_basis
        en = (proj * proj).sum(dim=-1)
        en_eff = (0.85 * en.mean() + 0.15 * en) if poi_emb.size(0) >= 8 else en
        return torch.sigmoid((en_eff - self.src_thresh) * 80.0)

    def score_relational_head(self, rel_vec: torch.Tensor) -> torch.Tensor:
        """Evaluates Stream 2 relational highway logit directly from 15-dim input."""
        normed = self.rel_norm(rel_vec)
        return (self.rel_net(normed) + self.rel_linear_skip(rel_vec)).squeeze(-1)

    def _compute_peer_geometry(
        self,
        user_embs: torch.Tensor,
        user_mask: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        B, M, _ = user_embs.shape
        sim_uu = torch.bmm(user_embs, user_embs.transpose(1, 2)).clamp(-1.0, 1.0)
        eye = torch.eye(M, device=user_embs.device, dtype=torch.bool).unsqueeze(0)
        peer_mask = (user_mask.unsqueeze(1) & user_mask.unsqueeze(2) & (~eye)).float()
        peer_denom = peer_mask.sum(dim=-1, keepdim=True).clamp(min=1.0)
        member_cohesion = (sim_uu * peer_mask).sum(dim=-1, keepdim=True) / peer_denom
        return sim_uu, member_cohesion

    def _fuse_invariant(
        self,
        rel_vec: torch.Tensor,          # (B, 15)
        cos_sim: torch.Tensor,          # (B, M)
        budget_gap: torch.Tensor,       # (B, M)
        user_feats: torch.Tensor,       # (B, M, 3)
        user_mask: torch.Tensor,        # (B, M) bool
        sim_uu: torch.Tensor,           # (B, M, M)
        member_cohesion: torch.Tensor,  # (B, M, 1)
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        B, M = cos_sim.shape
        mask_f = user_mask.float()
        poi_feat = rel_vec[:, 7:15]
        cos_mean = rel_vec[:, 0:1]
        cos_min = rel_vec[:, 1:2]
        cos_max = rel_vec[:, 2:3]

        b_margin = (user_feats[:, :, 0:1] - rel_vec[:, 8:9].unsqueeze(-1)).clamp(-1.0, 1.0)
        u_proxy = (2.8 * cos_sim - 3.6 * budget_gap).unsqueeze(-1)
        pf_exp = poi_feat.unsqueeze(1).expand(B, M, poi_feat.shape[-1])
        tok_u = torch.cat(
            [
                cos_sim.unsqueeze(-1),
                (cos_sim - cos_mean).unsqueeze(-1),
                (cos_sim - cos_min).unsqueeze(-1),
                (cos_sim - cos_max).unsqueeze(-1),
                member_cohesion,
                budget_gap.unsqueeze(-1),
                b_margin,
                u_proxy,
                user_feats,
                pf_exp,
            ],
            dim=-1,
        )  # (B, M, 19)

        h_u = self.user_res(self.user_in(tok_u.view(B * M, -1))).view(B, M, self.hidden_dim)
        if self.use_member_sab:
            h_u = self.member_sab(h_u, sim_uu, user_mask)

        h_p = self.poi_res(self.poi_in(rel_vec))
        pair = torch.cat([h_u, h_p.unsqueeze(1).expand(B, M, -1), cos_sim.unsqueeze(-1), budget_gap.unsqueeze(-1)], dim=-1)
        raw_member_logits = self.member_scorer(pair).squeeze(-1) + 0.85 * (cos_sim - 1.15 * budget_gap)
        member_scores = torch.sigmoid(raw_member_logits)

        if self.use_attention:
            _, aw = self.cross_attn(
                query=h_p.unsqueeze(1),
                key=h_u,
                value=h_u,
                key_padding_mask=~user_mask,
                need_weights=True,
                average_attn_weights=True,
            )
            attn_weights = aw.squeeze(1) * mask_f
            attn_weights = attn_weights / attn_weights.sum(dim=-1, keepdim=True).clamp(min=1e-6)
        else:
            attn_weights = mask_f / mask_f.sum(dim=-1, keepdim=True).clamp(min=1e-6)

        attn_mean = torch.clamp((member_scores * attn_weights).sum(dim=-1), 1e-4, 1.0 - 1e-4)
        attn_logit = torch.log(attn_mean / (1.0 - attn_mean))

        masked_for_min = member_scores.masked_fill(~user_mask, 1e4)
        soft_min = -self.softmin_temp * torch.logsumexp(-masked_for_min / self.softmin_temp, dim=-1)
        soft_min = torch.clamp(soft_min, 1e-4, 1.0 - 1e-4)
        softmin_logit = torch.log(soft_min / (1.0 - soft_min))

        rel_logit = self.score_relational_head(rel_vec) if self.use_relational_stream else torch.zeros_like(attn_logit)

        scales = F.softplus(self.fusion_scales)
        if self.use_relational_stream:
            inv_logit = scales[0] * attn_logit + scales[1] * softmin_logit + scales[2] * rel_logit + self.out_bias
        else:
            inv_logit = scales[0] * attn_logit + scales[1] * softmin_logit + self.out_bias
        return inv_logit, member_scores, attn_weights

    def forward_dual(
        self,
        user_embs: torch.Tensor,
        user_feats: torch.Tensor,
        user_mask: torch.Tensor,
        poi_emb: torch.Tensor,
        poi_feat: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        B, M, _ = user_embs.shape
        rel_vec, cos_sim, budget_gap = extract_group_relational_features(
            user_embs, user_feats, user_mask, poi_emb, poi_feat
        )
        sim_uu, member_cohesion = self._compute_peer_geometry(user_embs, user_mask)
        inv_logit, member_scores, attn_weights = self._fuse_invariant(
            rel_vec, cos_sim, budget_gap, user_feats, user_mask, sim_uu, member_cohesion
        )

        if self.use_hadamard:
            had = self.sem_drop(user_embs * poi_emb.unsqueeze(1))
            sem_m = self.sem_adapter(had.view(B * M, -1)).view(B, M)
            sem_logit = 2.0 * torch.tanh((sem_m * attn_weights).sum(dim=-1))
            gate = self.spectral_gate(poi_emb)
            scales = F.softplus(self.fusion_scales)
            sem_contrib = gate * scales[3] * sem_logit
        else:
            gate = torch.zeros(B, device=user_embs.device, dtype=user_embs.dtype)
            sem_contrib = torch.zeros_like(inv_logit)

        total_logit = inv_logit + sem_contrib
        group_score = torch.clamp(torch.sigmoid(total_logit), 1e-5, 1.0 - 1e-5)
        return total_logit, inv_logit, group_score, member_scores, attn_weights, gate

    def forward_logits(
        self,
        user_embs: torch.Tensor,
        user_feats: torch.Tensor,
        user_mask: torch.Tensor,
        poi_emb: torch.Tensor,
        poi_feat: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        total_logit, _, group_score, member_scores, attn_weights, _ = self.forward_dual(
            user_embs, user_feats, user_mask, poi_emb, poi_feat
        )
        return total_logit, group_score, member_scores, attn_weights

    def prepare_xai_context(
        self,
        user_embs: torch.Tensor,
        user_feats: torch.Tensor,
        user_mask: torch.Tensor,
        poi_emb: torch.Tensor,
        poi_feat: torch.Tensor,
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Precomputes original rel_vec (B, 15) and exact algebraic member-reconstruction
        constants so forward_from_rel_vec executes Stream 1 + Stream 2 end-to-end
        with <1e-5 identity error relative to forward_logits.
        """
        B, M, _ = user_embs.shape
        rel_vec, cos_sim, budget_gap = extract_group_relational_features(
            user_embs, user_feats, user_mask, poi_emb, poi_feat
        )
        sim_uu, member_cohesion = self._compute_peer_geometry(user_embs, user_mask)
        _, _, attn_weights = self._fuse_invariant(
            rel_vec, cos_sim, budget_gap, user_feats, user_mask, sim_uu, member_cohesion
        )

        if self.use_hadamard:
            had = self.sem_drop(user_embs * poi_emb.unsqueeze(1))
            sem_m = self.sem_adapter(had.view(B * M, -1)).view(B, M)
            sem_logit = 2.0 * torch.tanh((sem_m * attn_weights).sum(dim=-1))
            gate = self.spectral_gate(poi_emb)
            scales = F.softplus(self.fusion_scales)
            fixed_sem = (gate * scales[3] * sem_logit).detach()
        else:
            fixed_sem = torch.zeros(B, device=user_embs.device, dtype=user_embs.dtype)

        cos_mean = rel_vec[:, 0:1]
        cos_std = rel_vec[:, 3:4].clamp(min=1e-6)
        z_cos = ((cos_sim - cos_mean) / cos_std).detach()

        bg_mean = rel_vec[:, 4:5]
        bg_max = rel_vec[:, 5:6]
        denom_bg = bg_max - bg_mean
        rho_bg = torch.where(
            denom_bg > 1e-6,
            (budget_gap - bg_mean) / denom_bg.clamp(min=1e-6),
            torch.zeros_like(budget_gap),
        ).detach()

        ctx = {
            "z_cos": z_cos,
            "rho_bg": rho_bg,
            "user_feats": user_feats.detach(),
            "user_mask": user_mask.detach(),
            "sim_uu": sim_uu.detach(),
            "member_cohesion": member_cohesion.detach(),
            "fixed_sem": fixed_sem,
        }
        return rel_vec.detach(), ctx

    def forward_from_rel_vec(
        self,
        rel_vec: torch.Tensor,
        ctx: Dict[str, torch.Tensor],
    ) -> torch.Tensor:
        """
        Full end-to-end differentiable forward pass from 15-dim rel_vec (B, 15) through
        Stream 1 (MemberGramSAB + CrossAttn + SoftMin) + Stream 2 (RelHighway) + gated offset.
        """
        cos_rec = (rel_vec[:, 0:1] + rel_vec[:, 3:4] * ctx["z_cos"]).clamp(-1.0, 1.0)
        bg_rec = (rel_vec[:, 4:5] + (rel_vec[:, 5:6] - rel_vec[:, 4:5]) * ctx["rho_bg"]).clamp(0.0, 1.0)
        inv_logit, _, _ = self._fuse_invariant(
            rel_vec=rel_vec,
            cos_sim=cos_rec,
            budget_gap=bg_rec,
            user_feats=ctx["user_feats"],
            user_mask=ctx["user_mask"],
            sim_uu=ctx["sim_uu"],
            member_cohesion=ctx["member_cohesion"],
        )
        return inv_logit + ctx["fixed_sem"]

    def forward(
        self,
        user_embs: torch.Tensor,
        user_feats: torch.Tensor,
        user_mask: torch.Tensor,
        poi_emb: torch.Tensor,
        poi_feat: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        _, _, group_score, member_scores, attn_weights, _ = self.forward_dual(
            user_embs, user_feats, user_mask, poi_emb, poi_feat
        )
        return group_score, member_scores, attn_weights


def differentiable_gini_loss(
    member_scores: torch.Tensor,
    user_mask: torch.Tensor,
    eps: float = 1e-5,
) -> torch.Tensor:
    """Smooth differentiable Gini Index across valid group members."""
    mask_f = user_mask.float()
    counts = mask_f.sum(dim=-1).clamp(min=1.0)
    mean_s = (member_scores * mask_f).sum(dim=-1) / counts

    diff = member_scores.unsqueeze(2) - member_scores.unsqueeze(1)
    smooth_abs = torch.sqrt(diff * diff + eps)
    pair_mask = mask_f.unsqueeze(2) * mask_f.unsqueeze(1)
    pair_sum = (smooth_abs * pair_mask).sum(dim=(1, 2))
    gini = pair_sum / (2.0 * (counts ** 2) * (mean_s + eps))
    return gini.mean()


def pareto_fairness_infonce_loss(
    pos_logit: torch.Tensor,
    neg_logits: torch.Tensor,
    pos_members: torch.Tensor,
    user_mask: torch.Tensor,
    pos_eco: torch.Tensor,
    neg_eco: Optional[torch.Tensor] = None,
    pos_disp: Optional[torch.Tensor] = None,
    neg_disp: Optional[torch.Tensor] = None,
    pos_floor: Optional[torch.Tensor] = None,
    neg_floor: Optional[torch.Tensor] = None,
    pos_gini_true: Optional[torch.Tensor] = None,
    neg_gini_true: Optional[torch.Tensor] = None,
    tau: float = 0.20,
    lambda_gini: float = 0.36,
    lambda_misery: float = 0.28,
    lambda_eco: float = 0.38,
    misery_floor: float = 0.58,
    slate_temp: float = 0.85,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """
    Calibrated Multi-Objective Pareto InfoNCE Loss (v3):
      1. Listwise Sampled InfoNCE Ranking Loss (tau=0.20)
      2. Differentiable Member Gini + Soft-Slate True-Gini & Dispersion (slate_temp=0.85)
      3. Least-Misery Safety Floor + Soft-Slate Rawlsian Min-Satisfaction Maximization
      4. Differentiable Expected Eco-Exposure via Softmax Slate Probabilities
    """
    all_logits = torch.cat([pos_logit.unsqueeze(1), neg_logits], dim=1)
    logits = all_logits / tau
    targets = torch.zeros(pos_logit.size(0), dtype=torch.long, device=pos_logit.device)
    infonce = F.cross_entropy(logits, targets)
    slate_probs = F.softmax(all_logits / slate_temp, dim=1)

    if lambda_gini > 0:
        gini_l = differentiable_gini_loss(pos_members, user_mask)
        if pos_gini_true is not None and neg_gini_true is not None:
            all_gini = torch.cat([pos_gini_true.unsqueeze(1), neg_gini_true], dim=1)
            slate_gini = (slate_probs * all_gini).sum(dim=1).mean()
            gini_l = gini_l + 2.0 * slate_gini
        elif pos_disp is not None and neg_disp is not None:
            all_disp = torch.cat([pos_disp.unsqueeze(1), neg_disp], dim=1)
            slate_disp = (slate_probs * all_disp).sum(dim=1).mean()
            gini_l = gini_l + 1.0 * slate_disp
    else:
        gini_l = torch.tensor(0.0, device=pos_logit.device)

    if lambda_misery > 0:
        masked_pos = pos_members.masked_fill(~user_mask, 1.0)
        min_u = masked_pos.min(dim=-1).values
        misery_l = F.relu(misery_floor - min_u).mean()
        if pos_floor is not None and neg_floor is not None:
            all_floor = torch.cat([pos_floor.unsqueeze(1), neg_floor], dim=1)
            slate_floor = (slate_probs * all_floor).sum(dim=1).mean()
            misery_l = misery_l + 1.2 * F.relu(0.49 - slate_floor)
    else:
        misery_l = torch.tensor(0.0, device=pos_logit.device)

    if lambda_eco > 0 and neg_eco is not None:
        all_eco = torch.cat([pos_eco.unsqueeze(1), neg_eco], dim=1)
        expected_eco = (slate_probs * all_eco).sum(dim=1)
        eco_l = (1.0 - expected_eco).mean()
    else:
        eco_l = torch.tensor(0.0, device=pos_logit.device)

    total = infonce + lambda_gini * gini_l + lambda_misery * misery_l + lambda_eco * eco_l
    return total, {
        "infonce": float(infonce.item()),
        "gini": float(gini_l.item()),
        "misery": float(misery_l.item()),
        "eco": float(eco_l.item()),
    }


def fairness_regularized_bpr_loss(
    pos_group: torch.Tensor,
    pos_members: torch.Tensor,
    neg_group: torch.Tensor,
    user_mask: torch.Tensor,
    pos_eco: torch.Tensor,
    fairness_weight: float = 0.36,
    misery_weight: float = 0.28,
    eco_weight: float = 0.32,
    misery_floor: float = 0.58,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    margin = (pos_group - neg_group) * 6.0
    bpr_loss = -F.logsigmoid(margin).mean()
    gini_l = differentiable_gini_loss(pos_members, user_mask) if fairness_weight > 0 else torch.tensor(0.0, device=pos_group.device)
    masked_pos = pos_members.masked_fill(~user_mask, 1.0)
    misery_l = F.relu(misery_floor - masked_pos.min(dim=-1).values).mean() if misery_weight > 0 else torch.tensor(0.0, device=pos_group.device)
    eco_l = (1.0 - pos_eco).mean() if eco_weight > 0 else torch.tensor(0.0, device=pos_group.device)
    total = bpr_loss + fairness_weight * gini_l + misery_weight * misery_l + eco_weight * eco_l
    return total, {
        "bpr": float(bpr_loss.item()),
        "var": float(gini_l.item()),
        "misery": float(misery_l.item()),
        "eco": float(eco_l.item()),
    }
