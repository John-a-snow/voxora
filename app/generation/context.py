from typing import List, Dict, Any, Tuple


class ContextBuilder:
    def __init__(self, max_context_documents: int = 5):
        self.max_context_documents = max_context_documents

    def build_context(
        self,
        documents: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:

        selected_docs = []
        seen_ids = set()

        for document in documents:
            doc_id = str(document.get("document_id", ""))

            if not doc_id or doc_id in seen_ids:
                continue

            seen_ids.add(doc_id)
            selected_docs.append(document)

            if len(selected_docs) >= self.max_context_documents:
                break

        if not selected_docs:
            return "NO CONTEXT AVAILABLE", []

        context_blocks = []

        for index, document in enumerate(selected_docs, start=1):
            doc_id = document.get("document_id", f"doc_{index}")
            score = document.get("score", 0.0)
            text = document.get("text", "").strip()

            block = (
                f"[DOCUMENT {index}]\n"
                f"document_id: {doc_id}\n"
                f"relevance_score: {score:.4f}\n"
                f"content: {text}"
            )

            context_blocks.append(block)

        context = "\n\n---\n\n".join(context_blocks)

        return context, selected_docs