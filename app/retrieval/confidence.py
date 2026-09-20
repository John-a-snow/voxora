from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class RetrievalConfidenceResult:
    decision: str
    confidence: float
    top_score: float
    reason: str

    def to_dict(self):
        return {
            "decision": self.decision,
            "confidence": self.confidence,
            "top_score": self.top_score,
            "reason": self.reason
        }


class RetrievalConfidenceEvaluator:

    def __init__(
        self,
        min_dense_score: float = 0.30
    ):
        self.min_dense_score = min_dense_score

    def evaluate(
        self,
        results: List[Dict[str, Any]],
        min_score_override: float = None
    ) -> RetrievalConfidenceResult:

        threshold = (
            min_score_override
            if min_score_override is not None
            else self.min_dense_score
        )

        if not results:
            return RetrievalConfidenceResult(
                decision="LOW_CONFIDENCE",
                confidence=0.0,
                top_score=0.0,
                reason="No dense retrieval results."
            )

        scores = [
            float(item.get("score", 0.0))
            for item in results
        ]

        top_score = max(scores)

        confidence = max(
            0.0,
            min(1.0, top_score)
        )

        if top_score >= threshold:
            decision = "HIGH_CONFIDENCE"
            reason = (
                f"Top dense score {top_score:.4f} "
                f"passed threshold {threshold:.4f}."
            )
        else:
            decision = "LOW_CONFIDENCE"
            reason = (
                f"Top dense score {top_score:.4f} "
                f"was below threshold {threshold:.4f}."
            )

        return RetrievalConfidenceResult(
            decision=decision,
            confidence=confidence,
            top_score=top_score,
            reason=reason
        )