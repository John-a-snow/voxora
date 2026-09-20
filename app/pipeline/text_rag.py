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

logger= logging.getLogger(__name__)

class TextRAGServices:
    def __init__(
            self,
            retriever: ProductionRetriever,
            provider:Optional[LLMProvider] = None,
            