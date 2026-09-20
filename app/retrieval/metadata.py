import os
import pyarrow.parquet as pq


class CorpusMetadataLoader:
    def __init__(self, parquet_path: str):
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(
                f"Corpus file not found: {parquet_path}"
            )

        table = pq.read_table(parquet_path)
        self.documents = table.to_pylist()

    def get_document(self, row_id: int):
        if row_id < 0 or row_id >= len(self.documents):
            raise IndexError(
                f"Invalid document row: {row_id}"
            )

        return self.documents[row_id]

    def size(self) -> int:
        return len(self.documents)