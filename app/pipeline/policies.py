from dataclasses import dataclass


@dataclass
class RetrievalPolicy:
    dense_top_k: int = 20
    final_top_k: int = 5
    fallback_enabled: bool = True
    fallback_top_k: int = 5
    min_dense_score: float = 0.30


DEFAULT_RETRIEVAL_POLICY = RetrievalPolicy()