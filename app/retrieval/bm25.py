import os
import re
import pickle
import string
import logging

from typing import List, Tuple, Optional

import numpy as np
from rank_bm25 import BM25Okapi


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


INDIC_PUNCTUATION = (
    string.punctuation +
    "।॥''\"“”‘’"
)

PUNCT_PATTERN = re.compile(
    "[" + re.escape(INDIC_PUNCTUATION) + "]"
)


def tokenize_hindi(text: str) -> List[str]:
    if not text:
        return []

    text = PUNCT_PATTERN.sub(
        " ",
        text.lower().strip()
    )

    return [
        token
        for token in text.split()
        if token
    ]


class BM25Retriever:
    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75
    ):
        self.k1 = k1
        self.b = b
        self.bm25: Optional[BM25Okapi] = None
        self.corpus_size = 0

    def tokenize(self, text: str) -> List[str]:
        return tokenize_hindi(text)

    def build(self, documents: List[str]) -> None:
        self.corpus_size = len(documents)

        logger.info(
            f"Building BM25 index for {self.corpus_size} documents..."
        )

        tokenized_corpus = [
            self.tokenize(doc)
            for doc in documents
        ]

        self.bm25 = BM25Okapi(
            tokenized_corpus,
            k1=self.k1,
            b=self.b
        )

        logger.info(
            "BM25 index built successfully."
        )

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:

        if self.bm25 is None or self.corpus_size == 0:
            raise ValueError(
                "BM25 index is not populated or loaded."
            )

        tokens = self.tokenize(query)

        if not tokens:
            return (
                np.zeros((1, 0), dtype=np.float32),
                np.zeros((1, 0), dtype=np.int64)
            )

        scores = self.bm25.get_scores(
            tokens
        ).astype(np.float32)

        top_k = min(
            top_k,
            self.corpus_size
        )

        indices = np.argsort(scores)[::-1][:top_k]
        top_scores = scores[indices]

        return (
            top_scores.reshape(1, -1),
            indices.reshape(1, -1)
        )

    def save(self, file_path: str) -> None:
        if self.bm25 is None:
            raise ValueError(
                "Cannot save uninitialized BM25 index."
            )

        directory = os.path.dirname(
            os.path.abspath(file_path)
        )

        os.makedirs(
            directory,
            exist_ok=True
        )

        data = {
            "bm25": self.bm25,
            "k1": self.k1,
            "b": self.b,
            "corpus_size": self.corpus_size
        }

        with open(
            file_path,
            "wb"
        ) as file:
            pickle.dump(
                data,
                file,
                protocol=pickle.HIGHEST_PROTOCOL
            )

        logger.info(
            f"Saved BM25 index to {file_path}"
        )

    def load(self, file_path: str) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"BM25 index file not found at: {file_path}"
            )

        with open(
            file_path,
            "rb"
        ) as file:
            data = pickle.load(file)

        self.bm25 = data["bm25"]
        self.k1 = data["k1"]
        self.b = data["b"]
        self.corpus_size = data["corpus_size"]

        logger.info(
            f"Loaded BM25 index from {file_path}"
        )