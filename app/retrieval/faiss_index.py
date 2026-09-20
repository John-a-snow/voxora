import os
import logging
from typing import Tuple, Optional

import numpy as np
import faiss


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class FaissVectorIndex:
    def __init__(self, dimension: Optional[int] = None):
        self.dim = dimension
        self.index = None

        if dimension is not None:
            self.index = faiss.IndexFlatIP(dimension)

    def _validate_embeddings(self, embeddings: np.ndarray):
        if not isinstance(embeddings, np.ndarray):
            raise TypeError("Embeddings must be a numpy.ndarray.")

        if embeddings.ndim != 2:
            raise ValueError(
                f"Embeddings must be 2-dimensional (got shape {embeddings.shape})."
            )

        if embeddings.dtype != np.float32:
            raise ValueError(
                f"Embeddings dtype must be float32 (got {embeddings.dtype})."
            )

        if not np.isfinite(embeddings).all():
            raise ValueError("Embeddings contain NaN or Inf values.")

    def build(self, embeddings: np.ndarray):
        self._validate_embeddings(embeddings)

        count, dimension = embeddings.shape

        if self.dim is not None and self.dim != dimension:
            raise ValueError(
                f"Embedding dimension {dimension} does not match index dimension {self.dim}."
            )

        self.dim = dimension
        self.index = faiss.IndexFlatIP(self.dim)

        logger.info(f"Adding {count} vectors to FAISS index")
        self.index.add(embeddings)

        logger.info(f"FAISS index built with {self.index.ntotal} vectors")

    def save(self, file_path: str):
        if self.index is None or self.index.ntotal == 0:
            raise ValueError("Cannot save an empty FAISS index.")

        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        faiss.write_index(self.index, file_path)

        logger.info(f"FAISS index saved to {file_path}")

    def load(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"FAISS index file not found at: {file_path}"
            )

        self.index = faiss.read_index(file_path)
        self.dim = self.index.d

        logger.info(
            f"FAISS index loaded. Vectors: {self.index.ntotal}, "
            f"Dimension: {self.dim}"
        )

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:

        if self.index is None or self.index.ntotal == 0:
            raise ValueError("FAISS index is not ready.")

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        if query_vector.ndim != 2 or query_vector.shape[0] != 1:
            raise ValueError(
                f"Query vector must have shape (1, dim), got {query_vector.shape}."
            )

        if query_vector.dtype != np.float32:
            query_vector = query_vector.astype(np.float32)

        if query_vector.shape[1] != self.dim:
            raise ValueError(
                f"Query vector dimension {query_vector.shape[1]} "
                f"does not match index dimension {self.dim}."
            )

        if not np.isfinite(query_vector).all():
            raise ValueError("Query vector contains NaN or Inf values.")

        top_k = min(top_k, self.index.ntotal)

        scores, indices = self.index.search(query_vector, top_k)

        return scores, indices

    def size(self) -> int:
        if self.index is None:
            return 0

        return self.index.ntotal

    def dimension(self) -> int:
        if self.dim is None:
            return 0

        return self.dim