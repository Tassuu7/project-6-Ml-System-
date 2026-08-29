"""
DataMorph Studio - Network PageRank Centrality Feature Extractor
Computes power-iteration stationary Markov chain transition PageRank scores for entity graphs.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class PageRankCentralityExtractor(BaseTransformer):
    def __init__(self, source_col: str, target_col: str, damping: float = 0.85,
                 max_iter: int = 30, name: str = "PageRankCentralityExtractor"):
        super().__init__(columns=[source_col, target_col], name=name)
        self.source_col = source_col
        self.target_col = target_col
        self.damping = damping
        self.max_iter = max_iter
        self.pagerank_scores_: Dict[str, float] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "PageRankCentralityExtractor":
        src_vals = [str(x) for x in df[self.source_col].to_list()]
        dst_vals = [str(x) for x in df[self.target_col].to_list()]

        all_nodes = list(set(src_vals + dst_vals))
        n = len(all_nodes) or 1
        adj: Dict[str, List[str]] = {node: [] for node in all_nodes}
        out_deg: Dict[str, int] = {node: 0 for node in all_nodes}

        for s, d in zip(src_vals, dst_vals):
            adj[s].append(d)
            out_deg[s] += 1

        # Power iteration
        scores = {node: 1.0 / n for node in all_nodes}
        teleport = (1.0 - self.damping) / n

        for _ in range(self.max_iter):
            new_scores = {node: teleport for node in all_nodes}
            for u in all_nodes:
                if out_deg[u] > 0:
                    share = self.damping * scores[u] / out_deg[u]
                    for v in adj[u]:
                        new_scores[v] += share
                else:
                    for v in all_nodes:
                        new_scores[v] += self.damping * scores[u] / n
            scores = new_scores

        self.pagerank_scores_ = {node: round(s, 6) for node, s in scores.items()}
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        result = df.copy()
        src_scores = [self.pagerank_scores_.get(str(x), 0.0) for x in df[self.source_col].to_list()]
        dst_scores = [self.pagerank_scores_.get(str(x), 0.0) for x in df[self.target_col].to_list()]

        result.add_column(f"{self.source_col}_pagerank", src_scores)
        result.add_column(f"{self.target_col}_pagerank", dst_scores)
        return result
