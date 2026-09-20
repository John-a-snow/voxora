
<p align="center">
  <img src="assets/Third_space.png" alt="Voxora" width="900">
</p>

# VOXORA

**Voxora is a voice-based question answering project that combines speech-to-text, document retrieval and grounded responses.**

**The main idea is simple: a user speaks a question, the system converts it into text, searches the available knowledge base and returns an answer based on the retrieved information.**

## Current Progress

The project is still under development. Only a 40% of the project is functional and we are working on it .

## What is working right now

The current backend has a development corpus of 1,000 documents.

The backend can currently be started locally with FastAPI and the main retrieval components load successfully.

**Currently we have worked on:**

- Converting voice to text with Sarvam
- Creating text embeddings with E5
- Searching documents with FAISS
- Adding BM25 for another type of search
- Adding a fallback when search results
- Using Groq to generate answers

```text
Voice input
    ↓
Sarvam Speech to Text
    ↓
Query
    ↓
E5 Embedding
    ↓
FAISS Search
    ↓
BM25 fallback when needed
    ↓
Context
    ↓
Groq Response
    ↓
Grounding Check
    ↓
Final Answer
```

**How to run it locally**

For the backend:

```bash
.\.venv\Scripts\Activate.ps1
python serve.py
```

Backend:

```text
http://localhost:8001
```

FastAPI docs:

```text
http://localhost:8001/docs
```

For the frontend:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## Environment variables

The backend use a few API keys which are kept in `.env`.

```env
SARVAM_API_KEY=
GROQ_API_KEY=
LLM_PROVIDER=groq
GROQ_MODEL=openai/gpt-oss-20b
```
## Project structure

```text
voxora/
│
├── app/
│   ├── api/
│   ├── embeddings/
│   ├── generation/
│   ├── guardrails/
│   ├── ingestion/
│   ├── observability/
│   ├── pipeline/
│   ├── retrieval/
│   └── stt/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── indexes/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   ├── app.css
│   │   └── types.ts
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── postcss.config.mjs
│
├── scripts/
│   ├── build_dev_corpus.py
│   ├── build_embeddings.py
│   ├── build_faiss_index.py
│   └── build_bm25_index.py
│
├── api/
│   └── index.py
│
├── assets/
│   └── threadspace.png
│
├── serve.py
├── requirements.txt
├── vercel.json
├── .gitignore
└── README.md
```

## Tech used

Python, FastAPI, React, TypeScript, Sarvam, Groq, FAISS, BM25, Sentence Transformers and Vite.


## Built by
**Arushv**

**Zenix**

