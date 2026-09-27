import logging
from dataclasses import dataclass
from typing import Any, Dict


logger = logging.getLogger(__name__)


@dataclass
class RetrievalRelevanceResult:
    sufficient: bool
    decision: str
    confidence: float
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sufficient": self.sufficient,
            "decision": self.decision,
            "confidence": self.confidence,
            "reason": self.reason,
        }


class RetrievalRelevanceGuardrail:
    def __init__(
        self,
        min_top1_score: float = 0.80,
        min_candidates: int = 1,
    ):
        self.min_top1_score = min_top1_score
        self.min_candidates = min_candidates

    def evaluate(
        self,
        retrieval_output: Dict[str, Any],
    ) -> RetrievalRelevanceResult:

        results = retrieval_output.get("results", [])
        confidence_meta = retrieval_output.get("confidence", {})

        if not results or len(results) < self.min_candidates:
            return RetrievalRelevanceResult(
                sufficient=False,
                decision="INSUFFICIENT",
                confidence=0.0,
                reason="No candidate documents retrieved from knowledge base.",
            )

        top1_score = float(results[0].get("score", 0.0))

        conf_score = float(
            confidence_meta.get(
                "confidence_score",
                top1_score,
            )
        )

        top2_score = (
            float(results[1].get("score", 0.0))
            if len(results) > 1
            else top1_score
        )

        score_gap = top1_score - top2_score

        doc_ids = [
            str(result.get("document_id"))
            for result in results
        ]

        decision = (
            "SUFFICIENT"
            if conf_score >= self.min_top1_score
            else "INSUFFICIENT"
        )

        logger.debug(
            "Relevance: top1=%.4f, top2=%.4f, gap=%.4f, "
            "confidence=%.4f, decision=%s, documents=%s",
            top1_score,
            top2_score,
            score_gap,
            conf_score,
            decision,
            doc_ids,
        )

        if conf_score < self.min_top1_score:
            return RetrievalRelevanceResult(
                sufficient=False,
                decision="INSUFFICIENT",
                confidence=round(conf_score, 4),
                reason=(
                    f"Top candidate similarity score "
                    f"({conf_score:.4f}) is below sufficiency "
                    f"threshold ({self.min_top1_score:.4f})."
                ),
            )

        return RetrievalRelevanceResult(
            sufficient=True,
            decision="SUFFICIENT",
            confidence=round(conf_score, 4),
            reason=(
                f"Retrieval context is sufficient "
                f"(top1_score={conf_score:.4f}, "
                f"candidates={len(results)})."
            ),
        )