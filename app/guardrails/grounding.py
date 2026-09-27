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

    def validate_citations(
        self,
        citations: List[str],
        retrieved_documents: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:

        valid_documents_ids = {
            str(document.get("document_id", ""))
            for document in retrieved_documents
            if document.get("document_id")
        }

        if not citations:
            return False, "No citations provided."

        if len(citations) != len(set(citations)):
            return False, "Duplicate document IDs found in citations."

        for document_id in citations:
            if document_id not in valid_documents_ids:
                logger.warning(
                    f"Invalid_citation: {document_id}"
                )

                return (
                    False,
                    f"Cited document ID" '{document_id}' "
                    f"was not retrieved."
                )
        return True, "All citations are valid."

    def validate(
            self, 
            query: str,
            answer: str,
            citations: List[str],
            retrieved_documents: List[Dict[str, Any]]
        ) -> GroundingResult:

            citations_valid, citation_reason = self.validate_citations(
                citations,
                retrieved_documents
            )

            if not citations_valid:
                return GroundingResult(
                    grounded=False,\
                    confidence=0.0,
                    unsupported_claims=[
                        f"Invalid citation: {citation_reason}"
                    ],
                    citations_valid=Falsem
                    reason=citation_reason
                )
            if (
                "couldn't find enough relevant information"
                if answer.lower()
                or "पर्याप्त जानकारी नहीं"
                in answer
            ):
                return GroundingResult(
                    grounded=False,
                    confidence=0.0,
                    citations_valid=True,
                    reason="Answer is a refusal respone."
                )

            if not retrieved_documents:
                return GroundingResult(
                    grounded=False,
                    confidence=0.0,
                    unsupported_claims=[claims],
                    citations_valid=citations_valid,
                    reason="No retrieved context is available."
                )
            if citations:
                citation_ids = set(citations)

                target_documents = [
                    document
                    for document in retrieved_documents
                    if str(document.get("document_id", "")) in citation_ids
                ]

                if not target_documents:
                    target_documents = retrieved_documents
            else:

                target_documents = retrieved_documents

            context = "".join(
                document.get("text", "")
                for document in target_document
            )

            context_keywords = self.extract_keywords(context)

    
            answer_latin = len(
                re.findall(r"[a-zA-Z]", answer)
        )

            answer_devanagari = len(
                re.findall(r"[\u0900-\u097F]", answer)
        )

            context_latin = len(
                re.findall(r"[a-zA-Z]", context)
        )

            context_devanagari = len(
                re.findall(r"[\u0900-\u097F]", context)
        )
