import numpy as np
from sentence_transformers import SentenceTransformer


class MultilingualE5Embedder:
    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-small"
    ):
        self.model_name = model_name

        self.device = "cpu"

        self.model = SentenceTransformer(
            self.model_name,
            device=self.device
        )

    def embed_documents(self, texts):
        if not texts:
            return np.empty(
                (0, 384),
                dtype=np.float32
            )

        inputs = [
            f"passage: {text}"
            for text in texts
        ]

        embeddings = self.model.encode(
            inputs,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return embeddings.astype(
            np.float32
        )

    def embed_query(self, query: str):
        text = f"query: {query}"

        embedding = self.model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return embedding[0].astype(
            np.float32
        )