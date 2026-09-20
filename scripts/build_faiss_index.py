import os
import sys
import time
import json
import argparse
import logging
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieval.faiss_index import FaissVectorIndex


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_EMBEDDINGS_PATH = os.path.join(
    ROOT_DIR, "data", "processed", "dev_embeddings.npy"
)

DEFAULT_OUTPUT_INDEX_PATH = os.path.join(
    ROOT_DIR, "data", "indexes", "dev.faiss"
)

DEFAULT_METADATA_PATH = os.path.join(
    ROOT_DIR, "data", "indexes", "dev_index_metadata.json"
)


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

    parser.add_argument(
        "--embeddings",
        default=DEFAULT_EMBEDDINGS_PATH
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_INDEX_PATH
    )

    parser.add_argument(
        "--metadata",
        default=DEFAULT_METADATA_PATH
    )

    parser.add_argument(
        "--model-name",
        default="intfloat/multilingual-e5-small"
    )

    args = parser.parse_args()

    memory_before = get_memory_mb()
    logger.info(f"Memory before index build: {memory_before:.2f} MB")

    if not os.path.exists(args.embeddings):
        logger.error(f"Embeddings file not found: {args.embeddings}")
        sys.exit(1)

    start = time.time()

    embeddings = np.load(args.embeddings)

    logger.info(
        f"Loaded embeddings: shape={embeddings.shape}, "
        f"dtype={embeddings.dtype}"
    )

    if embeddings.ndim != 2:
        logger.error(f"Embeddings must be 2D, got {embeddings.shape}")
        sys.exit(1)

    if embeddings.dtype != np.float32:
        embeddings = embeddings.astype(np.float32)

    if not np.isfinite(embeddings).all():
        logger.error("Embeddings contain NaN or Inf values")
        sys.exit(1)

    vector_count, dimension = embeddings.shape

    index = FaissVectorIndex(dimension=dimension)
    index.build(embeddings)

    build_time = round(time.time() - start, 4)
    memory_after = get_memory_mb()

    index.save(args.output)

    index_size = os.path.getsize(args.output)

    metadata = {
        "index_type": "IndexFlatIP",
        "metric": "inner_product",
        "dimension": int(dimension),
        "vector_count": int(vector_count),
        "embedding_model": args.model_name,
        "normalized": True,
        "source_embedding_file": args.embeddings,
        "creation_time": datetime.now().isoformat(),
        "file_size_bytes": index_size,
        "memory_metrics": {
            "memory_before_mb": round(memory_before, 2),
            "memory_after_mb": round(memory_after, 2),
            "memory_delta_mb": round(memory_after - memory_before, 2)
        },
        "build_time_s": build_time
    }

    os.makedirs(os.path.dirname(args.metadata), exist_ok=True)

    with open(args.metadata, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    loaded_index = FaissVectorIndex()
    loaded_index.load(args.output)

    logger.info(f"FAISS index saved to: {args.output}")
    logger.info(f"Vectors: {loaded_index.size()}")
    logger.info(f"Dimension: {loaded_index.dimension()}")
    logger.info(f"Build time: {build_time} seconds")
    logger.info(f"Index size: {index_size / 1024:.2f} KB")


if __name__ == "__main__":
    main()