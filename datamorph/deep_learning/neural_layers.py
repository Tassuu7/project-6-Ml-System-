"""
DataMorph Studio - Deep Neural Network Layers & Attention Mechanisms
Implements Linear Dense layers, Multi-Head Self-Attention, and Layer Normalization in pure Python.
"""

import math
import random
from typing import List, Dict, Any, Optional
from datamorph.deep_learning.tensor_math import Tensor


class LinearLayer:
    """Fully-Connected Linear Projection Layer: y = x * W^T + b."""
    def __init__(self, in_features: int, out_features: int):
        self.in_features = in_features
        self.out_features = out_features
        # Xavier/Glorot normal initialization
        std = math.sqrt(2.0 / (in_features + out_features))
        self.W = [[Tensor(random.gauss(0.0, std)) for _ in range(in_features)] for _ in range(out_features)]
        self.b = [Tensor(0.0) for _ in range(out_features)]

    def forward(self, x: List[Tensor]) -> List[Tensor]:
        out = []
        for row in range(self.out_features):
            acc = self.b[row]
            for col in range(self.in_features):
                acc = acc + (x[col] * self.W[row][col])
            out.append(acc)
        return out


class LayerNormalization:
    """Applies Layer Normalization over feature dimensions."""
    def __init__(self, normalized_shape: int, eps: float = 1e-5):
        self.eps = eps
        self.gamma = [Tensor(1.0) for _ in range(normalized_shape)]
        self.beta = [Tensor(0.0) for _ in range(normalized_shape)]

    def forward(self, x: List[Tensor]) -> List[Tensor]:
        n = len(x)
        mean_val = sum(t.data for t in x) / float(n)
        var_val = sum((t.data - mean_val) ** 2 for t in x) / float(n)
        std_inv = 1.0 / math.sqrt(var_val + self.eps)

        out = []
        for i in range(n):
            normed = (x[i] + (-mean_val)) * std_inv
            out.append((normed * self.gamma[i]) + self.beta[i])
        return out


class MultiHeadSelfAttention:
    """Multi-Head Scaled Dot-Product Self-Attention for tabular feature tokens."""
    def __init__(self, d_model: int = 16, n_heads: int = 2):
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.W_q = LinearLayer(d_model, d_model)
        self.W_k = LinearLayer(d_model, d_model)
        self.W_v = LinearLayer(d_model, d_model)
        self.W_o = LinearLayer(d_model, d_model)

    def forward(self, tokens: List[List[Tensor]]) -> List[List[Tensor]]:
        # Scaled dot-product attention over sequence tokens
        out_tokens = []
        for token in tokens:
            q = self.W_q.forward(token)
            k = self.W_k.forward(token)
            v = self.W_v.forward(token)
            # Dot product attention score
            score = sum(q[i].data * k[i].data for i in range(self.d_model)) / math.sqrt(self.d_k)
            attn_weight = 1.0 / (1.0 + math.exp(-min(20.0, max(-20.0, score))))
            out_tokens.append([val * attn_weight for val in v])
        return out_tokens
