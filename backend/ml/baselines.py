"""
Neural Group Recommendation Baselines for Q1 Benchmarking:
  1. DeepSetsBaseline (Zaheer et al., NeurIPS 2017):
       Permutation-invariant member encoder + mean/sum pooling + post-pool scorer.
  2. AGREEBaseline (Cao et al., SIGIR 2018):
       Attentive Group Recommendation (member-item attention + NCF interaction tower).
  3. MoSANBaseline (Tran et al., SIGIR 2019):
       Medley of Sub-Attention Networks modeling peer-to-peer group voting sub-networks.
  4. SetTransformerBaseline (Lee et al., ICML 2019):
       Multi-head Self-Attention Block (SAB) over members + Pooling by Multihead Attention (PMA).
  5. GroupIMBaseline (Sankar et al., SIGIR 2020):
       Attentive group pooling with Bilinear User-Group Mutual Information (InfoNCE) auxiliary loss.
  6. GroupMLPBaseline:
       Deep Neural Pairwise Group MLP over mean-pooled member taste + POI context.
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
        self.attn_net = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )
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
        h_u = self.user_proj(torch.cat([user_embs, user_feats], dim=-1))
        h_p = self.poi_proj(torch.cat([poi_emb, poi_feat], dim=-1))
        h_p_exp = h_p.unsqueeze(1).expand(B, M, -1)

        attn_logits = self.attn_net(torch.cat([h_u, h_p_exp], dim=-1)).squeeze(-1)
        attn_logits = attn_logits.masked_fill(~user_mask, -1e9)
        alpha = F.softmax(attn_logits, dim=-1) * user_mask.float()
        alpha = alpha / alpha.sum(dim=-1, keepdim=True).clamp(min=1e-6)

        h_group = (alpha.unsqueeze(-1) * h_u).sum(dim=1)
        mask_f = user_mask.float()
        cos_sim = (user_embs * poi_emb.unsqueeze(1)).sum(dim=-1)
        mean_cos = (cos_sim * mask_f).sum(dim=-1, keepdim=True) / mask_f.sum(dim=-1, keepdim=True).clamp(min=1.0)

        joint = torch.cat([h_group * h_p, h_group, h_p, mean_cos], dim=-1)
        logit = self.ncf_head(joint).squeeze(-1)
        return logit, alpha


class DeepSetsBaseline(nn.Module):
    """
    DeepSets (Zaheer et al., NeurIPS 2017): Permutation-invariant phi-rho set pooling
    applied over companion embeddings and budgets paired with POI context.
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
        self.phi = nn.Sequential(
            nn.Linear(emb_dim + user_feat_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
        )
        self.poi_enc = nn.Sequential(
            nn.Linear(emb_dim + poi_feat_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
        )
        self.rho = nn.Sequential(
            nn.Linear(hidden_dim * 2 + 1, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
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
    ) -> torch.Tensor:
        h_u = self.phi(torch.cat([user_embs, user_feats], dim=-1))
        mask_f = user_mask.float()
        denom = mask_f.sum(dim=1, keepdim=True).clamp(min=1.0)
        h_g = (h_u * mask_f.unsqueeze(-1)).sum(dim=1) / denom
        h_p = self.poi_enc(torch.cat([poi_emb, poi_feat], dim=-1))

        cos_sim = (user_embs * poi_emb.unsqueeze(1)).sum(dim=-1)
        mean_cos = (cos_sim * mask_f).sum(dim=-1, keepdim=True) / denom
        return self.rho(torch.cat([h_g, h_p, mean_cos], dim=-1)).squeeze(-1)


class MoSANBaseline(nn.Module):
    """
    MoSAN (Tran et al., SIGIR 2019): Medley of Sub-Attention Networks.
    Each companion sub-network attends over peer companions to model group dominance
    and consensus voting, then aggregates contextual member-POI preference scores.
    """

    def __init__(
        self,
        emb_dim: int = 512,
        poi_feat_dim: int = 8,
        user_feat_dim: int = 3,
        hidden_dim: int = 64,
        num_sub_attns: int = 4,
        dropout: float = 0.25,
    ):
        super().__init__()
        self.num_sub = num_sub_attns
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
        )
        # Medley of sub-attention scoring heads over (ctx_u, member_v)
        self.sub_W = nn.Linear(hidden_dim * 2, num_sub_attns)
        self.sub_v = nn.Parameter(torch.randn(num_sub_attns) * 0.1)
        self.vote_head = nn.Sequential(
            nn.Linear(hidden_dim * 2 + 1, hidden_dim),
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
    ) -> torch.Tensor:
        B, M, _ = user_embs.shape
        h_u = self.user_proj(torch.cat([user_embs, user_feats], dim=-1))  # (B, M, H)
        h_p = self.poi_proj(torch.cat([poi_emb, poi_feat], dim=-1))       # (B, H)

        # Pairwise sub-attention across peers (B, M, M, H*2)
        hi = h_u.unsqueeze(2).expand(B, M, M, -1)
        hj = h_u.unsqueeze(1).expand(B, M, M, -1)
        sub_logits = torch.tanh(self.sub_W(torch.cat([hi, hj], dim=-1)))  # (B, M, M, K)
        pair_scores = (sub_logits * self.sub_v.view(1, 1, 1, -1)).mean(dim=-1)  # (B, M, M)

        key_mask = ~user_mask.unsqueeze(1).expand(B, M, M)
        pair_scores = pair_scores.masked_fill(key_mask, -1e9)
        beta = F.softmax(pair_scores, dim=-1) * user_mask.unsqueeze(1).float()
        beta = beta / beta.sum(dim=-1, keepdim=True).clamp(min=1e-6)

        ctx_u = torch.bmm(beta, h_u)  # (B, M, H)
        cos_u = (user_embs * poi_emb.unsqueeze(1)).sum(dim=-1, keepdim=True)
        hp_exp = h_p.unsqueeze(1).expand(B, M, -1)
        member_votes = self.vote_head(torch.cat([ctx_u * hp_exp, hp_exp, cos_u], dim=-1)).squeeze(-1)

        mask_f = user_mask.float()
        return (member_votes * mask_f).sum(dim=-1) / mask_f.sum(dim=-1).clamp(min=1.0)


class SetTransformerBaseline(nn.Module):
    """
    Set Transformer (Lee et al., ICML 2019): Self-Attention Block (SAB) across members +
    Pooling by Multihead Attention (PMA) with a learned seed vector S -> POI scoring.
    """

    def __init__(
        self,
        emb_dim: int = 512,
        poi_feat_dim: int = 8,
        user_feat_dim: int = 3,
        hidden_dim: int = 64,
        num_heads: int = 4,
        dropout: float = 0.25,
    ):
        super().__init__()
        self.user_proj = nn.Sequential(
            nn.Linear(emb_dim + user_feat_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.sab_attn = nn.MultiheadAttention(hidden_dim, num_heads, dropout=dropout, batch_first=True)
        self.sab_norm1 = nn.LayerNorm(hidden_dim)
        self.sab_ffn = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.GELU(),
            nn.Linear(hidden_dim * 2, hidden_dim),
        )
        self.sab_norm2 = nn.LayerNorm(hidden_dim)

        self.seed_vec = nn.Parameter(torch.randn(1, 1, hidden_dim) * 0.05)
        self.pma_attn = nn.MultiheadAttention(hidden_dim, num_heads, dropout=dropout, batch_first=True)
        self.pma_norm = nn.LayerNorm(hidden_dim)

        self.poi_proj = nn.Sequential(
            nn.Linear(emb_dim + poi_feat_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_dim * 3 + 1, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
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
    ) -> torch.Tensor:
        B, M, _ = user_embs.shape
        h_u = self.user_proj(torch.cat([user_embs, user_feats], dim=-1))
        pad_mask = ~user_mask

        sab_out, _ = self.sab_attn(h_u, h_u, h_u, key_padding_mask=pad_mask, need_weights=False)
        h_u = self.sab_norm1(h_u + sab_out)
        h_u = self.sab_norm2(h_u + self.sab_ffn(h_u))

        seed = self.seed_vec.expand(B, 1, -1)
        pma_out, _ = self.pma_attn(seed, h_u, h_u, key_padding_mask=pad_mask, need_weights=False)
        h_g = self.pma_norm((seed + pma_out).squeeze(1))

        h_p = self.poi_proj(torch.cat([poi_emb, poi_feat], dim=-1))
        mask_f = user_mask.float()
        mean_cos = ((user_embs * poi_emb.unsqueeze(1)).sum(dim=-1) * mask_f).sum(dim=-1, keepdim=True) / mask_f.sum(dim=-1, keepdim=True).clamp(min=1.0)
        return self.head(torch.cat([h_g * h_p, h_g, h_p, mean_cos], dim=-1)).squeeze(-1)


class GroupIMBaseline(nn.Module):
    """
    GroupIM (Sankar et al., SIGIR 2020): Mutual Information Maximizing Neural Group
    Recommendation with attentive member aggregation and bilinear InfoNCE user-group
    MI regularization during training.
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
        self.user_enc = nn.Sequential(
            nn.Linear(emb_dim + user_feat_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
        )
        self.attn_score = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1),
        )
        self.mi_bilinear = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.poi_enc = nn.Sequential(
            nn.Linear(emb_dim + poi_feat_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
        )
        self.scorer = nn.Sequential(
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
        return_mi_loss: bool = False,
    ):
        B, M, _ = user_embs.shape
        h_u = self.user_enc(torch.cat([user_embs, user_feats], dim=-1))  # (B, M, H)
        a_logits = self.attn_score(h_u).squeeze(-1).masked_fill(~user_mask, -1e9)
        alpha = F.softmax(a_logits, dim=-1) * user_mask.float()
        alpha = alpha / alpha.sum(dim=-1, keepdim=True).clamp(min=1e-6)

        h_g = (alpha.unsqueeze(-1) * h_u).sum(dim=1)  # (B, H)
        h_p = self.poi_enc(torch.cat([poi_emb, poi_feat], dim=-1))
        mask_f = user_mask.float()
        mean_cos = ((user_embs * poi_emb.unsqueeze(1)).sum(dim=-1) * mask_f).sum(dim=-1, keepdim=True) / mask_f.sum(dim=-1, keepdim=True).clamp(min=1.0)
        logit = self.scorer(torch.cat([h_g * h_p, h_g, h_p, mean_cos], dim=-1)).squeeze(-1)

        if not return_mi_loss:
            return logit

        # Mutual Information Maximization between group embedding h_g and member embeddings h_u vs shuffled peers
        proj_g = self.mi_bilinear(h_g)  # (B, H)
        pos_mi = (h_u * proj_g.unsqueeze(1)).sum(dim=-1)  # (B, M)
        perm_u = torch.roll(h_u, shifts=1, dims=0)
        neg_mi = (perm_u * proj_g.unsqueeze(1)).sum(dim=-1)  # (B, M)
        pos_bce = -F.logsigmoid(pos_mi) * mask_f
        neg_bce = -F.logsigmoid(-neg_mi) * mask_f
        mi_loss = (pos_bce + neg_bce).sum() / mask_f.sum().clamp(min=1.0)
        return logit, mi_loss


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
