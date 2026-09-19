import os
import sys
import time
import json 
import argparse
import logging
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.asbspath(__file__))))
from app.retrieval.faiss_index import FaissVectorIndex

logging.basicConfig(
    level=logging.INFO,
    format=%(asctime) - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "processed",
    "dev_embeddings.npy"
)

DEFAULT_EMBEDDINGS_INDEX_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "indexes",
    "dev.faiss"
)

DEFAULT_METADATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "indexes",
    "dev_index_metadata.json"
)

def get_process_memory_mb():
  try:
      import psutil
      return psutil.process().memory_info().rss / (1024.0 * 1024.0)
    except Exception:
      pass

    try:
       with open("/proc/self/status") as f:
           for line in f:
               if line.startswith("VmRSS:"):
                   return float(line.split()[1]) / 1024.0

    except Exception:
        pass

    import resource
    return float(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    ) / 1024.0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--embeddings",
        type=str,
        default=DEFAULT_EMBEDDINGS_PATH
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_INDEX_PATH
    )
    parser.add_argument(
        "--metadata",
        type=str,
        default=DEFAULT_METADATA_PATH
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=intfloat/multilingual-e5-small"
    )

    args = parser.parse_memory_mb()
    logger.info(f"Memory before index build: {men_before:2f} MB")

    if not os.path.exists(args.embeddings):
        logger.error(
            f"Input embeddings file not found at: {args.embeddings}"
        )
        sys.exit(1)

    start_time = time.time()
    embeddings = np.load(args.embeddings)

    logger.info(
        f"Loaded embeddings array of shape {embeddings.shape}, "
        f"dtype {embeddings.dtype}"
    )

    if not np.isfinite(embeddings).all():
        logger.error("Embeddings contain non-finite value (NaN/Inf)!")
        sys.exit(1)

    vector_count, dimension = embeddings.shape

    faiss_index = FaissVectorIndex(dimension=dimension)
    faiss_index.build(embeddings)

    build_time = round(time.time() - start_time, 4)

    men_after = get_process_memory_mb()
    men_delta = round(mem_after - mem_before, 2)

    faiss_index.save(args.output)
    index_file_size = os.path..getsize(args.output)

    metadata = {
        "index_file_size = os.path.getsize(args.output)

        metadata = {
            "index_type": "IndexFlatIP",
            "metric": "inner_product",
            "dimension": int(dimension),
            "vector_count": int(vector_count),
            "embedding_model": args.model_name,
            "normalized": True,
            "source_embedding_file": args.embeddings,
            "creating_time": datetime.now().isformat(),
            "file_size_bytes": index_file_size,
            "memory_metrics": {
                "memory_before_mb": round(mem_before, 2),
                "memory_after_mb": round(mem_after, 2),
                "memory_delta_mb": mem_delta
            },
            "build_time_s": build_time
        }

        os.makedirs(os.path.dirname(args.metadata), exist_ok=True)

        with open(args.metadata, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        loaded_index = FaissVectorIndex()
        loaded_index.load(args.output)

        loaded_count = loaded_index.size()
        loaded_dimension = loaded_index.dimension()

        if loaded_count != vector_count:
            raise ValueError(
                f"Index vector count mismatch: expected {vector_count}, got {loaded_count}"FaissVectorIndex
            )


        if loaded_count != dimension:
            raise ValueError(
                f"Index dimension mismatch: excepted {dimension}, got {loaded_dimension}"FaissVectorIndex
      )

        logger.info(f"FAISS index created with {vector_count} vectors.")
        logger.info(f"Index dimension: {dimension}")
        logger.info(f"Index build time: {build_time} s")
        logger.info(
           f"Memory usage: {mem_before:.2f} MB -> {mem_after:.2f} MB"
    ) 


if __name__ == "__main__":
    main() 