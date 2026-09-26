import os
import sys
import logging

import numpy as np
import pyarrow.parquet as pq

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)

from app.embeddings.model import MultilingualE5Embedder
from app.retrieval.faiss_index import FaissVectorIndex


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "dev_corpus.parquet"
)

INDEX_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "indexes",
    "dev.faiss"
)


def load_documents():
    logger.info("Loading corpus...")

    table = pq.read_table(DATA_PATH)

    documents = table.to_pylist()

    logger.info(
        f"Loaded {len(documents)} documents."
    )

    return documents


def build_index(documents, batch_size=16):
    logger.info("Loading ONNX embedder...")

    embedder = MultilingualE5Embedder()

    faiss_index = None

    total = len(documents)

    for start in range(0, total, batch_size):
        end = min(
            start + batch_size,
            total
        )

        batch = documents[start:end]

        texts = [
            str(doc.get("text", ""))
            for doc in batch
        ]

        logger.info(
            f"Embedding documents {start + 1}-{end} "
            f"of {total}"
        )

        embeddings = embedder.embed_documents(
            texts,
            batch_size=batch_size
        )

        if faiss_index is None:
            faiss_index = FaissVectorIndex(
                dimension=embeddings.shape[1]
            )

            faiss_index.build(
                embeddings
            )
        else:
            faiss_index.index.add(
                embeddings
            )

    if faiss_index is None:
        raise ValueError(
            "No documents were available."
        )

    return faiss_index


def main():
    documents = load_documents()

    faiss_index = build_index(
        documents,
        batch_size=16
    )

    os.makedirs(
        os.path.dirname(INDEX_PATH),
        exist_ok=True
    )

    faiss_index.save(
        INDEX_PATH
    )

    logger.info(
        f"FAISS index saved to: {INDEX_PATH}"
    )

    logger.info(
        f"Total vectors: {faiss_index.size()}"
    )

    logger.info(
        f"Embedding dimension: "
        f"{faiss_index.dimension()}"
    )


if __name__ == "__main__":
    main()