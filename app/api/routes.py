import os 
import time
import tempfile
import logging

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from app.stt.sarvam import SarvamSTTProvider
from app.retrieval.metadata import CorpusMetadataLoader
from app.embeddings.model import MutlilingualE5Embedder
from app.retrieval.faiss_index import FaissVectorIndex
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.retriever import (
    ProductionRetriever,
    VectorRetriever
)
from app.generation.config import LLMConfig
from app.generation.llm import get_llm_provider
from app.guardrails.policy import (
    GuardrailPolicy,
    GuardrailPolicyConfig
)
from app.pipeline.text_rag import TEXTRAGService
from app.observability.latency_buffer import 

logger = logging.getLogger(__name__)

router = APIRouter()

services = {}

def initialize_services():
    if "rag_service" in services:
        return

    project_root = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    logger.info(
        "Initializing Sarvam STT provider..."
    )

    services["stt_provider"] = SarvamSTTProvider()

    logger.info(
        "Initializing RAG component..."
    )

    parquet_path = os.path.join(
        project_root,
        "data",
        "processed",
        "dev_corpus.parquet"
    )

    faiss_path = os.path.join(
        project_root,
        "data",
        "indexes",
        "dev.faiss"
    )

    bm25_path = os.path.join(
        project_root,
        "data",
        "indexes",
        "dev_bm25.pkl"
    )

    metadata_loader = CorpusMetadataLoader(
        parquet_path
    )

    embedder = MultilingualE5Embedder()

    faiss_idx = FaissVectorIndex()
    faiss_idx.load(
        faiss_path
    )

    bm25_idx = BM25Retriever()
    bm25_idx.load(
        bm25_path
    )

    vector_retriever = VectorRetriever(
        embedder=embedder,
        faiss_index=faiss_idx,
        metadata_loader=metadata_loader
    )

    retriever = ProductionRetriever(
        vector_retriever=vector_retriever,
        bm25_retriever=bm25_idx,
        metadata_loader=metadata_loader
    )

    os.environ["LLM_PROVIDER"] = "groq"

    llm_config = LLMConfig()
    llm_config.provider = "groq"

    provider = get_llm_provider(
        config=llm_config
    )

    policy = GuardrailPolicy(
        config=GuardrailPolicyConfig(
            max_grounding_retries=0
        )
    )

    services["rag_service"] = TextRAGService(
        retriever=retriever,
        provider=provider,
        policy=policy
    )

    logger.info(
        "Services initialized."
    )

@router.on_event("startup")
async def startup_event():
    initialize_services()

@router.post("/api/voice-query")
async def voice_query(
    audio: UploadFile = File(...)
):
    start_e2e = time.perf_counter()

    if (
        "stt_provider" not in services
        or "rag_service" not in services
    ):
        raise HTTPException(
            status_code=500,
            detail="Services not initialized"
        )

    stt_provider = services[
        "stt_provider"
    ]

    rag_service = services[
        "rag_service"
    ]
        

