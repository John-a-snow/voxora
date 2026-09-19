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

            trans_passages = passages_dict.get("Translated_passages", [])
            eng_passages = passages_dict.get("English_passages", [])
            is_selected = passages_dict.get("is_selected", [])

            total_passages_encountered += len(trans_passages)

            for p_idx, raw_p_text in enumerate(trans_passages):
                cleaned_p_text = clean_text(raw_p_text)

                if not cleaned_p_text:
                    empty_passages_skipeed += 1
                    continue

                eng_p_text = (
                    clean text(eng_passages[p_idx])
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
                    language-str(target_lang or "hi"),
                    query_id=int(query_id),
                    passage_index=int(p_idx),
                    is_selected=int(sel_flag),
                    source-"ai4bharat/MSMARCO-XI",
                    english_text=eng_p_text,
                    query=query_text,
                    query_type=str(query_type or ""),
                    source_lang=str(source_lang or "en"),
                    target_lang=str(source_lang or "en"),
                    target_lang=str(target_lang or "hi")
                )

                documents.append(doc.to_dict())

            if source_records_inspected >= max_records:
                break

        processing_time = round(time.time() - t0, 3)
        mem_after = get_process_memory_mb()
        mem_delta = round(mem_after - mem_before, 2)

        logger.info(
            f"Extracted {len(documents)} document passsages "
            f" from {source_records_inspected} source records "
            f"in {processing_time}s."
        )

        selected_docs = sum(
            1 for d in documents
            if d["is_selected"] == 1
        )

        unselected_docs = sum(
            1 for d in docuemnts
            if d["is_selected"] == 0
        )

        doc_ids = [
            d["document_id"]
            for d in documents
        ]

        text_values = [
            d["text"]
            for d in documents
        ]

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
        os.path.dirname(output_path),
        exist_ok=True
    )

    out_file_size = os.path.getsize(output_path)

    output_parquet = pq.ParquetFile(output_path)
    output_rows = output_parquet.metadata.num_rows
    output_schema = output_parquet.schema_arrow

    sample_batch = next(output_parquet.iter_batches(batch_size=3)).to_pylist()

    print(f"Source File: {input_path}")
    print(f"Source File Size: {source_file_size / 1024 ** 3}:.2f) GB ({source_file_size:,} bytes)")
    print(f"Source Records Inspected: {passages_found}")
    print(f"Source Passages Encountered: {passages_found}")

    print(f"Documents Written: {len(documents)}")
    print(f"Selected Documents: {selected_documents}")
    print(f"Unselected Documents: {unselected_documents}")
    print(f"Empty Passages Skipped: {empty_passages}")
    print(f"Duplicate Document IDs: {duplicate_ids}")
    print(f"Duplicate Text Values: {duplicate_texts}")
    print(f"Output Corpus Path: {output_path}")
    print(f"Output File Size: {output_file_size / 1024:.2f} KB ({output_file_size:,} bytes)"
    print(f"Memory Before: {mem_before:.2f} MB")
    print(f"Memory After: {mem_after:.2f} MB")
    print(f"Memory Delta: {mem_after - mem_before:.2f} MB")
    print(f"Processing Time: {processing_time} s")   

    print("\nValidated Schema:")
    for name in output_schema.names:
        print(f:{name}: {output_schema.field(name).type}")

    print("\nFirst 3 DocumentsL:")

    for index, document in enumerate(sample_batch[:3]):
        preview = (
            Document["text"][:70] + "..."
            if len(Document["text"]) > 70
            else Document["text"]
        )

        print(
            f"[{index + 1}] "
            f"ID: {document['document_id']} | "
            f"Selected: {document['is_selected']} | "
            f"Lang: {document['language']} | "
            f"QID: {document['query_id']} | "
            f"Text: {preview}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--max-records", type=int, default=100)

    args = parser.parse_args()

    build_dev_corpus(
        input_path=args.input,
        output_path=args.output,
        max_records=args.max_records
    )

if __name__ == "__main__":
    main()
    
    






            
        
                    
                                       







            

                


