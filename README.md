# DFW Ops Intelligence Copilot

An AI-powered operations intelligence platform for Dallas Fort Worth International Airport. Combines ticket management with a RAG-based AI copilot assistant that helps operations staff troubleshoot issues, manage tickets through natural language, and query airport documentation.

## Screenshots

### Dashboard Landing Page
![Dashboard Landing Page](screenshots/dashboarding%20landing%20page.png)

The main dashboard displays a **Backlog Aging** chart powered by D3.js, showing ticket distribution across 4 aging buckets (0-7, 8-14, 15-30, 30+ days). Below the chart, you can see all active tickets in a sortable table. Click on any chart bar to filter tickets by that aging bucket, or click on a ticket row to view details.

---

### Ticket Details Page
![Ticket Details Page](screenshots/Ticket%20Details%20page.png)

The ticket detail view shows complete information about a specific ticket including its status, priority, category, creation date, and full description. From here, you can interact with the AI Copilot to get troubleshooting help.

---

### AI Troubleshooter
![AI Troubleshooter](screenshots/AI%20Troubleshooter.png)

The AI Copilot assistant provides intelligent troubleshooting suggestions based on the ticket context. It analyzes the issue description and offers step-by-step guidance to help resolve problems. All responses include source citations from the ticket description.

---

### Close Ticket via Chat
![Close Ticket in Chat](screenshots/close%20ticket%20in%20chat.png)

The AI Copilot can execute actions through natural language. Simply tell it to "mark as resolved" or "close this ticket" and it will detect the action intent and present a confirmation button. Click to confirm and the ticket status updates immediately.

---

### Reopen Ticket via Chat
![Reopen Ticket in Chat](screenshots/reopen%20ticket%20in%20chat.png)

Similarly, you can reopen resolved tickets through chat. The AI understands commands like "reopen this ticket" or "mark as open" and provides a confirmation workflow before making changes.

---

### RAG Document Chatbot
![RAG Chatbot](screenshots/RAG%20Chatbot.png)

The Document Q&A panel (floating chat bubble) allows you to query DFW Airport documentation including operations manuals, design criteria, and SMS documentation. Responses are grounded in the actual documents with citations, preventing hallucination.

---

## Features

- **Dashboard with Backlog Aging Visualization**: D3.js-powered interactive chart showing ticket distribution across 4 aging buckets (0-7, 8-14, 15-30, 30+ days)
- **Interactive Ticket Management**: Browse, filter, and view detailed ticket information
- **AI Copilot Assistant**: Chat with an AI assistant about specific tickets for troubleshooting help
- **Natural Language Actions**: Update ticket status through conversational commands with confirmation workflow
- **RAG Document Q&A**: Floating chat widget to query DFW Airport documentation (Operations Manual, Design Criteria, SMS Manual)
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
                     │  GPT-4o-mini │
                     └──────────────┘
```

### Tech Stack

**Backend:**
- Python 3.12+
- FastAPI with uvicorn
- LangChain + LangChain-OpenAI
- ChromaDB for vector storage
- OpenAI GPT-4o-mini

**Frontend:**
- React 19
- TypeScript 5.9
- Vite 7
- D3.js for data visualization
- React Router 7
- Axios for API calls

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

   > **Important**: Save the `.env` file with UTF-8 encoding. Windows Notepad defaults to UTF-16 which causes `UnicodeDecodeError`. In VS Code, check the encoding in the bottom-right corner.

3. **Install backend dependencies**
   ```bash
   uv sync  # recommended
   # or: pip install -e .
   ```

4. **Start the backend**
   ```bash
   cd backend
   uvicorn api:app --reload
   ```
   The API will be available at http://localhost:8000

5. **Start the frontend** (in another terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The frontend will be available at http://localhost:5173

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Endpoints

### Health & Info
- `GET /` - Service info and available endpoints
- `GET /health` - Health check

### RAG Document Assistant
- `GET /documents/{query}` - Search documents using vector retrieval
- `GET /ask?query=` - Ask a question with RAG Q&A

### Ticket Management
- `GET /api/tickets` - List all tickets (supports `?status=` and `?bucket=` filters)
- `GET /api/tickets/{id}` - Get ticket details
- `PATCH /api/tickets/{id}` - Update ticket status

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

## Usage Guide

### Dashboard
1. View the **Backlog Aging** chart showing ticket distribution
2. Click on a chart bar to filter tickets by aging bucket
3. Click on a ticket row to view details and interact with the AI

### Ticket Detail Page
1. View complete ticket information
2. Chat with the **AI Copilot** for troubleshooting help
3. Use natural language to change ticket status:
   - "Mark this as resolved"
   - "Close this ticket"
   - "Reopen this ticket"
   - "Mark as in progress"
4. Click the confirmation button when prompted to execute the action

### Document Q&A (Floating Chat)
1. Click the chat bubble icon in the bottom-right corner
2. Ask questions about airport operations, design criteria, or safety procedures
3. Receive answers grounded in actual documentation with citations

## Included Documents

The following DFW documentation is pre-loaded for RAG queries:

| Document | Description |
|----------|-------------|
| DFW Airport Operations Manual (2024) | Airport operations procedures |
| DFW Design Criteria Manual (2025) | Design and construction standards |
| DFW SMS Manual (2025) | Safety Management System procedures |
| DFW SMS SOW | SMS scope of work |

### Adding New Documents

1. Place PDF/DOCX/TXT files in `backend/files/`
2. Add metadata entry to `METADATA_CONFIG` in `backend/chatbot.py`
3. Delete `data/` directory to reset ChromaDB
4. Restart the backend (documents auto-load on startup)

## File Structure

```
dfw-ops-assistant/
├── backend/                    # FastAPI backend
│   ├── api.py                 # Unified API endpoints
│   ├── chatbot.py             # RAG document system
│   ├── mock_data.py           # Ticket mock data (200 tickets)
│   ├── models.py              # Pydantic models
│   ├── env_loader.py          # Environment loading with encoding fallback
│   └── files/                 # PDF/DOCX documents for RAG
│       ├── DFW_Airport_Operations_Manual_-_4-1-2024.pdf
│       ├── DFW_Design_Criteria_Manual_2025_FINAL.pdf
│       ├── DFW_SMS_Manual_March_2025_FINAL.pdf
│       └── ...
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/               # API client and types
│   │   │   ├── client.ts      # Axios API client
│   │   │   └── types.ts       # TypeScript interfaces
│   │   ├── components/        # React components
│   │   │   ├── BacklogAgingChart.tsx  # D3.js aging chart
│   │   │   ├── CopilotChat.tsx        # Ticket AI chat
│   │   │   ├── DocumentQAPanel.tsx    # RAG chat widget
│   │   │   ├── TicketsTable.tsx       # Ticket list table
│   │   │   └── Toast.tsx              # Notification component
│   │   ├── pages/             # Page components
│   │   │   ├── Dashboard.tsx  # Main dashboard
│   │   │   └── TicketDetail.tsx
│   │   └── App.tsx            # Main app with routing
│   └── package.json
├── data/                       # ChromaDB persistence (auto-created)
├── screenshots/                # Application screenshots
├── pyproject.toml             # Python dependencies
├── docker-compose.yml         # Docker deployment
└── README.md
```

## Troubleshooting

### UnicodeDecodeError on startup
The `.env` file is likely saved as UTF-16 (Windows Notepad default). Re-save it as UTF-8:
- **VS Code**: Click encoding in bottom-right → "Save with Encoding" → UTF-8
- **Notepad**: File → Save As → Encoding: UTF-8

### ChromaDB not loading documents
Delete the `data/` directory and restart the backend. Documents will reload automatically.

### OpenAI API errors
Verify your API key is correctly set in `.env` and has sufficient credits.

### Port already in use
The default ports are:
- Backend: 8000 (uvicorn default)
- Frontend: 5173 (Vite default)

Change with `uvicorn api:app --port <PORT>` or set `VITE_API_BASE_URL` in frontend `.env`.

### CORS errors
The backend allows all origins by default. For production, update `allow_origins` in `backend/api.py`.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `VITE_API_BASE_URL` | Backend URL for frontend | `http://localhost:8000` |

## License

MIT
