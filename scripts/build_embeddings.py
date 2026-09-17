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
        "--"


