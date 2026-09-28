import json
import os

import pyarrow as pa
import pyarrow.parquet as pq


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

BASE_CORPUS = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "dev_corpus.parquet"
)

CUSTOM_CORPUS = os.path.join(
    BASE_DIR,
    "data",
    "custom",
    "technology_corpus.jsonl"
)

OUTPUT_CORPUS = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "dev_corpus_custom.parquet"
)


def load_custom_documents():
    documents = []

    with open(
        CUSTOM_CORPUS,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:
            line = line.strip()

            if not line:
                continue

            item = json.loads(line)

            documents.append({
                "document_id": item["document_id"],
                "text": item["text"],
                "language": item.get(
                    "language",
                    "English"
                ),
                "query_id": -1,
                "passage_index": -1,
                "is_selected": 1,
                "source": item.get(
                    "source",
                    "Custom Knowledge"
                ),
                "english_text": item["text"],
                "query": "",
                "query_type": "custom_knowledge",
                "source_lang": "en",
                "target_lang": item.get(
                    "language",
                    "English"
                )
            })

    return documents


def main():
    if not os.path.exists(BASE_CORPUS):
        raise FileNotFoundError(
            f"Base corpus not found: {BASE_CORPUS}"
        )

    if not os.path.exists(CUSTOM_CORPUS):
        raise FileNotFoundError(
            f"Custom corpus not found: {CUSTOM_CORPUS}"
        )

    print("Loading existing corpus...")

    base_table = pq.read_table(
        BASE_CORPUS
    )

    base_documents = base_table.to_pylist()

    print(
        f"Existing documents: {len(base_documents)}"
    )

    print("Loading custom knowledge...")

    custom_documents = load_custom_documents()

    print(
        f"Custom documents: {len(custom_documents)}"
    )

    existing_ids = {
        document["document_id"]
        for document in base_documents
    }

    custom_documents = [
        document
        for document in custom_documents
        if document["document_id"] not in existing_ids
    ]

    documents = (
        base_documents +
        custom_documents
    )

    schema = base_table.schema

    table = pa.Table.from_pylist(
        documents,
        schema=schema
    )

    pq.write_table(
        table,
        OUTPUT_CORPUS
    )

    print()
    print("Merge complete")
    print("--------------")
    print(
        f"Original documents: {len(base_documents)}"
    )
    print(
        f"New custom documents: {len(custom_documents)}"
    )
    print(
        f"Total documents: {len(documents)}"
    )
    print(
        f"Output: {OUTPUT_CORPUS}"
    )


if __name__ == "__main__":
    main()