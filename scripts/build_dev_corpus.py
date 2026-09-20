import os
import sys
import time
import argparse

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.ingestion.models import Document


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DEFAULT_INPUT = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "hintrain.parquet"
)

DEFAULT_OUTPUT = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "dev_corpus.parquet"
)


def clean_text(value):
    if value is None:
        return ""

    return " ".join(
        str(value)
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split()
    )


def get_value(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)

    try:
        return value[key]
    except Exception:
        return default


def build_corpus(
    input_path,
    output_path,
    max_records
):
    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Dataset not found: {input_path}"
        )

    start = time.time()

    print("Reading dataset with DuckDB...")
    print(f"Input: {input_path}")

    conn = duckdb.connect()

    query = """
        SELECT
            query_id,
            target_lang,
            source_lang,
            query,
            query_type,
            passages
        FROM read_parquet(?)
        LIMIT ?
    """

    rows = conn.execute(
        query,
        [input_path, max_records]
    ).fetchall()

    conn.close()

    print(f"Source records read: {len(rows)}")

    documents = []
    total_passages = 0
    empty_passages = 0

    for row in rows:

        query_id = row[0]
        target_lang = row[1]
        source_lang = row[2]
        query_text = clean_text(row[3])
        query_type = row[4]
        passages = row[5]

        if query_id is None:
            query_id = len(documents) + 1

        translated = get_value(
            passages,
            "Translated_passages",
            []
        )

        english = get_value(
            passages,
            "English_passages",
            []
        )

        selected = get_value(
            passages,
            "is_selected",
            []
        )

        translated = translated or []
        english = english or []
        selected = selected or []

        total_passages += len(translated)

        for index, raw_text in enumerate(
            translated
        ):

            text = clean_text(raw_text)

            if not text:
                empty_passages += 1
                continue

            english_text = ""

            if index < len(english):
                english_text = clean_text(
                    english[index]
                )

            selected_flag = 0

            if index < len(selected):
                try:
                    selected_flag = int(
                        selected[index]
                    )
                except Exception:
                    selected_flag = 0

            document = Document(
                document_id=f"{query_id}_{index}",
                text=text,
                language=str(
                    target_lang or "hi"
                ),
                query_id=int(query_id),
                passage_index=int(index),
                is_selected=selected_flag,
                source="ai4bharat/MSMARCO-XI",
                english_text=english_text,
                query=query_text,
                query_type=str(
                    query_type or ""
                ),
                source_lang=str(
                    source_lang or "en"
                ),
                target_lang=str(
                    target_lang or "hi"
                )
            )

            documents.append(
                document.to_dict()
            )

    if not documents:
        raise RuntimeError(
            "No documents were extracted."
        )

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

    elapsed = round(
        time.time() - start,
        2
    )

    print()
    print("Corpus build complete")
    print("---------------------")
    print(f"Source records: {len(rows)}")
    print(f"Passages found: {total_passages}")
    print(f"Documents written: {len(documents)}")
    print(f"Empty passages: {empty_passages}")
    print(f"Output: {output_path}")
    print(f"Time: {elapsed} seconds")

    check = pq.read_table(
        output_path,
        columns=[
            "document_id",
            "text"
        ]
    )

    print(
        f"Validation: {check.num_rows} documents loaded."
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT
    )

    parser.add_argument(
        "--max-records",
        type=int,
        default=100
    )

    args = parser.parse_args()

    build_corpus(
        args.input,
        args.output,
        args.max_records
    )


if __name__ == "__main__":
    main()