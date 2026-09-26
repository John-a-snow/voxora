import gc
import logging
import time
from typing import List, Optional

import numpy as np


logger = logging.getLogger(__name__)


class MultilingualE5Embedder:
    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-small",
        device: Optional[str] = None,
        normalize_embeddings: bool = True
    ):
        self.model_name = model_name
        self.normalize_embeddings = normalize_embeddings

        import torch

        torch.set_num_threads(1)

        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass

        if device is None:
            self.device = (
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )
        else:
            self.device = device

        logger.info(
            f"Loading {self.model_name} on {self.device}"
        )

        start_time = time.time()

        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(
            self.model_name,
            device=self.device
        )

        self.model.eval()

        self.load_time_s = round(
            time.time() - start_time,
            3
        )

        if hasattr(
            self.model,
            "get_embedding_dimension"
        ):
            self.embedding_dim = (
                self.model.get_embedding_dimension()
            )
        else:
            self.embedding_dim = (
                self.model.get_sentence_embedding_dimension()
            )

        gc.collect()

        logger.info(
            f"Embedder ready in {self.load_time_s}s "
            f"(dimension: {self.embedding_dim})"
        )

    def embed_documents(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:

        if not texts:
            return np.empty(
                (0, self.embedding_dim),
                dtype=np.float32
            )

        import torch

        passages = [
            f"passage: {text}"
            for text in texts
        ]

        with torch.inference_mode():
            embeddings = self.model.encode(
                passages,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                normalize_embeddings=self.normalize_embeddings,
                convert_to_numpy=True
            )

        return embeddings.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:

        import torch

        query = f"query: {query}"

        with torch.inference_mode():
            embedding = self.model.encode(
                query,
                normalize_embeddings=self.normalize_embeddings,
                convert_to_numpy=True
            )

        return embedding.astype(
            np.float32
        ).flatten()

    def get_embedding_dimension(self) -> int:
        return self.embedding_dim