# DFW Airport Operations Copilot - Setup Guide

## Project Overview

The DFW Airport Operations Copilot is an intelligent assistant powered by Retrieval-Augmented Generation (RAG) technology. It provides airport staff with instant access to information from DFW Airport operational and design documentation through a conversational chat interface.

The system uses OpenAI's GPT models combined with vector search to deliver accurate, context-aware answers backed by source documents.

## Folder Structure

```
dfw-ops-copilot/
│
├── backend/                        # FastAPI backend server
│   ├── api.py                      # Main FastAPI application and endpoints
│   ├── chatbot.py                  # RAG implementation and document processing
│   ├── files/                      # Source documents directory
│   │   ├── *.pdf                   # PDF documents (Operations Manual, Design Criteria, etc.)
│   │   ├── *.docx                  # Word documents (if any)
│   │   └── *.txt                   # Text documents (if any)
│   └── __pycache__/                # Python bytecode cache
│
├── frontend/                       # React frontend application
│   ├── src/                        # Source code
│   │   ├── components/             # React components
│   │   │   ├── ChatPanel.jsx       # Main chat interface component
│   │   │   └── ChatPanel.css       # Chat panel styling
│   │   ├── assets/                 # Static assets (images, icons, etc.)
│   │   ├── App.jsx                 # Root React component
│   │   ├── App.css                 # Application-level styles
│   │   ├── index.css               # Global CSS styles
│   │   └── main.jsx                # React application entry point
│   ├── public/                     # Public static files
│   ├── node_modules/               # npm dependencies
│   ├── package.json                # npm dependencies and scripts
│   ├── package-lock.json           # npm dependency lock file
│   ├── vite.config.js              # Vite build configuration
│   ├── eslint.config.js            # ESLint configuration
│   ├── index.html                  # HTML entry point
│   └── README.md                   # Frontend-specific documentation
│
├── data/                           # Chroma vector database storage
│   └── chroma.sqlite3              # Vector embeddings and metadata (auto-generated)
│
├── .venv/                          # Python virtual environment (auto-generated)
├── .git/                           # Git repository data
├── .claude/                        # Claude Code configuration
│
├── .env                            # Environment variables (API keys)
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── .python-version                 # Python version specification
├── requirements.txt                # Python dependencies (pip)
├── pyproject.toml                  # Python project configuration (uv/pip)
├── uv.lock                         # uv dependency lock file
├── README.md                       # Project documentation
└── SETUP.md                        # This file
```

## Architecture

### System Components

The application follows a three-tier architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│  (React + Vite - Port 5173)                                 │
│  - ChatPanel Component: User interface                      │
│  - Handles user input and displays responses                │
│  - Real-time message streaming                              │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/REST API
                  │ (JSON)
┌─────────────────▼───────────────────────────────────────────┐
│                         Backend Layer                        │
│  (FastAPI - Port 8000)                                      │
│  - API Endpoints (/ask, /documents)                         │
│  - CORS middleware for cross-origin requests               │
│  - Request validation and error handling                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ LangChain Pipeline
┌─────────────────▼───────────────────────────────────────────┐
│                      RAG Processing Layer                    │
│  (LangChain + OpenAI + Chroma)                              │
│                                                              │
│  1. Query Processing                                         │
│     - Receives user question                                 │
│     - Detects if sources/citations are requested            │
│                                                              │
│  2. Document Retrieval                                       │
│     - Converts query to embeddings (text-embedding-3-large) │
│     - Searches Chroma vector DB for similar chunks          │
│     - Returns top 3 most relevant document chunks           │
│                                                              │
│  3. Context Augmentation                                     │
│     - Formats retrieved chunks with metadata                │
│     - Injects context into LLM prompt                       │
│     - Applies strict grounding instructions                 │
│                                                              │
│  4. Answer Generation                                        │
│     - Sends prompt + context to GPT-4-mini                  │
│     - Enforces source-based answering only                  │
│     - Returns answer with optional citations                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Vector Search
┌─────────────────▼───────────────────────────────────────────┐
│                      Data Storage Layer                      │
│  (Chroma Vector Database)                                   │
│  - Stores document chunks as vector embeddings              │
│  - Metadata: source, page, doc_title, airport, topic        │
│  - Persisted to disk in data/ directory                     │
│  - Supports similarity search                               │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Document Ingestion** (One-time setup):
   - PDF files placed in `backend/files/`
   - `chatbot.py` loads documents using PyMuPDFLoader
   - Documents are split into 800-character chunks (120 char overlap)
   - Chunks are converted to embeddings using OpenAI text-embedding-3-large
   - Embeddings stored in Chroma vector database (`data/`)
   - Metadata attached: source file, page number, document type, topic

2. **Query Processing** (Runtime):
   - User types question in frontend ChatPanel
   - Frontend sends HTTP GET request to `/ask?query=<question>`
   - Backend detects if sources are explicitly requested
   - Query converted to embedding vector
   - Vector search retrieves top 3 similar document chunks
   - Chunks + query injected into GPT-4-mini prompt
   - LLM generates grounded answer (only using provided context)
   - Response returned to frontend with optional source citations

3. **Answer Display**:
   - Frontend receives JSON response with answer and sources
   - Answer displayed in chat bubble
   - Sources shown with document name and page number (if requested)

### Technology Stack

**Backend:**
- **FastAPI**: Modern Python web framework for building APIs
- **LangChain**: Framework for building LLM applications
  - `langchain-openai`: OpenAI integration
  - `langchain-chroma`: Chroma vector store integration
  - `langchain-community`: Document loaders (PyMuPDF)
  - `langchain-core`: Core utilities and chains
- **Chroma**: Vector database for embeddings storage
- **OpenAI API**:
  - GPT-4-mini: Language model for answer generation
  - text-embedding-3-large: Embedding model for semantic search
- **PyMuPDF**: PDF parsing and text extraction
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation and settings management
- **python-dotenv**: Environment variable management

**Frontend:**
- **React 19**: UI library for building interactive interfaces
- **Vite**: Fast build tool and development server
- **Pure CSS**: No external UI frameworks (custom styling)
- **ESLint**: Code quality and linting

**Development Tools:**
- **uv**: Fast Python package installer and resolver
- **Git**: Version control

## Prerequisites

Before setting up the project, ensure you have:

- **Python 3.12+** installed ([Download Python](https://www.python.org/downloads/))
- **Node.js 18+** and npm installed ([Download Node.js](https://nodejs.org/))
- **OpenAI API Key** with access to GPT-4 and embeddings API ([Get API Key](https://platform.openai.com/api-keys))
- **Git** (optional, for version control)

## Setup Instructions

### 1. Environment Configuration

Create a `.env` file in the project root directory:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# .env contents:
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

**Important**: Never commit your `.env` file to version control. It's already included in `.gitignore`.

### 2. Backend Setup

#### Install Python Dependencies

Option A - Using uv (recommended, faster):
```bash
# Install uv if you don't have it
pip install uv

# Install dependencies
uv pip install -r requirements.txt
```

Option B - Using pip:
```bash
# Create virtual environment (optional but recommended)
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Add Documents

1. Place your PDF, DOCX, or TXT files in `backend/files/` directory
2. Supported formats:
   - PDF (recommended): Parsed with PyMuPDF for best results
   - DOCX: Word documents
   - TXT: Plain text files

Example documents:
- DFW Airport Operations Manual
- DFW Design Criteria Manual
- Standard Operating Procedures
- Safety guidelines

#### Configure Document Metadata (Optional)

Edit `backend/chatbot.py` lines 34-47 to add custom metadata for your documents:

```python
METADATA_CONFIG = {
    "your-document-name.pdf": {
        "airport": "dfw",
        "doc_type": "official",
        "source_name": "Human-Readable Document Name",
        "topic": "operations",  # or "design", "safety", etc.
    },
}
```

This metadata helps with:
- Better retrieval accuracy
- Organized source citations
- Topic-specific filtering

#### Start the Backend Server

```bash
cd backend
uvicorn api:app --reload --port 8000
```

The backend will:
- Start on `http://localhost:8000`
- Auto-load documents from `backend/files/` (first run only)
- Create vector database in `data/` directory
- Enable hot-reload for code changes (`--reload` flag)

**First Run Note**: Initial startup may take 1-2 minutes while documents are processed and embeddings are generated. Subsequent starts are instant.

Verify the backend is running:
```bash
# Open in browser or use curl
curl http://localhost:8000
# Should return: {"message": "DFW Airport RAG Assistant API"}
```

### 3. Frontend Setup

#### Install Node.js Dependencies

```bash
cd frontend
npm install
```

This installs:
- React and React DOM
- Vite build tooling
- Development dependencies (ESLint, etc.)

#### Start the Development Server

```bash
npm run dev
```

The frontend will:
- Start on `http://localhost:5173` (or next available port)
- Enable hot-module replacement (HMR) for instant updates
- Display the local and network URLs in the terminal

#### Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

You should see:
- A gradient background page
- A chat panel in the bottom-right corner
- Click the panel to expand and start chatting

## Using the Application

### Asking Questions

1. Click the chat panel to expand it
2. Type your question in the input field
3. Press Enter or click Send

Example questions:
- "What are the operating hours for Terminal D?"
- "What are the design requirements for taxiway lighting?"
- "How do I report a safety incident?"
- "What permits are needed for construction work?"

### Getting Source Citations

To see source documents and page numbers, explicitly request them:
- "What are the parking regulations? Give me sources."
- "Show me sources for terminal access procedures"
- "Where did you find information about fire safety codes?"

The system automatically detects requests for sources and includes citations.

### Response Format

Without source request:
```
Answer: Terminal D operates 24/7 with varying gate assignments based on airline schedules.
```

With source request:
```
Answer: Terminal D operates 24/7 with varying gate assignments based on airline schedules.

Sources:
- DFW Airport Operations Manual (page 42)
- Terminal Operations Guide (page 8)
```

## API Reference

### Endpoints

#### `GET /`
Health check and service information.

**Response:**
```json
{
  "message": "DFW Airport RAG Assistant API",
  "version": "0.1"
}
```

#### `GET /ask?query={question}`
Ask a question and receive a RAG-powered answer.

**Parameters:**
- `query` (string, required): The user's question

**Response:**
```json
{
  "query": "What are the operating hours?",
  "answer": "Terminal operations run 24/7...",
  "sources": [
    {
      "title": "DFW Airport Operations Manual",
      "page": "42",
      "snippet": "Terminal D operates continuously..."
    }
  ]
}
```

**Error Response:**
```json
{
  "query": "What are the operating hours?",
  "answer": "",
  "sources": [],
  "error": "OpenAI API error: Rate limit exceeded"
}
```

## Configuration

### Backend Configuration

**File**: `backend/chatbot.py`

Key configuration options:

```python
# LLM Model (line 24)
llm = ChatOpenAI(
    model="gpt-4-mini",          # or "gpt-4", "gpt-3.5-turbo"
    temperature=0,                # 0 = deterministic, 1 = creative
    max_completion_tokens=800     # Maximum response length
)

# Embedding Model (line 23)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large"  # or "text-embedding-3-small"
)

# Document Chunking (lines 100-103)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,        # Characters per chunk
    chunk_overlap=120      # Overlap for context continuity
)

# Retrieval Settings (lines 135-138)
retriever = chroma.as_retriever(
    search_type="similarity",
    search_kwargs={'k': 3}   # Number of chunks to retrieve
)

# Database Location (line 30)
persist_directory="../data"   # Vector database storage
```

### Frontend Configuration

**File**: `frontend/src/components/ChatPanel.jsx`

```javascript
// API endpoint (line 30)
const API_URL = 'http://localhost:8000/ask';

// Modify if backend runs on different host/port
```

### CORS Configuration

**File**: `backend/api.py`

```python
# Allowed origins (lines 20-21)
allow_origins=[
    "http://localhost:3000",   # Create React App default
    "http://localhost:5173"    # Vite default
]

# Add your production domain when deploying
```

## Advanced Features

### Customizing the Prompt

The system uses a strict, grounded prompt to prevent hallucinations. To modify response behavior, edit the prompt templates in `backend/chatbot.py` (lines 141-235):

- `BASE_TEMPLATE`: Core instructions for all queries
- `TEMPLATE_WITH_SOURCES`: Adds source citation instructions
- `TEMPLATE_WITHOUT_SOURCES`: Clean responses without citations

### Source Detection

The system automatically detects when users request sources using natural language patterns (lines 50-88 in `chatbot.py`):

- "give me sources"
- "show sources"
- "cite your sources"
- "where did you find this"

To modify detection, edit `should_include_sources()` function.

### Adding Custom Metadata

Enrich documents with custom metadata for better retrieval:

```python
METADATA_CONFIG = {
    "your-document.pdf": {
        "airport": "dfw",
        "doc_type": "procedure",     # official, guideline, procedure
        "source_name": "Display Name",
        "topic": "safety",           # operations, design, safety, etc.
        "department": "operations",   # Custom field
        "version": "2024-01"         # Custom field
    }
}
```

Access metadata in prompts or filtering logic.

### Vector Database Management

**Reset the database** (force re-indexing):
```python
# In backend/chatbot.py, uncomment line 131:
chroma.reset_collection()
```

**Check database stats**:
```python
# Run in Python shell:
from backend.chatbot import chroma
print(f"Documents in database: {chroma._collection.count()}")
```

## Troubleshooting

### Backend Issues

**Problem**: `OPENAI_API_KEY not found in environment variables`
- **Solution**: Create `.env` file in project root with valid API key
- Verify `.env` is in the same directory as `pyproject.toml`

**Problem**: `ModuleNotFoundError: No module named 'langchain'`
- **Solution**: Install dependencies: `pip install -r requirements.txt`
- Ensure you're in the correct virtual environment

**Problem**: `Address already in use (port 8000)`
- **Solution**: Kill existing process or use different port:
  ```bash
  uvicorn api:app --reload --port 8001
  ```

**Problem**: No documents loaded / empty responses
- **Solution**:
  1. Check files exist in `backend/files/`
  2. Verify file formats (PDF, DOCX, TXT)
  3. Check backend logs for parsing errors
  4. Reset database: uncomment `chroma.reset_collection()` in `chatbot.py`

**Problem**: OpenAI API rate limits / quota exceeded
- **Solution**:
  1. Check your OpenAI account billing and usage
  2. Reduce chunk retrieval count (`k=3` to `k=1`)
  3. Use cheaper models (gpt-3.5-turbo, text-embedding-3-small)

### Frontend Issues

**Problem**: `Failed to fetch` or CORS errors
- **Solution**:
  1. Verify backend is running on `http://localhost:8000`
  2. Check CORS settings in `backend/api.py`
  3. Open browser DevTools → Network tab to see exact error
  4. Ensure API_URL in ChatPanel.jsx matches backend address

**Problem**: Blank page / white screen
- **Solution**:
  1. Check browser console for JavaScript errors
  2. Verify Node dependencies installed: `npm install`
  3. Clear browser cache and reload
  4. Try incognito/private window

**Problem**: Styles not loading / broken layout
- **Solution**:
  1. Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
  2. Check `frontend/src/components/ChatPanel.css` exists
  3. Verify Vite dev server is running without errors

### General Issues

**Problem**: Slow responses / timeouts
- **Causes**:
  1. Large document collection (slow retrieval)
  2. High OpenAI API latency
  3. Too many chunks retrieved
- **Solutions**:
  1. Reduce `k` parameter in retriever (line 137 in chatbot.py)
  2. Use smaller embedding model (text-embedding-3-small)
  3. Optimize chunk size (reduce from 800 to 500)
  4. Check network connection

**Problem**: Inaccurate or irrelevant answers
- **Causes**:
  1. Relevant information not in documents
  2. Poor document chunking
  3. Query too vague
- **Solutions**:
  1. Add more comprehensive documents
  2. Adjust chunk size and overlap (lines 100-103)
  3. Increase retrieval count (`k=5` for more context)
  4. Rephrase question with more specific details

## Development

### Running in Development Mode

Backend (with auto-reload):
```bash
cd backend
uvicorn api:app --reload
```

Frontend (with HMR):
```bash
cd frontend
npm run dev
```

### Building for Production

Frontend build:
```bash
cd frontend
npm run build
```

Output: `frontend/dist/` directory with optimized static files

Serve production build:
```bash
npm run preview
```

### Code Quality

Run linter:
```bash
cd frontend
npm run lint
```

### Project Structure Best Practices

- Keep `backend/files/` organized by document type
- Don't commit `data/` directory (large binary files)
- Don't commit `.env` (contains secrets)
- Don't commit `node_modules/` or `.venv/` (regenerable)
- Use meaningful commit messages
- Document any custom metadata or configuration changes

## Next Steps

After successful setup:

1. **Test with sample questions** to verify RAG pipeline
2. **Add your organization's documents** to `backend/files/`
3. **Customize metadata** in `METADATA_CONFIG` for your documents
4. **Adjust retrieval parameters** based on response quality
5. **Customize the frontend** UI/UX to match your branding
6. **Deploy to production** (consider Docker, AWS, Azure, etc.)

## Support and Resources

- **LangChain Documentation**: https://python.langchain.com/
- **OpenAI API Reference**: https://platform.openai.com/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **Vite Guide**: https://vite.dev/guide/

For project-specific questions, review the code comments in:
- `backend/chatbot.py` (RAG implementation)
- `backend/api.py` (API endpoints)
- `frontend/src/components/ChatPanel.jsx` (UI component)
