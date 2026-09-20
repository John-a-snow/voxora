import os
import sys
import time
import json
import argparse
import logging
from datetime import datetime

import pyarrow.parquet as pq

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.retrieval.bm25 import BM25Retriever

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_INPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "dev_corpus.parquet"
)

DEFAULT_OUTPUT_INDEX_PATH = os.path.join(
    BASE_DIR,
    "data",
    "indexes",
    "dev_bm25.pkl"
)

DEFAULT_METADATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "indexes",
    "dev_bm25_metadata.json"
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
    return float(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    ) / 1024.0


def main():
    parser = argparse.ArgumentParser(
        description="BM25 Lexical Index Builder"
    )

    parser.add_argument(
        "--input",
        type=str,
        default=DEFAULT_INPUT_PATH,
        help="Input corpus Parquet path"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_INDEX_PATH,
        help="Output BM25 index path"
    )

    parser.add_argument(
        "--metadata",
        type=str,
        default=DEFAULT_METADATA_PATH,
        help="Output metadata JSON path"
    )

    parser.add_argument(
        "--k1",
        type=float,
        default=1.5,
        help="BM25 k1 parameter"
    )

    parser.add_argument(
        "--b",
        type=float,
        default=0.75,
        help="BM25 b parameter"
    )

    args = parser.parse_args()

    mem_before = get_process_memory_mb()

    logger.info(
        f"Memory before BM25 build: "
        f"{mem_before:.2f} MB"
    )

    if not os.path.exists(args.input):
        logger.error(
            f"Input corpus file not found at: "
            f"{args.input}"
        )
        sys.exit(1)

    t0 = time.time()

    table = pq.read_table(
        args.input,
        columns=["text"]
    )

    documents = table["text"].to_pylist()
    doc_count = len(documents)

    logger.info(
        f"Loaded {doc_count} passages "
        f"from {args.input}"
    )

    retriever = BM25Retriever(
        k1=args.k1,
        b=args.b
    )

    retriever.build(
        documents
    )

    build_time = round(
        time.time() - t0,
        4
    )

    mem_after = get_process_memory_mb()

    mem_delta = round(
        mem_after - mem_before,
        2
    )

    retriever.save(
        args.output
    )

    index_file_size = os.path.getsize(
        args.output
    )

    metadata = {
        "algorithm": "BM25Okapi",
        "corpus_count": int(doc_count),
        "k1": float(args.k1),
        "b": float(args.b),
        "source_corpus": args.input,
        "creation_timestamp": datetime.now().isoformat(),
        "file_size_bytes": index_file_size,
        "memory_metrics": {
            "memory_before_mb": round(
                mem_before,
                2
            ),
            "memory_after_mb": round(
                mem_after,
                2
            ),
            "memory_delta_mb": mem_delta
        },
        "build_time_s": build_time
    }

    os.makedirs(
        os.path.dirname(args.metadata),
        exist_ok=True
    )

    with open(
        args.metadata,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            metadata,
            f,
            indent=2
        )

    val_retriever = BM25Retriever()

    val_retriever.load(
        args.output
    )

    val_count = val_retriever.corpus_size

    print("\nBM25 index build complete.")
    print(f"Source corpus: {args.input}")
    print(f"Documents: {doc_count}")
    print(
        f"BM25 settings: k1={args.k1}, "
        f"b={args.b}"
    )
    print(f"Output: {args.output}")
    print(
        f"Output size: {index_file_size / 1024:.2f} KB "
        f"({index_file_size:,} bytes)"
    )
    print(f"Metadata: {args.metadata}")
    print(
        f"Corpus count check: "
        f"{doc_count} == {val_count}"
    )
    print(f"Build time: {build_time} s")
    print(
        f"Memory before: "
        f"{mem_before:.2f} MB"
    )
    print(
        f"Memory after: "
        f"{mem_after:.2f} MB"
    )
    print(
        f"Memory change: "
        f"{mem_delta:.2f} MB"
    )


if __name__ == "__main__":
    main()