# DFW Ops Intelligence Copilot

An AI-powered operations intelligence platform for Dallas Fort Worth International Airport. Combines ticket management with a RAG-based AI copilot assistant.

## Features

- **Dashboard with Backlog Aging Visualization**: D3.js-powered chart showing ticket distribution across 4 aging buckets (0-7, 8-14, 15-30, 30+ days)
- **Interactive Ticket Management**: Browse, filter, and view detailed ticket information
- **AI Copilot Assistant**: Chat with an AI assistant about specific tickets for troubleshooting help
- **RAG Document Q&A**: Query DFW Airport documentation (operations manuals, design criteria, SMS)
- **Source Citations**: AI responses include citations from ticket descriptions and documents
- **Responsive UI**: Modern interface built with React and TypeScript

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│   ChromaDB   │
│ (React/Vite)│      │  (FastAPI)   │      │  (Vectors)   │
└─────────────┘      └──────────────┘      └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   OpenAI     │
                     │   GPT-4o     │
                     └──────────────┘
```

### Tech Stack

- **Frontend**: React 18, TypeScript, Vite, D3.js, React Router
- **Backend**: Python 3.12+, FastAPI, LangChain, OpenAI GPT-4o-mini
- **Vector Store**: ChromaDB with OpenAI embeddings
- **Database**: In-memory mock data (easily extendable to SQLite)

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dfw-ops-assistant
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

   **Note**: Ensure `.env` is UTF-8 encoded. If you see `UnicodeDecodeError`:
   ```bash
   python scripts/fix_env_encoding.py
   ```

3. **Install backend dependencies**
   ```bash
   uv sync  # preferred
   # or: pip install -r requirements.txt
   ```

4. **Start the backend**
   ```bash
   cd backend
   uvicorn api:app --reload --port 8001
   ```

5. **Start the frontend** (in another terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs

### Docker Deployment

```bash
docker compose up -d
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
```

## API Endpoints

### RAG Document Assistant
- `GET /documents/{query}` - Search documents using vector retrieval
- `GET /ask?query=` - Ask a question with RAG Q&A

### Ticket Management
- `GET /api/tickets` - List all tickets (supports `?status=` and `?bucket=` filters)
- `GET /api/tickets/{id}` - Get ticket details

### KPIs
- `GET /api/kpis/backlog-aging` - Get backlog aging statistics (4 buckets)

### Chat
- `POST /api/tickets/{id}/chat` - Chat with AI about a specific ticket
  ```json
  {
    "message": "What could be causing this issue?",
    "history": []
  }
  ```

## Usage

### Dashboard
- View the **Backlog Aging** chart showing ticket distribution
- Click on a chart bar to filter tickets by aging bucket
- Click on a ticket row to view details

### Ticket Detail Page
- View complete ticket information
- Chat with the **AI Copilot** about the ticket
- View **source citations** from ticket descriptions

### Document Q&A
- Query airport documentation via the `/ask` endpoint
- Supports DFW Operations Manual, Design Criteria Manual, SMS Manual

## Adding New Documents

1. Place PDF/DOCX/TXT files in `backend/files/`
2. Add metadata entry to `METADATA_CONFIG` in `backend/chatbot.py`
3. Restart the backend (documents auto-load if collection is empty)

## File Structure

```
.
├── backend/               # FastAPI backend
│   ├── api.py            # Unified API endpoints
│   ├── chatbot.py        # RAG document system
│   ├── mock_data.py      # Ticket mock data
│   ├── models.py         # Pydantic models
│   ├── env_loader.py     # Environment loading utilities
│   └── files/            # PDF/DOCX documents for RAG
├── frontend/             # React frontend
│   ├── src/
│   │   ├── api/          # API client and types
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── App.tsx       # Main app with routing
│   └── Dockerfile
├── data/                 # ChromaDB persistence (auto-created)
├── scripts/              # Utility scripts
├── docker-compose.yml
└── README.md
```

## Troubleshooting

### Port already in use
Edit the port in the uvicorn command or `docker-compose.yml`.

### ChromaDB not loading documents
Delete `data/` directory and restart the backend.

### OpenAI API errors
Verify your API key is correctly set in `.env`.

## License

MIT
