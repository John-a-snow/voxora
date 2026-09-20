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
        metadata_loader: CorpusMetadataLoader
    ):
        self.embedder = embedder
        self.faiss_index = faiss_index
        self.metadata_loader = metadata_loader

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vec = self.embedder.embed_query(query)
        scores, indices = self.faiss_index.search(query_vec, top_k=top_k)

        results: List[Dict[str, Any]] = []

        if indices.size > 0:
            for rank_idx, (score, row_idx) in enumerate(
                zip(scores[0], indices[0]),
                start=1
            ):
                if row_idx < 0:
                    continue

                doc_meta = self.metadata_loader.get_document(int(row_idx))

                results.append({
                    "rank": rank_idx,
                    "document_id": doc_meta["document_id"],
                    "score": float(score),
                    "text": doc_meta["text"],
                    "language": doc_meta["language"],
                    "query_id": int(doc_meta["query_id"]),
                    "passage_index": int(doc_meta["passage_index"]),
                    "is_selected": int(doc_meta["is_selected"]),
                    "source": doc_meta.get(
                        "source",
                        "ai4bharat/MSMARCO-XI"
                    ),
                    "english_text": doc_meta.get("english_text", ""),
                    "query": doc_meta.get("query", ""),
                    "query_type": doc_meta.get("query_type", "")
                })

        return results


class HybridRetriever:
    def __init__(
        self,
        dense_retriever: VectorRetriever,
        bm25_retriever: BM25Retriever,
        metadata_loader: CorpusMetadataLoader,
        dense_candidate_k: int = 20,
        bm25_candidate_k: int = 20,
        rrf_k: int = 60,
        dense_weight: float = 1.0,
        bm25_weight: float = 1.0
    ):
        self.dense_retriever = dense_retriever
        self.bm25_retriever = bm25_retriever
        self.metadata_loader = metadata_loader
        self.dense_candidate_k = dense_candidate_k
        self.bm25_candidate_k = bm25_candidate_k

        self.fusion = ReciprocalRankFusion(
            k=rrf_k,
            dense_weight=dense_weight,
            bm25_weight=bm25_weight
        )

    def retrieve_bm25_candidates(
        self,
        query: str,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        scores, indices = self.bm25_retriever.search(
            query,
            top_k=top_k
        )

        results = []

        if indices.size > 0:
            for rank_idx, (score, row_idx) in enumerate(
                zip(scores[0], indices[0]),
                start=1
            ):
                if row_idx < 0:
                    continue

                doc_meta = self.metadata_loader.get_document(
                    int(row_idx)
                )

                results.append({
                    "rank": rank_idx,
                    "document_id": doc_meta["document_id"],
                    "score": float(score),
                    "text": doc_meta["text"],
                    "language": doc_meta["language"],
                    "query_id": int(doc_meta["query_id"]),
                    "passage_index": int(doc_meta["passage_index"]),
                    "is_selected": int(doc_meta["is_selected"]),
                    "source": doc_meta.get(
                        "source",
                        "ai4bharat/MSMARCO-XI"
                    )
                })

        return results

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        dense_candidates = self.dense_retriever.retrieve(
            query,
            top_k=self.dense_candidate_k
        )

        bm25_candidates = self.retrieve_bm25_candidates(
            query,
            top_k=self.bm25_candidate_k
        )

        return self.fusion.fuse(
            dense_results=dense_candidates,
            bm25_results=bm25_candidates,
            top_k=top_k
        )


class ProductionRetriever:
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        bm25_retriever: Optional[BM25Retriever] = None,
        metadata_loader: Optional[CorpusMetadataLoader] = None,
        policy: Optional[RetrievalPolicy] = None,
        confidence_evaluator: Optional[RetrievalConfidenceEvaluator] = None
    ):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever

        self.metadata_loader = (
            metadata_loader
            or getattr(vector_retriever, "metadata_loader", None)
        )

        self.policy = policy or DEFAULT_RETRIEVAL_POLICY

        self.confidence_evaluator = (
            confidence_evaluator
            or RetrievalConfidenceEvaluator(
                min_dense_score=self.policy.min_dense_score
            )
        )

    def retrieve_bm25_candidates(
            self,
            query: str,
            top_k int = 5
        ) -> List[Dict[str, Any]]:
            if (
                self.self.bm25_retriever is None
                or self.self.metadata_loader is None
            ):
                return []

            sources, indices = self.bm25_retriever.search(\
                query,
                top_k=top_k
            )

            if indices.size > 0:
                for rank_idx, (score, row_) in enumerate(
                    zip(scores[0], indices[0]),
                    start=1
                ):
                    if now_idx < 0:
                        continue

                    doc_meta = self.metadata_loader.get_document(
                        int(row_idx)
                    )

                    results.append({
                        "rank": rank_idx,
                        "document_id": doc_meta["document_id"],
                        "score": float(score),
                        "text": doc_meta["text"],
                        "language"