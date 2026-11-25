"""
Neural Group Recommendation Baselines for Q1 Benchmarking:
  1. AGREEBaseline: Faithful PyTorch adaptation of Cao et al. (SIGIR 2018),
     "Attentive Group Recommendation" (Neural Attention over group member
     embeddings + NCF interaction tower with pairwise BPR ranking).
  2. GroupMLPBaseline: Deep Neural Pairwise Group MLP over mean-pooled
     member taste vectors + POI semantic + context features.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


class AGREEBaseline(nn.Module):
    """
    AGREE (Cao et al., SIGIR 2018): Attentive Group Recommendation adapted for
    inductive multimodal member-history + POI context representations.
    """

    def __init__(
        self,
        emb_dim: int = 512,
        poi_feat_dim: int = 8,
        user_feat_dim: int = 3,
        hidden_dim: int = 64,
        dropout: float = 0.25,
    ):
        super().__init__()
        self.user_proj = nn.Sequential(
            nn.Linear(emb_dim + user_feat_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        self.poi_proj = nn.Sequential(
            nn.Linear(emb_dim + poi_feat_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        # AGREE member-item attention network
        self.attn_net = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )
        # NCF fusion over (h_group * h_poi, h_group, h_poi, raw_mean_cos)
        self.ncf_head = nn.Sequential(
            nn.Linear(hidden_dim * 3 + 1, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )

    def forward(
        self,
        user_embs: torch.Tensor,
        user_feats: torch.Tensor,
        user_mask: torch.Tensor,
        poi_emb: torch.Tensor,
        poi_feat: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        B, M, _ = user_embs.shape
        h_u = self.user_proj(torch.cat([user_embs, user_feats], dim=-1))  # (B, M, H)
        h_p = self.poi_proj(torch.cat([poi_emb, poi_feat], dim=-1))       # (B, H)
        h_p_exp = h_p.unsqueeze(1).expand(B, M, -1)

        attn_logits = self.attn_net(torch.cat([h_u, h_p_exp], dim=-1)).squeeze(-1)  # (B, M)
        attn_logits = attn_logits.masked_fill(~user_mask, -1e9)
        alpha = F.softmax(attn_logits, dim=-1) * user_mask.float()
        alpha = alpha / alpha.sum(dim=-1, keepdim=True).clamp(min=1e-6)

        h_group = (alpha.unsqueeze(-1) * h_u).sum(dim=1)  # (B, H)

        mask_f = user_mask.float()
        cos_sim = (user_embs * poi_emb.unsqueeze(1)).sum(dim=-1)
        mean_cos = (cos_sim * mask_f).sum(dim=-1, keepdim=True) / mask_f.sum(dim=-1, keepdim=True).clamp(min=1.0)

        joint = torch.cat([h_group * h_p, h_group, h_p, mean_cos], dim=-1)
        logit = self.ncf_head(joint).squeeze(-1)
        return logit, alpha


class GroupMLPBaseline(nn.Module):
    """
    Deep Neural Pairwise Group MLP pooling member embeddings by mean and scoring against POI features.
    """

    def __init__(
        self,
        emb_dim: int = 512,
        poi_feat_dim: int = 8,
        user_feat_dim: int = 3,
        hidden_dim: int = 64,
        dropout: float = 0.25,
    ):
        super().__init__()
        in_dim = emb_dim * 2 + user_feat_dim + poi_feat_dim + 1
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, hidden_dim * 2),
            nn.LayerNorm(hidden_dim * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(
        self,
        user_embs: torch.Tensor,
        user_feats: torch.Tensor,
        user_mask: torch.Tensor,
        poi_emb: torch.Tensor,
        poi_feat: torch.Tensor,
    ) -> torch.Tensor:
        mask_f = user_mask.float().unsqueeze(-1)
        denom = mask_f.sum(dim=1).clamp(min=1.0)
        mean_u_emb = (user_embs * mask_f).sum(dim=1) / denom
        mean_u_feat = (user_feats * mask_f).sum(dim=1) / denom
        mean_cos = (mean_u_emb * poi_emb).sum(dim=-1, keepdim=True)
        x = torch.cat([mean_u_emb, poi_emb, mean_u_feat, poi_feat, mean_cos], dim=-1)
        return self.mlp(x).squeeze(-1)
