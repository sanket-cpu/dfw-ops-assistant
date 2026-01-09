# DFW Airport Operations Intelligence Copilot - v1.0

> **RAG-powered chatbot for DFW Airport HVAC maintenance operations**

A Retrieval-Augmented Generation (RAG) application that helps airport maintenance technicians quickly find information from DFW Airport operations manuals, design criteria, and HVAC maintenance documentation.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Knowledge Base](#knowledge-base)
- [Limitations](#limitations)

---

## Overview

Version 1.0 implements a **basic RAG pipeline** using LangChain and ChromaDB for document retrieval with OpenAI's GPT-4o-mini for question answering. The system enables maintenance technicians to ask natural language questions about DFW Airport HVAC systems, operational procedures, and design standards.

### Key Capabilities

- Query DFW Airport operations and design documentation using natural language
- Retrieve relevant context from 5+ technical manuals and guidelines
- Get AI-generated answers with source citations
- Simple chat interface for iterative questioning
- Real-time document retrieval with metadata tracking

---

## Features

### v1.0 Implementation

- ✅ **Document Ingestion**: Automatic loading of PDF, DOCX, and TXT files from `/backend/files`
- ✅ **Vector Search**: ChromaDB-based similarity search (k=3 retrieval)
- ✅ **LLM Integration**: OpenAI GPT-4o-mini for answer generation
- ✅ **Source Attribution**: Returns document title, page number, and content snippets
- ✅ **Chat Interface**: Clean Streamlit UI with conversation history
- ✅ **Chunking Strategy**: Recursive character text splitting (800 tokens, 120 overlap)
- ✅ **Metadata Enrichment**: Airport, doc type, and topic tags for each chunk

### Limitations

- No reranking or relevance scoring
- Fixed retrieval parameters (k=3)
- No query preprocessing or expansion
- Single vector store persistence location
- Manual document upload only (no UI-based ingestion)

---

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI | 0.121.3+ |
| **Frontend** | Streamlit | 1.51.0+ |
| **LLM** | OpenAI GPT-4o-mini | gpt-4.1-mini |
| **Embeddings** | OpenAI Embeddings | text-embedding-3-small |
| **Vector Store** | ChromaDB | 1.3.5+ |
| **RAG Framework** | LangChain | 1.0.8+ |
| **Python** | 3.12+ | - |
| **Package Manager** | UV | - |

---

## Project Structure

```
DFW-OPS-COPILOT/
├── backend/
│   ├── files/                          # Knowledge base documents (PDFs, DOCX, TXT)
│   │   ├── DFW_Design_Criteria_Manual_2025_FINAL.pdf
│   │   ├── DFW_Airport_Operations_Manual_-_4-1-2024.pdf
│   │   ├── HVAC-Design-Manual.pdf
│   │   ├── HVAC-LAWA-Guidelines.pdf
│   │   ├── hvac-preventive-maintenance-checklist.pdf
│   │   └── Context.txt
│   ├── api.py                          # FastAPI routes
│   └── chatbot.py                      # RAG logic and LangChain setup
├── data/                               # ChromaDB vector store (auto-generated)
│   └── .gitkeep
├── .venv/                              # Python virtual environment
├── .env                                # Environment variables (not tracked)
├── .env.example                        # Template for environment variables
├── .gitignore                          # Git ignore rules
├── .python-version                     # Python version specification
├── app.py                              # Streamlit frontend
├── pyproject.toml                      # UV package configuration
├── requirements.txt                    # Pip dependencies
├── uv.lock                             # UV lock file
└── README.md                           # This file
```

---

## Prerequisites

- **Python**: 3.12 or higher
- **OpenAI API Key**: Get one from [OpenAI Platform](https://platform.openai.com)
- **Package Manager**: UV (recommended) or pip
- **System**: Windows/Linux/macOS with 4GB+ RAM

---

## Installation

### Option 1: Using UV (Recommended)

```bash
# Clone or navigate to project directory
cd dfw-ops-copilot

# Install UV if not already installed
pip install uv

# Install dependencies
uv sync

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate
```

### Option 2: Using pip

```bash
# Clone or navigate to project directory
cd dfw-ops-copilot

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

### 1. Set up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_API_KEY_HERE
```

⚠️ **Never commit `.env` to version control!**

### 2. Prepare Knowledge Base

Place your PDF, DOCX, or TXT files in the `backend/files/` directory. The system will automatically load and index them on first run.

**Included Documents (v1):**
- DFW Design Criteria Manual (2025)
- DFW Airport Operations Manual (April 2024)
- HVAC Design Manual
- HVAC LAWA Guidelines
- HVAC Preventive Maintenance Checklist
- Context.txt (equipment inventory)

---

## Usage

### Running the Application

The application consists of two services that must run simultaneously:

#### Terminal 1: Start the FastAPI Backend

```bash
# Navigate to backend directory
cd backend

# Run the API server
uvicorn api:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

#### Terminal 2: Start the Streamlit Frontend

```bash
# In project root directory
streamlit run app.py
```

Frontend will open automatically in your browser at: `http://localhost:8501`

### First-Time Setup

On the first run, the system will:
1. Load all documents from `backend/files/`
2. Split documents into 800-token chunks with 120-token overlap
3. Generate embeddings using OpenAI's `text-embedding-3-small`
4. Store vectors in ChromaDB at `../data/`

This process takes **2-5 minutes** depending on document size. Subsequent runs use the persisted vector store.

### Example Queries

Try these questions in the chat interface:

```
What is the protocol for AHU filter replacement in Terminal C?

What temperature should be maintained in passenger areas during summer?

How should HVAC techs respond to a BAS alarm for Chiller C42 fault?

What are the design criteria for HVAC systems in Terminal D?
```

---

## API Documentation

### Available Endpoints

#### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "service": "RAG Assistant using FastAPI, OPENAI and Streamlit",
  "description": "Welcome to the Airport Assistant!",
  "status": "running"
}
```

#### 2. Search Documents
```http
GET /documents/{query}
```

**Parameters:**
- `query` (string): Search query

**Response:**
```json
{
  "documents": [...],
  "total": 3,
  "query": "HVAC filter replacement"
}
```

#### 3. Ask Question (Main RAG Endpoint)
```http
GET /ask?query={question}
```

**Parameters:**
- `query` (string): User question

**Response:**
```json
{
  "query": "What is the temperature range for passenger areas?",
  "answer": "According to the DFW Operations Manual, passenger areas must maintain...",
  "sources": [
    {
      "title": "DFW_Airport_Operations_Manual_-_4-1-2024.pdf",
      "page": "12",
      "snippet": "Maintain temp 72–76°F and 40–55% RH..."
    }
  ]
}
```

### Interactive API Docs

Once the backend is running, access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Knowledge Base

### Document Processing Pipeline

1. **Loading**: `DirectoryLoader` reads PDF/DOCX/TXT from `backend/files/`
2. **Splitting**: `RecursiveCharacterTextSplitter` creates 800-token chunks
3. **Metadata**: Auto-enrichment with `doc_title`, `airport`, `doc_type`, `topic`
4. **Embedding**: OpenAI `text-embedding-3-small` (1536 dimensions)
5. **Storage**: ChromaDB collection named `documents`

### Retrieval Configuration

```python
# From chatbot.py
retriever = chroma.as_retriever(
    search_type="similarity",
    search_kwargs={'k': 3}  # Returns top 3 most similar chunks
)
```

### Prompt Engineering

v1 uses a **strict grounding prompt** to prevent hallucination:
- Only answers from retrieved context
- Explicitly states when information is unavailable
- Cites specific manuals (OPS vs DCM)
- Returns source metadata (document name, page number, snippet)

---

## Limitations

### v1.0 Known Issues

1. **No Reranking**: Retrieved documents are not reranked by relevance
2. **Fixed k=3**: Cannot dynamically adjust number of retrieved chunks
3. **No Query Expansion**: Simple queries may miss relevant documents
4. **Single Persistence Path**: Vector store location hardcoded to `../data/`
5. **No Multi-Turn Context**: Each query is independent (no conversation memory)
6. **Manual Document Management**: No UI for uploading/removing documents
7. **Basic Error Handling**: Limited retry logic and fallback mechanisms

---

## Troubleshooting

### Common Issues

**Problem**: `OPENAI_API_KEY not found in environment variables`
- **Solution**: Ensure `.env` file exists in project root with valid API key

**Problem**: `No module named 'langchain'`
- **Solution**: Activate virtual environment and run `pip install -r requirements.txt`

**Problem**: ChromaDB shows 0 documents
- **Solution**: Delete `data/` folder and restart backend to re-index documents

**Problem**: Slow first query
- **Solution**: First query triggers document loading (2-5 min). Subsequent queries are fast.

**Problem**: Backend won't start on port 8000
- **Solution**: Port already in use. Change port: `uvicorn api:app --port 8001`

---


## License

This project is for internal DFW Airport use. All airport documentation remains property of Dallas Fort Worth International Airport.

---

## Version History

### v1.0 (January 2026)
- Initial release
- Basic RAG pipeline with ChromaDB + LangChain
- Streamlit chat interface
- FastAPI backend with 3 endpoints
- Support for 5 HVAC/operations manuals
- Source citation with metadata

**Built with:** FastAPI, LangChain, ChromaDB, OpenAI, Streamlit
