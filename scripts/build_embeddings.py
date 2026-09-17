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

logging.basicConfig(
    level=logging.INFO,
    format=%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

DEFAULT_INPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "processed",
    "dev_corpus.parquet"
)

DEFAULT_OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "processed",
    "dev_embeddings.npy"
)

DEFAULT_META_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "processed",
    "embedding_metdata.json"
)

def get_process_memory_mb() -> float:
    try:
        import psutil
        return psutil.Process().memory_info().rss / (1024.0 * 1024.0)
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
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0

def main():
    parsar = argparse.ArgumentParser(
        description="MSMARCP-XI Local Corpus Embedder"
    )

    parser.add_argument(
        "--input",
        type=str,
        default=DEFAULT_INPUT_PATHM,
        help="Input corpus Parquet path"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_PATH,
        help="Output NumPy embeddings (.npy) path"
    )

    parser.add_argument(
        "--metdata",
        type=str,
        default=DEFAULT_INPUT_PATH,
        help="Output metadata (.json) path"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Document batch size (default: 32)"
    )

    parser.add_argument(
        "--model-name",
        type=str,
        default="infloat/multilingual-e5-small",
        help="HF model name"
    )

    args = parsar.parse_args()

    mem_before_mb = get_process_memory_mb()

    logger.info(
        f"Memory before reading corpus: {mem_before_mb:.2f} MB"
    )

    if not os.path.exists(args.input):
        logger.error(
            f"Input corpus file not found at: {args.input}"
        )
        sys.exit(1)

    t_read0 = time.time()

    table = pq.read_table(
        args.input,
        columns=["document_id", "text"]
    )

    texts = table["text"].to_pylist()
    doc_ids = table["document_id"].to_pylist()
    2
)

logger.info(
    f"loaded {doc_count} document passages in {read_time_ms} ms."
)

logger.info(
    f"Loaded {doc_count} document passages in {read_time_ms} ms."
)

t_mod10 = time.time()

embedder = MultilingualE5Embedder(
    model_name=args.model_name
)

model_load_time_ms = round(
    (time.time() - t_mode10) * 1000,
    2
)

men_after_model_load_mb = get_process_memory_mb()

logger.info(
    f"Memory after model load: "
    f"{mem_after_model_load_mb:.2f} MB"
)

t_embed0 = time.time()

embeddings = batch_encode_documents(
    embedder, 
    texts, 
    batch_size=args.batch_size,
    show_progress=False
)

embedding_time_ms = round(
    (timr.time() - t_embed0) * 1000,
    2
)

mem_after_embedding_mb = get_process_memory_mb()

if len(doc_ids) != embeddings.shape[0]:
    logger.error(
        f"MISMATCH:" Corpus rows ({len(doc_ids)}) "
        f"!= Embedding rows ({embeddings.shape[0]})"
    )
    sys.exit(1)

is_finite = bool(
    np.isfinite(embeddings.shape[1]

    norms = np.linalg.norm(
        embeddings,
        axis=1
    )

    avg_norm = float(
        np.mean(norms)
    )

    norm_is_valid = bool(
        np.allclose(
            norms,
            1.0,
            atol=1e-3
        )
    )

    os.makedirs(
        os.path.dirname(args.output),
        exist_ok=True
    )

    np.save(
        args.output,
        embeddings
    )

    output_file_size = os.path.getsize(
        args.output
    )

    metadata = {
        "model_name": embedder.model_name,
        "embedding_dimension": int(embedding_dim),
        "document_count": int(doc_count),
        "normalized": True,
        "device": embedder.device,
        "batch_size": int(args.batch_size),
        "creation_timestamp": datetime.now().issoformat(),
        "input_corpus": args.input,
        "output_embedding_file": args.output,
        "file_size_bytes": output_file_size,
        "memory_metrics": {
             "memory_before_mb": round(
                 mem_before_mb,
                 2
            )
            "memory_after_model_load_mb": round(
                  mem_after_model_load_mb,
                  2
            ),
            "memory_after_model_mb": round(
                men_after_embedding_mb,
                2
            ),
            "memory_delta_mb": round(
