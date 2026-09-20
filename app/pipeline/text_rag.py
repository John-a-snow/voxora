import time
import logging
from typing import Dict, Any, Optional

from app.retrieval.retriever import ProductionRetriever
from app.pipeline.policies import RetrievalPolicy
from app.pipeline.state import RAGState
from app.generation.interface import LLMProvider
from app.generation.config import (
    LLMConfig,
    DEFAULT_LLM_CONFIG
)
from app.generation.context import ContextBuilder
from app.generation.parser import GenerationParser
from app.generation.llm import get_llm_provider
from app.guardrails.input import InputSafetyGuardrail
from app.guardrails.relevance import RetrievalRelevanceGuardrail
from app.guardrails.grounding import GroundingValidator
from app.guardrails.policy import GuardrailPolicy


logger = logging.getLogger(__name__)


class TextRAGService:
    def __init__(
        self,
        retriever: ProductionRetriever,
        provider: Optional[LLMProvider] = None,
        context_builder: Optional[ContextBuilder] = None,
        config: Optional[LLMConfig] = None,
        input_guardrail: Optional[InputSafetyGuardrail] = None,
        relevance_guardrail: Optional[RetrievalRelevanceGuardrail] = None,
        grounding_validator: Optional[GroundingValidator] = None,
        policy: Optional[GuardrailPolicy] = None
    ):
        self.retriever = retriever
        self.config = config or DEFAULT_LLM_CONFIG

        self.provider = (
            provider
            or get_llm_provider(self.config)
        )

        self.context_builder = (
            context_builder
            or ContextBuilder(
                max_context_documents=self.config.max_context_documents
            )
        )

        self.input_guardrail = (
            input_guardrail
            or InputSafetyGuardrail()
        )

        self.relevance_guardrail = (
            relevance_guardrail
            or RetrievalRelevanceGuardrail()
        )

        self.grounding_validator = (
            grounding_validator
            or GroundingValidator()
        )

        self.policy = (
            policy
            or GuardrailPolicy()
        )

    def run(
        self,
        query: str,
        policy_override: Optional[RetrievalPolicy] = None,
        dry_run: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        total_start = time.perf_counter()
        state = RAGState(query=query)

        input_start = time.perf_counter()

        input_res = self.input_guardrail.validate(
            query
        )

        input_guard_ms = round(
            (time.perf_counter() - input_start) * 1000.0,
            2
        )

        state.input_safety_status = (
            "passed"
            if input_res.safe
            else "rejected"
        )

        state.input_safety_category = (
            input_res.category
        )

        if not input_res.safe:
            total_ms = round(
                (time.perf_counter() - total_start) * 1000.0,
                2
            )

            response = self.policy.handle_unsafe_input(
                query,
                input_res
            )

            response["telemetry"] = {
                "input_guardrail_ms": input_guard_ms,
                "retrieval_ms": 0.0,
                "retrieval_guardrail_ms": 0.0,
                "context_build_ms": 0.0,
                "llm_ms": 0.0,
                "parsing_ms": 0.0,
                "grounding_guardrail_ms": 0.0,
                "total_guardrail_ms": input_guard_ms,
                "total_ms": total_ms
            }

            response["provider"] = getattr(
                self.provider,
                "provider_name",
                self.config.provider
            )

            response["model"] = getattr(
                self.provider,
                "model_name",
                self.config.model_name
            )

            return response

        retrieval_start = time.perf_counter()

        retrieval_output = self.retriever.retrieve(
            query,
            policy_override=policy_override
        )

        retrieval_ms = round(
            (time.perf_counter() - retrieval_start) * 1000.0,
            2
        )

        state.retrieved_documents = (
            retrieval_output.get(
                "results",
                []
            )
        )

        relevance_start = time.perf_counter()

        relevance_res = (
            self.relevance_guardrail.evaluate(
                retrieval_output
            )
        )

        relevance_ms = round(
            (time.perf_counter() - relevance_start) * 1000.0,
            2
        )

        state.retrieval_sufficiency = (
            relevance_res.decision
        )

        state.retrieval_guardrail_reason = (
            relevance_res.reason
        )

        if not relevance_res.sufficient:
            total_ms = round(
                (time.perf_counter() - total_start) * 1000.0,
                2
            )

            response = (
                self.policy.handle_insufficient_retrieval(
                    query,
                    relevance_res
                )
            )

            total_guard_ms = round(
                input_guard_ms + relevance_ms,
                2
            )

            response["telemetry"] = {
                "input_guardrail_ms": input_guard_ms,
                "retrieval_ms": retrieval_ms,
                "retrieval_guardrail_ms": relevance_ms,
                "context_build_ms": 0.0,
                "llm_ms": 0.0,
                "parsing_ms": 0.0,
                "grounding_guardrail_ms": 0.0,
                "total_guardrail_ms": total_guard_ms,
                "total_ms": total_ms
            }

            response["provider"] = getattr(
                self.provider,
                "provider_name",
                self.config.provider
            )

            response["model"] = getattr(
                self.provider,
                "model_name",
                self.config.model_name
            )

            return response

        context_start = time.perf_counter()

        context_str, selected_docs = (
            self.context_builder.build_context(
                state.retrieved_documents
            )
        )

        context_build_ms = round(
            (time.perf_counter() - context_start) * 1000.0,
            2
        )

        state.formatted_context = context_str

        if dry_run:
            total_ms = round(
                (time.perf_counter() - total_start) * 1000.0,
                2
            )

            total_guard_ms = round(
                input_guard_ms + relevance_ms,
                2
            )

            return {
                "query": query,
                "answer": (
                    "[DRY-RUN MODE] LLM call skipped. "
                    "Context payload formatted successfully."
                ),
                "grounded": False,
                "confidence": 0.0,
                "citations": [
                    doc.get("document_id", "")
                    for doc in selected_docs
                ],
                "status": "dry_run",
                "refusal_reason": None,
                "retrieved_documents": selected_docs,
                "context_str": context_str,
                "telemetry": {
                    "input_guardrail_ms": input_guard_ms,
                    "retrieval_ms": retrieval_ms,
                    "retrieval_guardrail_ms": relevance_ms,
                    "context_build_ms": context_build_ms,
                    "llm_ms": 0.0,
                    "parsing_ms": 0.0,
                    "grounding_guardrail_ms": 0.0,
                    "total_guardrail_ms": total_guard_ms,
                    "total_ms": total_ms
                },
                "provider": "dry_run",
                "model": "none"
            }

        current_retry = 0
        max_attempts = (
            1 + self.policy.config.max_grounding_retries
        )

        total_llm_ms = 0.0
        total_parse_ms = 0.0
        total_grounding_ms = 0.0

        last_parsed_response = None
        last_grounding_res = None

        while current_retry < max_attempts:
            llm_start = time.perf_counter()
            llm_result = None
            generation_error = None

            try:
                llm_result = self.provider.generate(
                    query,
                    context_str,
                    metadata=metadata
                )

                total_llm_ms += round(
                    (time.perf_counter() - llm_start) * 1000.0,
                    2
                )

            except Exception as err:
                total_llm_ms += round(
                    (time.perf_counter() - llm_start) * 1000.0,
                    2
                )

                generation_error = str(err)

            if generation_error or not llm_result:
                total_ms = round(
                    (time.perf_counter() - total_start) * 1000.0,
                    2
                )

                total_guard_ms = round(
                    input_guard_ms
                    + relevance_ms
                    + total_grounding_ms,
                    2
                )

                return {
                    "query": query,
                    "answer": (
                        f"Generation error: "
                        f"{generation_error}"
                    ),
                    "grounded": False,
                    "confidence": 0.0,
                    "citations": [],
                    "status": "error",
                    "refusal_reason": (
                        f"generation_error: "
                        f"{generation_error}"
                    ),
                    "retrieved_documents": selected_docs,
                    "context_str": context_str,
                    "telemetry": {
                        "input_guardrail_ms": input_guard_ms,
                        "retrieval_ms": retrieval_ms,
                        "retrieval_guardrail_ms": relevance_ms,
                        "context_build_ms": context_build_ms,
                        "llm_ms": total_llm_ms,
                        "parsing_ms": total_parse_ms,
                        "grounding_guardrail_ms": total_grounding_ms,
                        "total_guardrail_ms": total_guard_ms,
                        "total_ms": total_ms
                    },
                    "provider": getattr(
                        self.provider,
                        "provider_name",
                        self.config.provider
                    ),
                    "model": getattr(
                        self.provider,
                        "model_name",
                        self.config.model_name
                    )
                }

            parse_start = time.perf_counter()

            try:
                parsed_resp = GenerationParser.parse(
                    llm_result.raw_response,
                    provider=llm_result.provider,
                    model=llm_result.model
                )

                total_parse_ms += round(
                    (time.perf_counter() - parse_start) * 1000.0,
                    2
                )

                last_parsed_response = parsed_resp

            except Exception as parse_error:
                total_parse_ms += round(
                    (time.perf_counter() - parse_start) * 1000.0,
                    2
                )

                total_ms = round(
                    (time.perf_counter() - total_start) * 1000.0,
                    2
                )

                total_guard_ms = round(
                    input_guard_ms
                    + relevance_ms
                    + total_grounding_ms,
                    2
                )

                return {
                    "query": query,
                    "answer": (
                        f"Parsing error: "
                        f"{parse_error}"
                    ),
                    "grounded": False,
                    "confidence": 0.0,
                    "citations": [],
                    "status": "error",
                    "refusal_reason": (
                        f"parsing_error: "
                        f"{parse_error}"
                    ),
                    "retrieved_documents": selected_docs,
                    "context_str": context_str,
                    "telemetry": {
                        "input_guardrail_ms": input_guard_ms,
                        "retrieval_ms": retrieval_ms,
                        "retrieval_guardrail_ms": relevance_ms,
                        "context_build_ms": context_build_ms,
                        "llm_ms": total_llm_ms,
                        "parsing_ms": total_parse_ms,
                        "grounding_guardrail_ms": total_grounding_ms,
                        "total_guardrail_ms": total_guard_ms,
                        "total_ms": total_ms
                    },
                    "provider": llm_result.provider,
                    "model": llm_result.model
                }

            grounding_start = time.perf_counter()

            grounding_res = (
                self.grounding_validator.validate(
                    query=query,
                    answer=parsed_resp.answer,
                    citations=parsed_resp.citations,
                    retrieved_documents=selected_docs
                )
            )

            grounding_ms = round(
                (time.perf_counter() - grounding_start) * 1000.0,
                2
            )

            total_grounding_ms += grounding_ms
            last_grounding_res = grounding_res

            state.grounding_status = (
                "passed"
                if grounding_res.grounded
                else "rejected"
            )

            state.grounding_confidence = (
                grounding_res.confidence
            )

            state.unsupported_claims = (
                grounding_res.unsupported_claims
            )

            state.citation_validation = (
                grounding_res.citations_valid
            )

            state.retry_count = current_retry

            if grounding_res.grounded:
                total_ms = round(
                    (time.perf_counter() - total_start) * 1000.0,
                    2
                )

                total_guard_ms = round(
                    input_guard_ms
                    + relevance_ms
                    + total_grounding_ms,
                    2
                )

                return {
                    "query": query,
                    "answer": parsed_resp.answer,
                    "generated_answer": parsed_resp.answer,
                    "grounded": True,
                    "confidence": grounding_res.confidence,
                    "citations": parsed_resp.citations,
                    "status": "success",
                    "refusal_reason": None,
                    "retrieved_documents": selected_docs,
                    "context_str": context_str,
                    "unsupported_claims": [],
                    "retry_count": current_retry,
                    "telemetry": {
                        "input_guardrail_ms": input_guard_ms,
                        "retrieval_ms": retrieval_ms,
                        "retrieval_guardrail_ms": relevance_ms,
                        "context_build_ms": context_build_ms,
                        "llm_ms": round(total_llm_ms, 2),
                        "parsing_ms": round(total_parse_ms, 2),
                        "grounding_guardrail_ms": round(
                            total_grounding_ms,
                            2
                        ),
                        "total_guardrail_ms": total_guard_ms,
                        "total_ms": total_ms
                    },
                    "provider": llm_result.provider,
                    "model": llm_result.model
                }

            if self.policy.should_retry_grounding(
                grounding_res,
                current_retry
            ):
                logger.info(
                    f"Retrying answer generation for "
                    f"query '{query}' "
                    f"(retry {current_retry + 1})..."
                )

                current_retry += 1

            else:
                break

        total_ms = round(
            (time.perf_counter() - total_start) * 1000.0,
            2
        )

        total_guard_ms = round(
            input_guard_ms
            + relevance_ms
            + total_grounding_ms,
            2
        )

        generated_answer = (
            last_parsed_response.answer
            if last_parsed_response
            else None
        )

        response = (
            self.policy.handle_ungrounded_final(
                query,
                last_grounding_res,
                generated_answer=generated_answer
            )
        )

        response["generated_answer"] = generated_answer

        response["unsupported_claims"] = (
            last_grounding_res.unsupported_claims
            if last_grounding_res
            else []
        )

        response["retry_count"] = current_retry

        response["telemetry"] = {
            "input_guardrail_ms": input_guard_ms,
            "retrieval_ms": retrieval_ms,
            "retrieval_guardrail_ms": relevance_ms,
            "context_build_ms": context_build_ms,
            "llm_ms": round(total_llm_ms, 2),
            "parsing_ms": round(total_parse_ms, 2),
            "grounding_guardrail_ms": round(
                total_grounding_ms,
                2
            ),
            "total_guardrail_ms": total_guard_ms,
            "total_ms": total_ms
        }

        response["provider"] = getattr(
            self.provider,
            "provider_name",
            self.config.provider
        )

        response["model"] = getattr(
            self.provider,
            "model_name",
            self.config.model_name
        )

        return response