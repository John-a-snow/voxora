import os
import sys
import time
import argparse
import logging 
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.apppend(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.ingestion.models import Document

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s - &(message)=s"

    DEFAULT_INPUT_PATH = "/home"`
    DEFAULT_OUTPUT_PATH = os.path.join(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "processed",
        "dev_corpus.parquet"
)
def get_process_memory_mb() -> float:
     try:
        import psutil
        return psutil.Process.memory


