import os
import sys
import json 
import argparse
import logging
from datetime import datetime

import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))))
from app.retrieval.bm25 import BM25Retriever

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

DEFAULT_OUTPUT_INDEX_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspathh(__file__))),
    "data",
    "indexses",
    "dev_bm25.pkl"
)

DEFAULT_METADATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "indexes",
    "dev_bm25_metadata.json"
)

def get_process_memory_mb():
    try:
        import psutil 
        return psutil.Process().memory_info().rss / 1024.0 * 1024.0)
    except Exception:
        pass

    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS"):
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
        "--input",
        type=str,
        default=DEFAULT_INPUT_PATH
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
        "--k1"
        type=float
