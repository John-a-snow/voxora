import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple


logger = logging.getLogger(__name__)


STOP_WORDS = {
    "is", "was", "are", "were", "the", "a", "an", "and", "or",
    "in", "on", "at", "to", "for", "of", "with", "by", "that",
    "this", "का", "की", "के", "में", "से", "को", "पर", "और",
    "है", "हैं", "था", "थी", "थे", "यह", "वह", "द्वारा",
    "लिए", "एक", "या"
}


@dataclass
class GroundingResult:
    grounded: bool
    confidence: float
    unsupported_claims: List[str] = field(default_factory=list)
    citations_valid: bool = True
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grounded": self.grounded,
            "confidence": self.confidence,
            "unsupported_claims": self.unsupported_claims,
            "citations_valid": self.citations_valid,
            "reason": self.reason
        }


class GroundingValidator:
    def __init__(
        self,
        min_sentence_overlap_ratio: float = 0.35,
        max_novel_terms: int = 3
    ):
        self.min_sentence_overlap_ratio = min_sentence_overlap_ratio
        self.max_novel_terms = max_novel_terms

    @staticmethod
    def extract_keywords(text: str) -> Set[str]:
        words = re.findall(
            r"[^\s,.:;!?|\"'\(\)\[\]{}॥।]+",
            text.lower()
        )

        return {
            word
            for word in words
            if word not in STOP_WORDS
            and len(word) > 1
            and not word.isdigit()
        }
