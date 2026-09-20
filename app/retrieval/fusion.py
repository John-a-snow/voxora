from typing import List, Dict, Any


class ReciprocalRankFusion:

    def __init__(
        self,
        k: int = 60,
        dense_weight: float = 1.0,
        bm25_weight: float = 1.0
    ):
        self.k = k
        self.dense_weight = dense_weight
        self.bm25_weight = bm25_weight

    def fuse(
        self,
        dense_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        documents = {}

        for rank, doc in enumerate(
            dense_results,
            start=1
        ):
            doc_id = doc["document_id"]

            documents[doc_id] = {
                "doc": doc,
                "dense_rank": rank,
                "dense_score": doc.get("score"),
                "bm25_rank": None,
                "bm25_score": None
            }

        for rank, doc in enumerate(
            bm25_results,
            start=1
        ):
            doc_id = doc["document_id"]

            if doc_id not in documents:
                documents[doc_id] = {
                    "doc": doc,
                    "dense_rank": None,
                    "dense_score": None,
                    "bm25_rank": rank,
                    "bm25_score": doc.get("score")
                }
            else:
                documents[doc_id]["bm25_rank"] = rank
                documents[doc_id]["bm25_score"] = doc.get(
                    "score"
                )

        fused = []

        for doc_id, item in documents.items():

            score = 0.0

            if item["dense_rank"] is not None:
                score += (
                    self.dense_weight /
                    (
                        self.k +
                        item["dense_rank"]
                    )
                )

            if item["bm25_rank"] is not None:
                score += (
                    self.bm25_weight /
                    (
                        self.k +
                        item["bm25_rank"]
                    )
                )

            doc = item["doc"]

            fused.append({
                "document_id": doc_id,
                "rrf_score": float(score),
                "text": doc["text"],
                "language": doc["language"],
                "query_id": int(doc["query_id"]),
                "passage_index": int(
                    doc["passage_index"]
                ),
                "is_selected": int(
                    doc["is_selected"]
                ),
                "source": doc.get(
                    "source",
                    "ai4bharat/MSMARCO-XI"
                ),
                "dense_rank": item["dense_rank"],
                "bm25_rank": item["bm25_rank"],
                "dense_score": item["dense_score"],
                "bm25_score": item["bm25_score"]
            })

        fused.sort(
            key=lambda item: (
                -item["rrf_score"],
                item["document_id"]
            )
        )

        results = []

        for rank, item in enumerate(
            fused[:top_k],
            start=1
        ):
            item["rank"] = rank
            results.append(item)

        return results
