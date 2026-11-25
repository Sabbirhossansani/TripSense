"""
TripSense-FairNet v2: Hybrid Rotation-Invariant + Bounded Hadamard FairNet v2.

Key Architectural Innovations for Q1 Publication:
  1. Hybrid Rotation-Invariant + Bounded Semantic Cross-Attention Stream:
       Encodes each member u via exact domain-invariant geometric consensus tokens:
         [cos_u, cos_u - cos_mean, cos_u - cos_min, member_cohesion, budget_gap_u, user_feats(3), poi_feat(8)]
       fused with a bounded low-rank Hadamard semantic residual (0.35 * tanh(sem_proj(drop(e_u * e_p))))
       that captures fine-grained intra-city category affinity while preventing unbounded out-of-domain drift
       across unseen cities (Melbourne, Tokyo, New-York).
  2. City-Invariant 15-d Group-Relational Highway (Without Input LayerNorm Distortion):
       Operates directly on un-squashed [cos_mean, cos_min, cos_max, cos_std, bg_mean, bg_max, m_norm, poi_feat(8)]
       with hidden-layer LayerNorm-GELU residual MLPs + linear skip for strong generalization and exact
       Integrated Gradients attribution (Axiom 1 Completeness).
  3. Additive Softplus Consensus Fusion & Calibrated Multi-Objective Pareto InfoNCE:
       Fuses cross-attention consensus logit, soft-min misery logit, and relational highway logit,
       trained over all positive group targets via 20-negative InfoNCE + Differentiable Gini +
       Soft-Slate Rawlsian Dispersion + Least-Misery Safety Floor + Expected Eco-Exposure.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict


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
        softmin_temp: float = 0.14,
        use_attention: bool = True,
        use_relational_stream: bool = True,
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

        # ── Stream 1: Hybrid Rotation-Invariant + Bounded Semantic Cross-Attention ─
        self.rel_dim = 7 + poi_feat_dim  # 15
        self.emb_drop = nn.Dropout(0.35)
        self.sem_dim = 24
        self.sem_proj = nn.Sequential(
            nn.Linear(emb_dim, self.sem_dim),
            nn.LayerNorm(self.sem_dim),
            nn.Tanh(),
        )

        tok_u_dim = 5 + user_feat_dim + poi_feat_dim + self.sem_dim  # 40
        self.user_in = nn.Sequential(
            nn.Linear(tok_u_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.user_res = ResidualBlock(hidden_dim, dropout)

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

        # ── Stream 2: City-Invariant 15-dim Group-Relational Highway (No Input LayerNorm Distortion) ─
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

        # Additive softplus stream scales + bias
        self.fusion_scales = nn.Parameter(torch.tensor([0.75, 0.25, 1.35], dtype=torch.float32))
        self.out_bias = nn.Parameter(torch.zeros(1, dtype=torch.float32))

    def score_relational_head(self, rel_vec: torch.Tensor) -> torch.Tensor:
        """Evaluates Stream 2 relational highway logit directly from 15-dim input."""
        normed = self.rel_norm(rel_vec)
        return (self.rel_net(normed) + self.rel_linear_skip(rel_vec)).squeeze(-1)

    def forward_logits(
        self,
        user_embs: torch.Tensor,
        user_feats: torch.Tensor,
        user_mask: torch.Tensor,
        poi_emb: torch.Tensor,
        poi_feat: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        B, M, _ = user_embs.shape
        rel_vec, cos_sim, budget_gap = extract_group_relational_features(
            user_embs, user_feats, user_mask, poi_emb, poi_feat
        )

        # Bounded low-rank Hadamard semantic agreement in [-0.35, +0.35]
        hadamard = self.emb_drop(user_embs * poi_emb.unsqueeze(1))
        h_sem = 0.35 * self.sem_proj(hadamard.view(B * M, -1)).view(B, M, self.sem_dim)

        # Rotation-invariant intra-group geometric features per member
        cos_mean = rel_vec[:, 0:1]
        cos_min = rel_vec[:, 1:2]
        cos_rel_mean = (cos_sim - cos_mean).unsqueeze(-1)
        cos_rel_min = (cos_sim - cos_min).unsqueeze(-1)

        mask_f = user_mask.float()
        sim_uu = torch.bmm(user_embs, user_embs.transpose(1, 2)).clamp(-1.0, 1.0)
        eye = torch.eye(M, device=user_embs.device, dtype=torch.bool).unsqueeze(0)
        peer_mask = (user_mask.unsqueeze(1) & user_mask.unsqueeze(2) & (~eye)).float()
        peer_denom = peer_mask.sum(dim=-1, keepdim=True).clamp(min=1.0)
        member_cohesion = (sim_uu * peer_mask).sum(dim=-1, keepdim=True) / peer_denom

        pf_exp = poi_feat.unsqueeze(1).expand(B, M, poi_feat.shape[-1])
        tok_u = torch.cat(
            [
                cos_sim.unsqueeze(-1),
                cos_rel_mean,
                cos_rel_min,
                member_cohesion,
                budget_gap.unsqueeze(-1),
                user_feats,
                pf_exp,
                h_sem,
            ],
            dim=-1,
        )  # (B, M, 40)

        h_u = self.user_res(self.user_in(tok_u.view(B * M, -1))).view(B, M, self.hidden_dim)
        h_p = self.poi_res(self.poi_in(rel_vec))

        h_p_exp = h_p.unsqueeze(1).expand(B, M, self.hidden_dim)
        pair = torch.cat([h_u, h_p_exp, cos_sim.unsqueeze(-1), budget_gap.unsqueeze(-1)], dim=-1)
        raw_member_logits = self.member_scorer(pair).squeeze(-1) + 0.75 * (cos_sim - 0.8 * budget_gap)
        member_scores = torch.sigmoid(raw_member_logits)

        if self.use_attention:
            pad_mask = ~user_mask
            _, attn_w = self.cross_attn(
                query=h_p.unsqueeze(1),
                key=h_u,
                value=h_u,
                key_padding_mask=pad_mask,
                need_weights=True,
                average_attn_weights=True,
            )
            attn_weights = attn_w.squeeze(1) * mask_f
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
            group_logit = scales[0] * attn_logit + scales[1] * softmin_logit + scales[2] * rel_logit + self.out_bias
        else:
            group_logit = scales[0] * attn_logit + scales[1] * softmin_logit + self.out_bias

        group_score = torch.clamp(torch.sigmoid(group_logit), 1e-5, 1.0 - 1e-5)
        return group_logit, group_score, member_scores, attn_weights

    def forward(
        self,
        user_embs: torch.Tensor,
        user_feats: torch.Tensor,
        user_mask: torch.Tensor,
        poi_emb: torch.Tensor,
        poi_feat: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        _, group_score, member_scores, attn_weights = self.forward_logits(
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
    neg_eco: torch.Tensor = None,
    pos_disp: torch.Tensor = None,
    neg_disp: torch.Tensor = None,
    pos_floor: torch.Tensor = None,
    neg_floor: torch.Tensor = None,
    tau: float = 0.20,
    lambda_gini: float = 0.30,
    lambda_misery: float = 0.20,
    lambda_eco: float = 0.35,
    misery_floor: float = 0.58,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """
    Calibrated Multi-Objective Pareto Loss:
      1. Listwise Sampled InfoNCE Ranking Loss (tau=0.20)
      2. Differentiable Intra-Group Gini + Calibrated Soft-Slate Dispersion (0.9x)
      3. Least-Misery Safety Floor + Calibrated Soft-Slate Floor Protection (0.6x)
      4. Differentiable Expected Eco-Exposure via Softmax Slate Probabilities
    """
    all_logits = torch.cat([pos_logit.unsqueeze(1), neg_logits], dim=1)
    logits = all_logits / tau
    targets = torch.zeros(pos_logit.size(0), dtype=torch.long, device=pos_logit.device)
    infonce = F.cross_entropy(logits, targets)
    slate_probs = F.softmax(all_logits / 1.5, dim=1)

    if lambda_gini > 0:
        gini_l = differentiable_gini_loss(pos_members, user_mask)
        if pos_disp is not None and neg_disp is not None:
            all_disp = torch.cat([pos_disp.unsqueeze(1), neg_disp], dim=1)
            slate_disp = (slate_probs * all_disp).sum(dim=1).mean()
            gini_l = gini_l + 0.9 * slate_disp
    else:
        gini_l = torch.tensor(0.0, device=pos_logit.device)

    if lambda_misery > 0:
        masked_pos = pos_members.masked_fill(~user_mask, 1.0)
        min_u = masked_pos.min(dim=-1).values
        misery_l = F.relu(misery_floor - min_u).mean()
        if pos_floor is not None and neg_floor is not None:
            all_floor = torch.cat([pos_floor.unsqueeze(1), neg_floor], dim=1)
            slate_floor = (slate_probs * all_floor).sum(dim=1).mean()
            misery_l = misery_l + 0.6 * F.relu(0.10 - slate_floor)
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
    fairness_weight: float = 0.30,
    misery_weight: float = 0.20,
    eco_weight: float = 0.35,
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
