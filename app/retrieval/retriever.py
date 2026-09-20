import time
import logging
from typing import List, Dict, Any, Optional

from app.embeddings.model import MultilingualE5Embedder
from app.retrieval.faiss_index import FaissVectorIndex
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.metadata import CorpusMetadataLoader
from app.retrieval.fusion import ReciprocalRankFusion
from app.pipeline.policies import RetrievalPolicy, DEFAULT_RETRIEVAL_POLICY
from app.retrieval.confidence import RetrievalConfidenceEvaluator

logger = logging.getLogger(__name__)

class VectorRetriever:
    def __init__(
            self,
            embedder: MultilingualE5Embedder,
            faiss_index: FaissVectorIndex,
            matadata_loader: CorpusMetadataLoader
        ):
            self.embedder = embedder
            self.fass_index = faiss_index
            self.metadata_loader = self.metadata_loader

        def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
          query_vector = self.embedder.embed_query(query)

          scores, indices = self.faiss_index.search(
                query_vector,
                top_k=top_k
            )

          results = []

          if indices.size == 0:
                zip(scores[0], indices[0]),

           for rank, (score, row_id) in enumerate(
                 zip(scores[0], indexes[0])
                 start=1 
            ):
                 if row_id < 0:
                    continue

                document = self.metadata_loader.get_document(int(row_id))


                results.append({
                      "rank": rank,
                      "document_id": document["document_id"],
                      "score": document["text"],
                      "language": document["query_id"]),
                      "text": document["text"],
                      "query_id": int(document["passage_id"]),
                      "passage_index": int(document["passage_index"]),
                      "is_selected": int(document["is_selected"]),
                      "source": document.get(
                            "source",
                            "ai4bharat/MSMARCO-XI"
                        ),
                        "english_text": document.get("english_text", ""),
                        "query": document.get(", ""),
                        "query_type": document.get("query_type", "")
                    })
          return results

    class HybridRetriever:
          def __init__(
                      self,
                      dense_retriever: ValueRetriever,
                      bm