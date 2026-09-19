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

DEFAULT_INPUT_PATH = "/home/arvind/.cache/huggingface/hub/datasets--ai4bharat--MSMARCO-XI/snapshots/bf5cdc1f26e581e519018e434db14edd1b77602b/train/hintrain.parquet"
DEFAULT_OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "dev_corpus.parquet"
)


def get_process_memory_mb():
    try:
        import psutil
        return psutil.Process().memory_info().rss / (1024 * 1024)
    except Exception:
        pass

    try:
        with open("/proc/self/status") as file:
            for line in file:
                if line.startswith("VmRSS:"):
                    return float(line.split()[1]) / 1024
    except Exception:
        pass

    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def clean_text(text):
    if not text:
        return ""

    text = str(text).replace("\r\n", "\n").replace("\r", "\n")
    return " ".join(text.split())


def build_dev_corpus(input_path, output_path, max_records=100):
    memory_before = get_process_memory_mb()
    start_time = time.time()

    if not os.path.exists(input_path):
        logger.error(f"Local source Parquet file not found at: {input_path}")
        sys.exit(1)

    source_size = os.path.getsize(input_path)
    logger.info(f"Reading dataset from {input_path}")
    logger.info(f"Source file size: {source_size / (1024 ** 3):.2f} GB")

    parquet_file = pq.ParquetFile(input_path)

    records_read = 0
    passages_found = 0
    empty_passages = 0
    documents = []

    for batch in parquet_file.iter_batches(batch_size=max_records):
        records = batch.to_pylist()

        for record in records:
            if records_read >= max_records:
                break

            records_read += 1

            query_id = record.get("query_id")
            if query_id is None:
                query_id = records_read

            target_lang = record.get("target_lang", "hi")
            source_lang = record.get("source_lang", "en")
            query = clean_text(record.get("query", ""))
            query_type = record.get("query_type", "")

            passages = record.get("passages", {})
            if not isinstance(passages, dict):
                continue

            translated = passages.get("Translated_passages", [])
            english = passages.get("English_passages", [])
            selected = passages.get("is_selected", [])

            passages_found += len(translated)

            for index, raw_text in enumerate(translated):
                text = clean_text(raw_text)

                if not text:
                    empty_passages += 1
                    continue

                english_text = (
                    clean_text(english[index])
                    if index < len(english)
                    else ""
                )

                is_selected = (
                    int(selected[index])
                    if index < len(selected)
                    else 0
                )

                document = Document(
                    document_id=f"{query_id}_{index}",
                    text=text,
                    language=str(target_lang or "hi"),
                    query_id=int(query_id),
                    passage_index=int(index),
                    is_selected=is_selected,
                    source="ai4bharat/MSMARCO-XI",
                    english_text=english_text,
                    query=query,
                    query_type=str(query_type or ""),
                    source_lang=str(source_lang or "en"),
                    target_lang=str(target_lang or "hi")
                )

                documents.append(document.to_dict())

        if records_read >= max_records:
            break

    selected_count = sum(
        1 for document in documents
        if document["is_selected"] == 1
    )

    document_ids = [document["document_id"] for document in documents]
    texts = [document["text"] for document in documents]

    duplicate_ids = len(document_ids) - len(set(document_ids))
    duplicate_texts = len(texts) - len(set(texts))

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

    table = pa.Table.from_pylist(documents, schema=schema)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pq.write_table(table, output_path)

    output_size = os.path.getsize(output_path)

    output_file = pq.ParquetFile(output_path)
    output_schema = output_file.schema_arrow
    sample = next(output_file.iter_batches(batch_size=3)).to_pylist()

    processing_time = round(time.time() - start_time, 3)
    memory_after = get_process_memory_mb()

    print(f"Source Records: {records_read}")
    print(f"Passages Found: {passages_found}")
    print(f"Documents Written: {len(documents)}")
    print(f"Selected Documents: {selected_count}")
    print(f"Empty Passages: {empty_passages}")
    print(f"Duplicate IDs: {duplicate_ids}")
    print(f"Duplicate Texts: {duplicate_texts}")
    print(f"Output File: {output_path}")
    print(f"Output Size: {output_size / 1024:.2f} KB")
    print(f"Processing Time: {processing_time} s")
    print(f"Memory: {memory_before:.2f} MB -> {memory_after:.2f} MB")

    print("\nSchema:")
    for name in output_schema.names:
        print(f"{name}: {output_schema.field(name).type}")

    print("\nSample Documents:")
    for index, document in enumerate(sample[:3]):
        preview = document["text"][:70]
        if len(document["text"]) > 70:
            preview += "..."

        print(
            f"{index + 1}. "
            f"{document['document_id']} | "
            f"{document['language']} | "
            f"{preview}"
        )


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
        default=DEFAULT_OUTPUT_PATH
    )

    parser.add_argument(
        "--max-records",
        type=int,
        default=100
    )

    args = parser.parse_args()

    build_dev_corpus(
        args.input,
        args.output,
        args.max_records
    )


if __name__ == "__main__":
    main()