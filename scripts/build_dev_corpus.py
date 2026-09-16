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

def clean_text(raw_text: str) -> str:
    if not raw_text:
        return ""
    text = str(raw_text).replace("\r\n", "\n").replace("\r", "\n")
    return " " .join(text.split())

def build_dev_corpus(input_path: str, output_path: str, max_records: int = 100)
    mem_before = get_process_memory_mb()
    t0 = time.time()

    logger.info(f"Memory before reading: {mem_before:.2f} MB"}
    logger.info(f"Input source Parquet file: {input_path}")

    if not os.path.exists(input_path):
        logger.error(f"Local source Parquet file not found at: {input_path}")
        print("\nERROR: No Local MSMARCO-XI Parquet artifact is available.\n")
        sys.exit(1)

    source_file_size = os.path.getsize(input_path)
    logger.info(f"Source file size: {source_file_size / (1024**3):.2f}GB ({source_file_size:,} bytes)")

    pf = pq.ParquetFile(input_path)

    source_records_inspected = 0
    total_passages_encountered = 0
    empty_passages_skipped = 0 
    documents: list[dict] = []

    for batch in pf.iter_batches(batch_size=max_records)
        batch_records = batch.to_pylist()

        for record_idx, r in enumerate(batch_records):







            

                


