import os
import sys
import time
import argparse
import logging
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.ingestion.models import Document

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_INPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "hintrain.parquet"
)

DEFAULT_OUTPUT_PATH = os.path.join(
    BASE_DIR,
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
    return float(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    ) / 1024.0


def clean_text(raw_text: str) -> str:
    if not raw_text:
        return ""

    text = str(raw_text).replace("\r\n", "\n").replace("\r", "\n")
    return " ".join(text.split())


def build_dev_corpus(
    input_path: str,
    output_path: str,
    max_records: int = 100
) -> None:
    mem_before = get_process_memory_mb()
    t0 = time.time()

    logger.info(f"Memory before reading: {mem_before:.2f} MB")
    logger.info(f"Input source Parquet path: {input_path}")

    if not os.path.exists(input_path):
        logger.error(f"Local source Parquet file not found at: {input_path}")
        print("\nERROR: No local MSMARCO-XI Parquet artifact is available.\n")
        sys.exit(1)

    source_file_size = os.path.getsize(input_path)

    logger.info(
        f"Source file size: {source_file_size / (1024 ** 3):.2f} GB "
        f"({source_file_size:,} bytes)"
    )

    pf = pq.ParquetFile(input_path)

    source_records_inspected = 0
    total_passages_encountered = 0
    empty_passages_skipped = 0
    documents = []

    for batch in pf.iter_batches(batch_size=max_records):
        batch_records = batch.to_pylist()

        for r in batch_records:
            if source_records_inspected >= max_records:
                break

            source_records_inspected += 1

            query_id = r.get("query_id")
            if query_id is None:
                query_id = source_records_inspected

            target_lang = r.get("target_lang", "hi")
            source_lang = r.get("source_lang", "en")
            query_text = clean_text(r.get("query", ""))
            query_type = r.get("query_type", "")

            passages_dict = r.get("passages", {})

            if not isinstance(passages_dict, dict):
                continue

            trans_passages = passages_dict.get(
                "Translated_passages",
                []
            )
            eng_passages = passages_dict.get(
                "English_passages",
                []
            )
            is_selected = passages_dict.get(
                "is_selected",
                []
            )

            total_passages_encountered += len(trans_passages)

            for p_idx, raw_p_text in enumerate(trans_passages):
                cleaned_p_text = clean_text(raw_p_text)

                if not cleaned_p_text:
                    empty_passages_skipped += 1
                    continue

                eng_p_text = (
                    clean_text(eng_passages[p_idx])
                    if p_idx < len(eng_passages)
                    else ""
                )

                sel_flag = (
                    int(is_selected[p_idx])
                    if p_idx < len(is_selected)
                    else 0
                )

                doc_id = f"{query_id}_{p_idx}"

                doc = Document(
                    document_id=doc_id,
                    text=cleaned_p_text,
                    language=str(target_lang or "hi"),
                    query_id=int(query_id),
                    passage_index=int(p_idx),
                    is_selected=int(sel_flag),
                    source="ai4bharat/MSMARCO-XI",
                    english_text=eng_p_text,
                    query=query_text,
                    query_type=str(query_type or ""),
                    source_lang=str(source_lang or "en"),
                    target_lang=str(target_lang or "hi")
                )

                documents.append(doc.to_dict())

        if source_records_inspected >= max_records:
            break

    processing_time = round(time.time() - t0, 3)
    mem_after = get_process_memory_mb()
    mem_delta = round(mem_after - mem_before, 2)

    logger.info(
        f"Extracted {len(documents)} document passages from "
        f"{source_records_inspected} source records in "
        f"{processing_time}s."
    )

    selected_docs = sum(
        1 for d in documents
        if d["is_selected"] == 1
    )

    unselected_docs = sum(
        1 for d in documents
        if d["is_selected"] == 0
    )

    doc_ids = [d["document_id"] for d in documents]
    text_values = [d["text"] for d in documents]

    duplicate_ids = len(doc_ids) - len(set(doc_ids))
    duplicate_texts = len(text_values) - len(set(text_values))

    schema = pa.schema([
        ("document_id", pa.string()),
        ("text", pa.string()),
        ("language", pa.string()),
        ("query_id", pa.int64()),
        ("passage_index", pa.int64()),
        ("is_selected", pa.int64()),
        ("source", pa.string()),
        ("english_text", pa.string()),
        ("query", pa.string()),
        ("query_type", pa.string()),
        ("source_lang", pa.string()),
        ("target_lang", pa.string())
    ])

    table = pa.Table.from_pylist(
        documents,
        schema=schema
    )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    pq.write_table(
        table,
        output_path
    )

    out_file_size = os.path.getsize(output_path)

    val_pf = pq.ParquetFile(output_path)
    val_num_rows = val_pf.metadata.num_rows
    val_schema = val_pf.schema_arrow
    val_batch = next(
        val_pf.iter_batches(batch_size=3)
    ).to_pylist()

    print("\nCorpus build complete.")
    print(f"Source records: {source_records_inspected}")
    print(f"Passages found: {total_passages_encountered}")
    print(f"Documents written: {len(documents)}")
    print(f"Selected documents: {selected_docs}")
    print(f"Unselected documents: {unselected_docs}")
    print(f"Empty passages skipped: {empty_passages_skipped}")
    print(f"Duplicate document IDs: {duplicate_ids}")
    print(f"Duplicate text values: {duplicate_texts}")
    print(f"Output: {output_path}")
    print(
        f"Output size: {out_file_size / 1024:.2f} KB "
        f"({out_file_size:,} bytes)"
    )
    print(f"Memory before: {mem_before:.2f} MB")
    print(f"Memory after: {mem_after:.2f} MB")
    print(f"Memory change: {mem_delta:.2f} MB")
    print(f"Processing time: {processing_time} s")

    print("\nSchema:")
    for name in val_schema.names:
        print(f"{name}: {val_schema.field(name).type}")

    print("\nFirst 3 documents:")
    for idx, d in enumerate(val_batch[:3]):
        text_preview = (
            d["text"][:70] + "..."
            if len(d["text"]) > 70
            else d["text"]
        )

        print(
            f"{idx + 1}. "
            f"ID={d['document_id']} | "
            f"Selected={d['is_selected']} | "
            f"Lang={d['language']} | "
            f"QID={d['query_id']} | "
            f"Text={text_preview}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Development Corpus Builder"
    )

    parser.add_argument(
        "--input",
        type=str,
        default=DEFAULT_INPUT_PATH,
        help="Path to local source Parquet file"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_PATH,
        help="Output corpus Parquet path"
    )

    parser.add_argument(
        "--max-records",
        type=int,
        default=100,
        help="Maximum source records to inspect"
    )

    args = parser.parse_args()

    build_dev_corpus(
        input_path=args.input,
        output_path=args.output,
        max_records=args.max_records
    )


if __name__ == "__main__":
    main()