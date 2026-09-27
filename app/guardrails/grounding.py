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

        valid_document_ids = {
            str(document.get("document_id", ""))
            for document in retrieved_documents
            if document.get("document_id")
        }

        if not citations:
            return False, "No citations provided."

        if len(citations) != len(set(citations)):
            return False, "Duplicate document IDs found in citations."

        for document_id in citations:
            if document_id not in valid_document_ids:
                logger.warning(
                    f"Invalid citation: {document_id}"
                )

                return (
                    False,
                    f"Cited document ID '{document_id}' "
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
                grounded=False,
                confidence=0.0,
                unsupported_claims=[
                    f"Invalid citation: {citation_reason}"
                ],
                citations_valid=False,
                reason=citation_reason
            )

        if (
            "couldn't find enough relevant information"
            in answer.lower()
            or "पर्याप्त जानकारी नहीं"
            in answer
        ):
            return GroundingResult(
                grounded=False,
                confidence=0.0,
                citations_valid=True,
                reason="Answer is a refusal response."
            )

        if not retrieved_documents:
            return GroundingResult(
                grounded=False,
                confidence=0.0,
                unsupported_claims=[answer],
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

        context = " ".join(
            document.get("text", "")
            for document in target_documents
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

        answer_is_english = answer_latin > answer_devanagari
        answer_is_hindi = answer_devanagari > answer_latin

        context_is_english = context_latin > context_devanagari
        context_is_hindi = context_devanagari > context_latin

        cross_lingual = (
            (answer_is_english and context_is_hindi)
            or
            (answer_is_hindi and context_is_english)
        )

        sentences = [
            sentence.strip()
            for sentence in re.split(
                r"[.!?|।]",
                answer
            )
            if sentence.strip()
        ]

        if not sentences:
            sentences = [answer.strip()]

        unsupported_claims = []
        supported_count = 0

        for sentence in sentences:
            sentence_keywords = self.extract_keywords(
                sentence
            )

            if not sentence_keywords:
                supported_count += 1
                continue

            matching_keywords = (
                sentence_keywords.intersection(
                    context_keywords
                )
            )

            new_keywords = (
                sentence_keywords - context_keywords
            )

            overlap_ratio = (
                len(matching_keywords)
                / len(sentence_keywords)
            )

            if (
                cross_lingual
                and citations
                and citations_valid
            ):
                supported_count += 1

            elif (
                overlap_ratio >= self.min_sentence_overlap_ratio
                or len(new_keywords) <= self.max_novel_terms
            ):
                supported_count += 1

            else:
                unsupported_claims.append(
                    sentence
                )

        confidence = round(
            supported_count / len(sentences),
            4
        ) if sentences else 1.0

        grounded = (
            not unsupported_claims
            and citations_valid
        )

        if grounded:
            reason = (
                "Answer is supported by the retrieved "
                "context and citations."
            )
        else:
            reason = (
                f"Found {len(unsupported_claims)} "
                "unsupported sentence claims."
            )

        return GroundingResult(
            grounded=grounded,
            confidence=confidence,
            unsupported_claims=unsupported_claims,
            citations_valid=citations_valid,
            reason=reason
        )