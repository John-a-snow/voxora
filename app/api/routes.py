import os
import re
import time
import tempfile
from statistics import median
from typing import Dict, List, Any

import pyarrow.parquet as pq
from fastapi import APIRouter, UploadFile, File, HTTPException
from groq import Groq

from app.stt.sarvam import SarvamSTTProvider
from app.embeddings.model import MultilingualE5Embedder
from app.retrieval.faiss_index import FaissVectorIndex
from app.retrieval.bm25 import BM25Retriever


router = APIRouter()

services = {}
latency_records: List[Dict[str, float]] = []


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

CORPUS_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "dev_corpus.parquet"
)

FAISS_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "indexes",
    "dev.faiss"
)

BM25_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "indexes",
    "dev_bm25.pkl"
)


def load_corpus():
    table = pq.read_table(
        CORPUS_PATH
    )

    rows = table.to_pylist()

    return rows


def initialize_services():
    if services:
        return

    print("Loading backend services...")

    if not os.path.exists(CORPUS_PATH):
        raise FileNotFoundError(
            f"Corpus not found: {CORPUS_PATH}"
        )

    if not os.path.exists(FAISS_PATH):
        raise FileNotFoundError(
            f"FAISS index not found: {FAISS_PATH}"
        )

    if not os.path.exists(BM25_PATH):
        raise FileNotFoundError(
            f"BM25 index not found: {BM25_PATH}"
        )

    services["stt"] = SarvamSTTProvider()

    services["embedder"] = MultilingualE5Embedder()

    faiss_index = FaissVectorIndex()
    faiss_index.load(
        FAISS_PATH
    )
    services["faiss"] = faiss_index

    bm25_index = BM25Retriever()
    bm25_index.load(
        BM25_PATH
    )
    services["bm25"] = bm25_index

    services["documents"] = load_corpus()

    groq_key = os.getenv(
        "GROQ_API_KEY",
        ""
    )

    if not groq_key:
        raise ValueError(
            "GROQ_API_KEY is not configured."
        )

    services["groq"] = Groq(
        api_key=groq_key
    )

    services["groq_model"] = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b"
    )

    print(
        f"Loaded {len(services['documents'])} documents."
    )

    print("FAISS loaded.")
    print("BM25 loaded.")
    print("Sarvam loaded.")
    print("Groq loaded.")
    print("Backend ready.")


def is_unsafe(query: str) -> bool:
    patterns = [
        r"ignore previous instructions",
        r"ignore all instructions",
        r"system prompt",
        r"reveal your prompt",
        r"jailbreak",
        r"how to build a bomb",
        r"how to make explosives",
        r"how to hack into"
    ]

    text = query.lower()

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


def retrieve_documents(
    query: str,
    top_k: int = 5
):
    embedder = services["embedder"]
    faiss_index = services["faiss"]
    bm25_index = services["bm25"]
    documents = services["documents"]

    start = time.perf_counter()

    query_vector = embedder.embed_query(
        query
    )

    dense_scores, dense_indices = (
        faiss_index.search(
            query_vector,
            top_k=10
        )
    )

    dense_results = []

    for score, index in zip(
        dense_scores[0],
        dense_indices[0]
    ):
        if index < 0:
            continue

        doc = dict(
            documents[int(index)]
        )

        doc["score"] = float(score)
        doc["retrieval_type"] = "dense"

        dense_results.append(
            doc
        )

    top_score = (
        dense_results[0]["score"]
        if dense_results
        else 0.0
    )

    fallback_used = False

    if top_score < 0.30:
        fallback_used = True

        bm25_scores, bm25_indices = (
            bm25_index.search(
                query,
                top_k=10
            )
        )

        results = []

        for score, index in zip(
            bm25_scores[0],
            bm25_indices[0]
        ):
            if index < 0:
                continue

            doc = dict(
                documents[int(index)]
            )

            doc["score"] = float(score)
            doc["retrieval_type"] = "bm25"

            results.append(
                doc
            )

        selected = results[:top_k]

    else:
        selected = dense_results[:top_k]

    for rank, doc in enumerate(
        selected,
        start=1
    ):
        doc["rank"] = rank

    retrieval_ms = round(
        (time.perf_counter() - start) * 1000.0,
        2
    )

    return (
        selected,
        fallback_used,
        retrieval_ms
    )


def build_context(
    documents: List[Dict[str, Any]]
) -> str:

    blocks = []

    for index, doc in enumerate(
        documents,
        start=1
    ):
        blocks.append(
            f"[DOCUMENT {index}]\n"
            f"document_id: {doc.get('document_id', '')}\n"
            f"content: {doc.get('text', '')}"
        )

    if not blocks:
        return "NO CONTEXT AVAILABLE"

    return "\n\n---\n\n".join(
        blocks
    )


def generate_answer(
    query: str,
    context: str
):
    client = services["groq"]
    model = services["groq_model"]

    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer only from the supplied context. "
                    "Do not invent facts. "
                    "Use citation document IDs from the context. "
                    "If the context is insufficient, say so clearly. "
                    "Return only JSON."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{query}\n\n"
                    f"Context:\n{context}\n\n"
                    "Return JSON with this exact structure:\n"
                    "{"
                    "\"answer\":\"...\","
                    "\"citations\":[\"document_id\"],"
                    "\"grounded\":true,"
                    "\"confidence\":0.0"
                    "}"
                )
            }
        ],
        temperature=0.2,
        max_completion_tokens=512,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "grounded_answer",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "answer": {
                            "type": "string"
                        },
                        "citations": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "grounded": {
                            "type": "boolean"
                        },
                        "confidence": {
                            "type": "number"
                        }
                    },
                    "required": [
                        "answer",
                        "citations",
                        "grounded",
                        "confidence"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    generation_ms = round(
        (time.perf_counter() - start) * 1000.0,
        2
    )

    content = (
        response.choices[0]
        .message
        .content
        or ""
    )

    if not content:
        raise RuntimeError(
            "Groq returned an empty response."
        )

    import json

    data = json.loads(
        content
    )

    return (
        data,
        generation_ms
    )


def validate_grounding(
    answer: str,
    citations: List[str],
    documents: List[Dict[str, Any]]
):
    valid_ids = {
        str(doc["document_id"])
        for doc in documents
    }

    if not citations:
        return False, 0.0

    if not all(
        str(citation) in valid_ids
        for citation in citations
    ):
        return False, 0.0

    answer_words = set(
        re.findall(
            r"[a-zA-Z]{4,}",
            answer.lower()
        )
    )

    context_words = set()

    for doc in documents:
        context_words.update(
            re.findall(
                r"[a-zA-Z]{4,}",
                doc.get(
                    "text",
                    ""
                ).lower()
            )
        )

    if not answer_words:
        return True, 1.0

    overlap = (
        len(
            answer_words.intersection(
                context_words
            )
        )
        / len(answer_words)
    )

    grounded = overlap >= 0.10

    return grounded, round(
        overlap,
        4
    )


def percentile(
    values,
    percent
):
    if not values:
        return 0.0

    values = sorted(values)

    if len(values) == 1:
        return float(values[0])

    position = (
        percent / 100
    ) * (len(values) - 1)

    lower = int(position)
    upper = min(
        lower + 1,
        len(values) - 1
    )

    fraction = (
        position - lower
    )

    return (
        values[lower]
        + (
            values[upper]
            - values[lower]
        ) * fraction
    )


def get_metric(
    name: str
):
    values = [
        record[name]
        for record in latency_records
        if name in record
    ]

    return {
        "p50": round(
            percentile(values, 50),
            2
        ),
        "p70": round(
            percentile(values, 70),
            2
        ),
        "p100": round(
            percentile(values, 100),
            2
        )
    }


@router.on_event("startup")
async def startup_event():
    initialize_services()


@router.post("/api/voice-query")
async def voice_query(
    audio: UploadFile = File(...)
):
    start_e2e = time.perf_counter()

    if not services:
        initialize_services()

    temporary_path = None

    try:
        suffix = (
            os.path.splitext(
                audio.filename or ".webm"
            )[1]
            or ".webm"
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            content = await audio.read()

            temp_file.write(
                content
            )

            temporary_path = temp_file.name

        stt_result = services[
            "stt"
        ].transcribe(
            temporary_path
        )

    finally:
        if (
            temporary_path
            and os.path.exists(
                temporary_path
            )
        ):
            os.remove(
                temporary_path
            )

    if not stt_result.transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="No speech detected."
        )

    transcript = (
        stt_result.transcript.strip()
    )

    language = (
        "Hindi"
        if "hi" in (
            stt_result.detected_language
            or ""
        ).lower()
        else "English"
    )

    if is_unsafe(transcript):
        total_ms = round(
            (
                time.perf_counter()
                - start_e2e
            ) * 1000.0,
            2
        )

        return {
            "transcript": transcript,
            "language": language,
            "answer": (
                "I can't help with that request."
            ),
            "grounded": False,
            "citations": [],
            "status": "refused_unsafe",
            "timings": {
                "stt_ms": stt_result.latency_ms,
                "retrieval_ms": 0.0,
                "generation_ms": 0.0,
                "grounding_ms": 0.0,
                "total_rag_ms": 0.0,
                "total_e2e_ms": total_ms
            },
            "retrieved_documents": []
        }

    documents, fallback_used, retrieval_ms = (
        retrieve_documents(
            transcript
        )
    )

    if not documents:
        total_ms = round(
            (
                time.perf_counter()
                - start_e2e
            ) * 1000.0,
            2
        )

        return {
            "transcript": transcript,
            "language": language,
            "answer": (
                "No relevant information was found "
                "in the knowledge base."
            ),
            "grounded": False,
            "citations": [],
            "status": "refused_insufficient",
            "timings": {
                "stt_ms": stt_result.latency_ms,
                "retrieval_ms": retrieval_ms,
                "generation_ms": 0.0,
                "grounding_ms": 0.0,
                "total_rag_ms": retrieval_ms,
                "total_e2e_ms": total_ms
            },
            "retrieved_documents": []
        }

    context = build_context(
        documents
    )

    generation_data, generation_ms = (
        generate_answer(
            transcript,
            context
        )
    )

    grounding_start = time.perf_counter()

    answer = generation_data.get(
        "answer",
        ""
    )

    citations = generation_data.get(
        "citations",
        []
    )

    grounded, grounding_confidence = (
        validate_grounding(
            answer,
            citations,
            documents
        )
    )

    grounding_ms = round(
        (
            time.perf_counter()
            - grounding_start
        ) * 1000.0,
        2
    )

    if not grounded:
        status = "ungrounded"
    else:
        status = "success"

    total_rag_ms = round(
        retrieval_ms
        + generation_ms
        + grounding_ms,
        2
    )

    total_e2e_ms = round(
        (
            time.perf_counter()
            - start_e2e
        ) * 1000.0,
        2
    )

    latency_records.append(
        {
            "stt_ms": stt_result.latency_ms,
            "retrieval_ms": retrieval_ms,
            "generation_ms": generation_ms,
            "grounding_ms": grounding_ms,
            "total_rag_ms": total_rag_ms,
            "total_e2e_ms": total_e2e_ms
        }
    )

    return {
        "transcript": transcript,
        "language": language,
        "answer": answer,
        "grounded": grounded,
        "citations": citations,
        "status": status,
        "timings": {
            "stt_ms": stt_result.latency_ms,
            "retrieval_ms": retrieval_ms,
            "generation_ms": generation_ms,
            "grounding_ms": grounding_ms,
            "total_rag_ms": total_rag_ms,
            "total_e2e_ms": total_e2e_ms
        },
        "retrieved_documents": documents,
        "fallback_used": fallback_used,
        "grounding_confidence": grounding_confidence
    }


@router.get("/api/latency/summary")
async def latency_summary(
    sample_size: int = 10
):
    records = latency_records[
        -sample_size:
    ]

    count = len(records)

    if count == 0:
        return {
            "sample_count": 0,
            "updated_at": time.time(),
            "source": "live_requests",
            "stt_ms": {
                "p50": 0,
                "p70": 0,
                "p100": 0
            },
            "retrieval_ms": {
                "p50": 0,
                "p70": 0,
                "p100": 0
            },
            "generation_ms": {
                "p50": 0,
                "p70": 0,
                "p100": 0
            },
            "grounding_ms": {
                "p50": 0,
                "p70": 0,
                "p100": 0
            },
            "total_rag_ms": {
                "p50": 0,
                "p70": 0,
                "p100": 0
            },
            "total_e2e_ms": {
                "p50": 0,
                "p70": 0,
                "p100": 0
            }
        }

    return {
        "sample_count": count,
        "updated_at": time.time(),
        "source": "live_requests",
        "stt_ms": get_metric("stt_ms"),
        "retrieval_ms": get_metric("retrieval_ms"),
        "generation_ms": get_metric("generation_ms"),
        "grounding_ms": get_metric("grounding_ms"),
        "total_rag_ms": get_metric("total_rag_ms"),
        "total_e2e_ms": get_metric("total_e2e_ms")
    }