
<p align="center">
  <img src="assets/Third_space.png" alt="Voxora" width="900">
</p>
<p align="center">

  <img src="https://img.shields.io/badge/TSX-3178C6?style=flat&logo=typescript&logoColor=white" alt="TSX"/>

  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python"/>

  <img src="https://img.shields.io/badge/Dockerfile-2496ED?style=flat&logo=docker&logoColor=white" alt="Dockerfile"/>

  <img src="https://img.shields.io/badge/JSON-000000?style=flat&logo=json&logoColor=white" alt="JSON"/>

  <img src="https://img.shields.io/badge/CSS-1572B6?style=flat&logo=css3&logoColor=white" alt="CSS"/>

</p>

<p align="center">

  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="MIT License"/>

</p>

# VOXORA

**Voxora is a voice-based question answering RAG pipeline that combines either voice or text. , document retrieval and grounded responses.**

**The main idea is simple: A user speaks or writes a question, the system converts it into text, searches the available knowledge base and returns an answer based on the retrieved information.**

# What Voxora can do

**Currently Voxora supports:**

* Voice-based questions
* Text-based questions
* Speech-to-text using Sarvam
* Multilingual text embeddings using E5
* Document search using FAISS
* BM25 search as a fallback
* Context-based answer generation using Groq
* Basic grounding checks for generated answers
* Source/citation IDs for retrieved information
* Retrieval and generation latency tracking
* A React frontend connected to the FastAPI backend

# Knowledge Base

The backend currently uses a development corpus containing 1,047 documents.

Along with the original development corpus, we added a small custom technology-focused corpus covering topics such as:

Hack Club
Git
GitHub
Python
Java
JavaScript
Web Development

## How It Works

**For a text question:**
```
Text Input
    ↓
E5 Embedding
    ↓
FAISS Search
    ↓
BM25 fallback when needed
    ↓
Relevant Documents
    ↓
Groq
    ↓
Grounding Check
    ↓
Final Answer
```
**For a voice question:**
```
Voice Input
    ↓
Sarvam Speech-to-Text
    ↓
Query
    ↓
E5 Embedding
    ↓
FAISS Search
    ↓
BM25 fallback when needed
    ↓
Relevant Documents
    ↓
Groq
    ↓
Grounding Check
    ↓
Final Answer
```

# Tech Stack
**Backend**
Python, FastAPI, FAISS, BM25, ONNX Runtime, Multilingual E5, Groq
Sarvam
PyArrow

**Frontend**
React, TypeScript, Vite, CSS

**Deployment**

Render for the backend
Vercel for the frontend


# Currently we have worked on:**

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
# How to run it locally

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

Do not commit API keys to GitHub.

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
│   ├── custom/
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
├── onnx/
│   └── tokenizer.json
│
├── scripts/
│   ├── build_embeddings.py
│   ├── build_faiss_index.py
│   ├── build_bm25_index.py
│   ├── merge_custom_corpus.py
│   └── serve.py
│
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── README.md
```

## Built by

- [@Arushv](https://github.com/John-a-snow)
- [@WhoisZenix](https://github.com/whoisZeniX)

