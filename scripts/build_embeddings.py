import os
import sys
import time
import json
import argparse
import logging
from datetime import datetime

import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.embeddings.model import MultilingualE5Embedder
from app.embeddings.batcher import batch_encode_documents


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_INPUT_PATH = os.path.join(ROOT_DIR, "data", "processed", "dev_corpus.parquet")
DEFAULT_OUTPUT_PATH = os.path.join(ROOT_DIR, "data", "processed", "dev_embeddings.npy")
DEFAULT_META_PATH = os.path.join(ROOT_DIR, "data", "processed", "embedding_metadata.json")


def get_memory_mb():
    try:
        import psutil
        return psutil.Process().memory_info().rss / (1024 * 1024)
    except Exception:
        pass

    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return float(line.split()[1]) / 1024
    except Exception:
        pass

    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--metadata", default=DEFAULT_META_PATH)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument(
        "--model-name",
        default="intfloat/multilingual-e5-small"
    )

    args = parser.parse_args()

    memory_before = get_memory_mb()
    logger.info(f"Memory before reading corpus: {memory_before:.2f} MB")

    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)

    start = time.time()

    table = pq.read_table(args.input, columns=["document_id", "text"])
    texts = table["text"].to_pylist()
    doc_ids = table["document_id"].to_pylist()

    read_time = round((time.time() - start) * 1000, 2)
    logger.info(f"Loaded {len(texts)} documents in {read_time} ms")

    start = time.time()

    embedder = MultilingualE5Embedder(model_name=args.model_name)

    model_time = round((time.time() - start) * 1000, 2)
    memory_after_model = get_memory_mb()

    logger.info(f"Memory after model load: {memory_after_model:.2f} MB")

    start = time.time()

    embeddings = batch_encode_documents(
        embedder,
        texts,
        batch_size=args.batch_size,
        show_progress=False
    )

    embedding_time = round((time.time() - start) * 1000, 2)
    memory_after_embedding = get_memory_mb()

    if len(doc_ids) != embeddings.shape[0]:
        logger.error(
            f"Document count ({len(doc_ids)}) does not match "
            f"embedding count ({embeddings.shape[0]})"
        )
        sys.exit(1)

    finite = bool(np.isfinite(embeddings).all())
    dimension = embeddings.shape[1]

    norms = np.linalg.norm(embeddings, axis=1)
    average_norm = float(np.mean(norms))
    normalized = bool(np.allclose(norms, 1.0, atol=1e-3))

    output_dir = os.path.dirname(args.output)
    os.makedirs(output_dir, exist_ok=True)

    np.save(args.output, embeddings)

    file_size = os.path.getsize(args.output)

    metadata = {
        "model_name": embedder.model_name,
        "embedding_dimension": int(dimension),
        "document_count": int(len(texts)),
        "normalized": True,
        "device": embedder.device,
        "batch_size": int(args.batch_size),
        "creation_timestamp": datetime.now().isoformat(),
        "input_corpus": args.input,
        "output_embedding_file": args.output,
        "file_size_bytes": file_size,
        "memory_metrics": {
            "memory_before_mb": round(memory_before, 2),
            "memory_after_model_load_mb": round(memory_after_model, 2),
            "memory_after_embedding_mb": round(memory_after_embedding, 2),
            "memory_delta_mb": round(memory_after_embedding - memory_before, 2)
        },
        "timing_metrics": {
            "model_load_time_ms": model_time,
            "embedding_time_ms": embedding_time,
            "total_time_ms": round(model_time + embedding_time, 2)
        }
    }

    with open(args.metadata, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    saved_embeddings = np.load(args.output)

    logger.info(f"Embeddings saved to: {args.output}")
    logger.info(f"Shape: {saved_embeddings.shape}")
    logger.info(f"Data type: {saved_embeddings.dtype}")
    logger.info(f"Finite values: {finite}")
    logger.info(f"Average norm: {average_norm:.6f}")
    logger.info(f"Normalized: {normalized}")
    logger.info(f"Embedding time: {embedding_time} ms")
    logger.info(f"File size: {file_size / 1024:.2f} KB")


if __name__ == "__main__":
    main()