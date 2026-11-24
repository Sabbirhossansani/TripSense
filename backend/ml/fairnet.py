"""
TripSense-FairNet: Neural Group Fairness & Cross-Attention Consensus Model.

Architecture:
  - POI Encoder: Projects SigLIP multimodal embedding (D) + 8 continuous context/eco features
    through a LayerNorm-GELU residual MLP into a 128-d unified space.
  - Member Encoder: Projects each member's continuous taste embedding (D) + 3 profile context
    features (budget tier, preference entropy, flexibility) into 128-d.
  - Individual Utility Head: Predicts per-member satisfaction y_{u,p} in [0, 1].
  - Cross-Attention Consensus Head: Queries member representations with candidate POI context
    to learn adaptive group member weights alpha_{u,g,p}, combined with a differentiable
    soft-min Least-Misery safety gate and sustainability regularizer.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


class ResidualBlock(nn.Module):
    def __init__(self, dim: int, dropout: float = 0.15):
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


class TripSenseFairNet(nn.Module):
    def __init__(
        self,
        emb_dim: int = 768,
        poi_feat_dim: int = 8,
        user_feat_dim: int = 3,
        hidden_dim: int = 128,
        num_heads: int = 4,
        dropout: float = 0.15,
        softmin_temp: float = 0.15,
    ):
        super().__init__()
        self.emb_dim = emb_dim
        self.hidden_dim = hidden_dim
        self.softmin_temp = softmin_temp

        # 1. POI Multimodal + Context Projection
        self.poi_in = nn.Sequential(
            nn.Linear(emb_dim + poi_feat_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.poi_res = ResidualBlock(hidden_dim, dropout)

        # 2. User Taste + Budget Projection
        self.user_in = nn.Sequential(
            nn.Linear(emb_dim + user_feat_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.user_res = ResidualBlock(hidden_dim, dropout)

        # 3. Per-Member Satisfaction Head: [h_u, h_p, h_u * h_p, raw_cos, poi_feat] -> y_{u,p}
        self.member_scorer = nn.Sequential(
            nn.Linear(hidden_dim * 3 + 1 + poi_feat_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )

        # 4. Cross-Attention Group Consensus Head
        self.cross_attn = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        self.attn_norm = nn.LayerNorm(hidden_dim)

        # Predicts scalar gate mixing learned attention-weighted utility and soft-min protection
        self.consensus_gate = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.GELU(),
            nn.Linear(64, 2),
        )

    def forward(
        self,
        user_embs: torch.Tensor,      # (B, M, emb_dim)
        user_feats: torch.Tensor,     # (B, M, user_feat_dim)
        user_mask: torch.Tensor,      # (B, M) bool, True = valid member
        poi_emb: torch.Tensor,        # (B, emb_dim)
        poi_feat: torch.Tensor,       # (B, poi_feat_dim)
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Returns:
          group_score: (B,) predicted fair group utility in (0, 1)
          member_scores: (B, M) predicted individual utilities in (0, 1)
          attn_weights: (B, M) learned member influence weights summing to 1 over valid members
        """
        B, M, _ = user_embs.shape

        # Encode POI -> (B, H)
        h_p = self.poi_res(self.poi_in(torch.cat([poi_emb, poi_feat], dim=-1)))

        # Encode Users -> (B, M, H)
        u_cat = torch.cat([user_embs, user_feats], dim=-1)
        h_u = self.user_res(self.user_in(u_cat.view(B * M, -1))).view(B, M, self.hidden_dim)

        # Expand POI to match members -> (B, M, H), preserving raw cosine & tabular skip signals
        h_p_exp = h_p.unsqueeze(1).expand(B, M, self.hidden_dim)
        raw_cos = (user_embs * poi_emb.unsqueeze(1)).sum(dim=-1, keepdim=True)
        pf_exp = poi_feat.unsqueeze(1).expand(B, M, poi_feat.shape[-1])
        pair = torch.cat([h_u, h_p_exp, h_u * h_p_exp, raw_cos, pf_exp], dim=-1)
        raw_member_logits = self.member_scorer(pair).squeeze(-1)  # (B, M)
        member_scores = torch.sigmoid(raw_member_logits)

        # Cross-attention: POI queries group members
        # key_padding_mask expects True for positions to IGNORE
        pad_mask = ~user_mask
        attn_out, attn_w = self.cross_attn(
            query=h_p.unsqueeze(1),
            key=h_u,
            value=h_u,
            key_padding_mask=pad_mask,
            need_weights=True,
            average_attn_weights=True,
        )
        attn_weights = attn_w.squeeze(1)  # (B, M)
        # Ensure masked weights are strictly zero and renormalized
        attn_weights = attn_weights * user_mask.float()
        attn_weights = attn_weights / attn_weights.sum(dim=-1, keepdim=True).clamp(min=1e-6)

        # Weighted mean satisfaction
        attn_mean_score = (member_scores * attn_weights).sum(dim=-1)  # (B,)

        # Differentiable soft-min (Least-Misery protection): -T * logsumexp(-s / T)
        masked_for_min = member_scores.masked_fill(~user_mask, 1e4)
        soft_min_score = -self.softmin_temp * torch.logsumexp(-masked_for_min / self.softmin_temp, dim=-1)
        soft_min_score = torch.clamp(soft_min_score, 0.0, 1.0)

        # Adaptive gate conditioned on POI + attended group state
        h_group = self.attn_norm(attn_out.squeeze(1) + h_p)
        gate_weights = F.softmax(self.consensus_gate(torch.cat([h_p, h_group], dim=-1)), dim=-1)

        group_score = gate_weights[:, 0] * attn_mean_score + gate_weights[:, 1] * soft_min_score
        group_score = torch.clamp(group_score, 1e-5, 1.0 - 1e-5)

        return group_score, member_scores, attn_weights


def fairness_regularized_bpr_loss(
    pos_group: torch.Tensor,      # (B,)
    pos_members: torch.Tensor,    # (B, M)
    neg_group: torch.Tensor,      # (B,)
    user_mask: torch.Tensor,      # (B, M)
    pos_eco: torch.Tensor,        # (B,) normalized eco score in [0, 1]
    fairness_weight: float = 0.35,
    misery_weight: float = 0.30,
    eco_weight: float = 0.10,
    misery_floor: float = 0.60,
) -> Tuple[torch.Tensor, dict]:
    """
    Multi-objective Q1 Loss:
      L = L_BPR(pos, neg) + lambda_1 * Var_u(y_{u,p+}) + lambda_2 * ReLU(tau - min_u y_{u,p+}) + lambda_3 * (1 - eco)
    """
    # Pairwise ranking BPR loss (on logit margin scaled for sharp separation)
    margin = (pos_group - neg_group) * 6.0
    bpr_loss = -F.logsigmoid(margin).mean()

    if fairness_weight == 0.0 and misery_weight == 0.0:
        return bpr_loss, {"bpr": float(bpr_loss.item()), "var": 0.0, "misery": 0.0, "eco": 0.0}

    # Masked variance across group members on positive item
    mask_f = user_mask.float()
    counts = mask_f.sum(dim=-1, keepdim=True).clamp(min=1.0)
    mean_u = (pos_members * mask_f).sum(dim=-1, keepdim=True) / counts
    sq_diff = ((pos_members - mean_u) ** 2) * mask_f
    var_loss = (sq_diff.sum(dim=-1) / counts.squeeze(-1)).mean()

    # Minimum member satisfaction protection
    masked_pos = pos_members.masked_fill(~user_mask, 1.0)
    min_u, _ = masked_pos.min(dim=-1)
    misery_loss = F.relu(misery_floor - min_u).mean()

    # Eco-sustainability encouragement
    eco_loss = (1.0 - pos_eco).mean()

    total = bpr_loss + fairness_weight * var_loss + misery_weight * misery_loss + eco_weight * eco_loss
    return total, {
        "bpr": float(bpr_loss.item()),
        "var": float(var_loss.item()),
        "misery": float(misery_loss.item()),
        "eco": float(eco_loss.item()),
    }
