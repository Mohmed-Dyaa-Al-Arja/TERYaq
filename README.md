# TERYAQ — Multimodal Clinical RAG for Breast Cancer

TERYAQ is a multimodal clinical Retrieval-Augmented Generation (RAG) system designed to provide evidence-grounded answers about breast cancer using clinical documents, visual evidence, and large language models.

The system combines document ingestion, semantic retrieval, visual understanding, reranking, evidence validation, safety checks, and response generation into an end-to-end pipeline.

## Project Architecture

```text
TERYaq/
│
├── backend/
│   ├── config/
│   ├── embedding/
│   ├── ingestion/
│   ├── llm/
│   ├── multimodal/
│   ├── rag/
│   ├── safety/
│   └── tests/
│
├── frontend/
│   ├── api/
│   ├── components/
│   ├── pages/
│   ├── assets/
│   ├── img/
│   └── utils/
│
├── data/
│   ├── README.md
│   └── pdf/
│
├── processed/
│   ├── chunks/
│   ├── metadata/
│   └── pages/
│
├── notebook/
│   └── RAG1_breast_Cancer.ipynb
│
├── doc/
│   ├── Untitled Diagram.drawio
│   └── Untitled Diagram.drawio.png
│
├── .env.example
├── .gitignore
└── README.md
```

## Main Components

### Backend

The backend contains the core AI and RAG pipeline:

* PDF ingestion and processing
* Text and visual chunking
* Metadata extraction
* Embedding generation
* Vector database retrieval
* Reranking
* Multimodal visual analysis
* Evidence validation
* Safety and claim verification
* LLM response generation

### Frontend

The frontend is built with Streamlit and provides:

* Document upload
* Breast cancer analysis
* RAG-based chat
* Result visualization
* History
* PDF report generation
* Features and project information
* Developer and team pages

## RAG Pipeline

```text
Clinical PDF
     │
     ▼
Document Ingestion
     │
     ├── Text Extraction
     ├── Page Rendering
     └── Visual Extraction
     │
     ▼
Chunking + Metadata
     │
     ▼
Embeddings
     │
     ▼
Vector Store
     │
     ▼
Retriever
     │
     ▼
Reranker
     │
     ▼
Evidence Gate
     │
     ▼
Multimodal / LLM Reasoning
     │
     ▼
Safety Validation
     │
     ▼
Grounded Response
```

## Technologies

* Python
* Streamlit
* LangChain
* ChromaDB
* Vector Embeddings
* Large Language Models
* Multimodal Vision Models
* PDF Processing
* Retrieval-Augmented Generation (RAG)
* Semantic Search
* Reranking
* Evidence Validation

## Team

### Mohamed Dyaa

AI / RAG / Backend Development

GitHub:
https://github.com/Mohmed-Dyaa-Al-Arja

### Yusuf

Contributor

GitHub:
https://github.com/Yusuf111414

### Maryam Shaker

Contributor

GitHub:
https://github.com/star942-coder

### Omar Alawar

Contributor

GitHub:
https://github.com/OmarAlawar1919

### Alaa Reda

Contributor

GitHub:
https://github.com/Alaa-Reda

## Important Notes

Generated vector databases, caches, Python bytecode, secrets, and other temporary files should not be committed to the repository.

API keys must be stored in environment variables and never hard-coded into source files.

## Disclaimer

This project is intended for research, educational, and development purposes.

It is not a substitute for professional medical advice, diagnosis, or treatment.

```
```

