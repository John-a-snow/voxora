from dataclasses import dataclass, asdict


@dataclass
class Document:
    document_id: str
    text: str
    language: str
    query_id: int
    passage_index: int
    is_selected: int
    source: str
    english_text: str
    query: str
    query_type: str
    source_lang: str
    target_lang: str

    def to_dict(self):
        return asdict(self)