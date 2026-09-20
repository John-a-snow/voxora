import time
import logging
from typing import List, Dict, Any, Optional

from app.embeddings.model import MultilingualE5Embedder
from app.retrieval.faiss_index import FaissVectorIndex
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.metadata import CorpusMetadataLoader
from app.retrieval.fusion import ReciprocalRankFusion
from app.pipeline.policies import (
    RetrievalPolicy,
    DEFAULT_RETRIEVAL_POLICY
)
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

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        query_vec = self.embedder.embed_query(query)

        scores, indices = self.faiss_index.search(
            query_vec,
            top_k=top_k
        )

        results = []

        if indices.size > 0:
            for rank, (score, row_idx) in enumerate(
                zip(scores[0], indices[0]),
                start=1
            ):
                if row_idx < 0:
                    continue

                doc = self.metadata_loader.get_document(
                    int(row_idx)
                )

                results.append({
                    "rank": rank,
                    "document_id": doc["document_id"],
                    "score": float(score),
                    "text": doc["text"],
                    "language": doc["language"],
                    "query_id": int(doc["query_id"]),
                    "passage_index": int(doc["passage_index"]),
                    "is_selected": int(doc["is_selected"]),
                    "source": doc.get(
                        "source",
                        "ai4bharat/MSMARCO-XI"
                    ),
                    "english_text": doc.get(
                        "english_text",
                        ""
                    ),
                    "query": doc.get(
                        "query",
                        ""
                    ),
                    "query_type": doc.get(
                        "query_type",
                        ""
                    )
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
            for rank, (score, row_idx) in enumerate(
                zip(scores[0], indices[0]),
                start=1
            ):
                if row_idx < 0:
                    continue

                doc = self.metadata_loader.get_document(
                    int(row_idx)
                )

                results.append({
                    "rank": rank,
                    "document_id": doc["document_id"],
                    "score": float(score),
                    "text": doc["text"],
                    "language": doc["language"],
                    "query_id": int(doc["query_id"]),
                    "passage_index": int(doc["passage_index"]),
                    "is_selected": int(doc["is_selected"]),
                    "source": doc.get(
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

        dense_candidates = (
            self.dense_retriever.retrieve(
                query,
                top_k=self.dense_candidate_k
            )
        )

        bm25_candidates = (
            self.retrieve_bm25_candidates(
                query,
                top_k=self.bm25_candidate_k
            )
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
        confidence_evaluator: Optional[
            RetrievalConfidenceEvaluator
        ] = None
    ):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever

        self.metadata_loader = (
            metadata_loader
            or getattr(
                vector_retriever,
                "metadata_loader",
                None
            )
        )

        self.policy = (
            policy
            or DEFAULT_RETRIEVAL_POLICY
        )

        self.confidence_evaluator = (
            confidence_evaluator
            or RetrievalConfidenceEvaluator(
                min_dense_score=self.policy.min_dense_score
            )
        )

    def retrieve_bm25_candidates(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        if (
            self.bm25_retriever is None
            or self.metadata_loader is None
        ):
            return []

        scores, indices = (
            self.bm25_retriever.search(
                query,
                top_k=top_k
            )
        )

        results = []

        if indices.size > 0:
            for rank, (score, row_idx) in enumerate(
                zip(scores[0], indices[0]),
                start=1
            ):
                if row_idx < 0:
                    continue

                doc = self.metadata_loader.get_document(
                    int(row_idx)
                )

                results.append({
                    "rank": rank,
                    "document_id": doc["document_id"],
                    "score": float(score),
                    "text": doc["text"],
                    "language": doc["language"],
                    "query_id": int(doc["query_id"]),
                    "passage_index": int(doc["passage_index"]),
                    "is_selected": int(doc["is_selected"]),
                    "source": doc.get(
                        "source",
                        "ai4bharat/MSMARCO-XI"
                    ),
                    "english_text": doc.get(
                        "english_text",
                        ""
                    ),
                    "query": doc.get(
                        "query",
                        ""
                    ),
                    "query_type": doc.get(
                        "query_type",
                        ""
                    )
                })

        return results

    def retrieve(
        self,
        query: str,
        policy_override: Optional[RetrievalPolicy] = None
    ) -> Dict[str, Any]:

        start_time = time.time()

        active_policy = (
            policy_override
            or self.policy
        )

        dense_results = (
            self.vector_retriever.retrieve(
                query,
                top_k=active_policy.dense_top_k
            )
        )

        confidence = (
            self.confidence_evaluator.evaluate(
                dense_results,
                min_score_override=active_policy.min_dense_score
            )
        )

        fallback_used = False
        final_candidates = []

        if (
            confidence.decision == "HIGH_CONFIDENCE"
            or not active_policy.fallback_enabled
            or self.bm25_retriever is None
        ):
            final_candidates = [
                dict(candidate)
                for candidate in dense_results[
                    :active_policy.final_top_k
                ]
            ]

        else:
            fallback_used = True

            bm25_candidates = (
                self.retrieve_bm25_candidates(
                    query,
                    top_k=active_policy.fallback_top_k
                )
            )

            seen_ids = set()

            for candidate in bm25_candidates:
                doc_id = candidate["document_id"]

                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    final_candidates.append(
                        dict(candidate)
                    )

                if len(final_candidates) >= (
                    active_policy.final_top_k
                ):
                    break

            if len(final_candidates) < (
                active_policy.final_top_k
            ):
                for candidate in dense_results:
                    doc_id = candidate["document_id"]

                    if doc_id not in seen_ids:
                        seen_ids.add(doc_id)
                        final_candidates.append(
                            dict(candidate)
                        )

                    if len(final_candidates) >= (
                        active_policy.final_top_k
                    ):
                        break

        for rank, item in enumerate(
            final_candidates,
            start=1
        ):
            item["rank"] = rank

        elapsed_ms = round(
            (time.time() - start_time) * 1000,
            2
        )

        return {
            "results": final_candidates,
            "confidence": confidence.to_dict(),
            "fallback_used": fallback_used,
            "dense_count": len(dense_results),
            "latency_ms": elapsed_ms
        }