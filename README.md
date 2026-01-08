# Ops Intelligence Copilot

An AI-powered operations intelligence platform that combines ticket management with an intelligent copilot assistant. Built with React, FastAPI, and OpenAI GPT-4.

## Features

- **Dashboard with Backlog Aging Visualization**: D3.js-powered chart showing ticket distribution across 4 aging buckets (0-7, 8-14, 15-30, 30+ days)
- **Interactive Ticket Management**: Browse, filter, and view detailed ticket information
- **AI Copilot Assistant**: Chat with an AI assistant about specific tickets to get troubleshooting help and recommendations
- **Source Citations**: AI responses include citations with excerpts from ticket descriptions
- **Responsive UI**: Modern, clean interface built with React and TypeScript

## Architecture

```
┌─────────────┐      ┌──────────────┐
│   Frontend  │─────▶│  ops-adapter │
│ (React/Vite)│      │   (FastAPI)  │
└─────────────┘      └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   tickets.db │
                     │   (SQLite)   │
                     └──────────────┘
```

### Services

- **Frontend**: React 18 + TypeScript + Vite, served via nginx
- **ops-adapter**: FastAPI backend with SQLite database and OpenAI integration
- **Database**: SQLite with 22 pre-populated mock tickets

## Quick Start

### Prerequisites

- Docker and Docker Compose
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

3. **Start the application**
   ```bash
   docker compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs

### That's it! The database is automatically initialized with mock tickets on first run.

## Usage

### Dashboard
- View the **Backlog Aging** chart showing ticket distribution
- Click on a chart bar to **filter tickets** by aging bucket
- Click on a ticket row to **view details**

### Ticket Detail Page
- View complete ticket information (title, status, priority, description, dates)
- Chat with the **AI Copilot** about the ticket
- Ask questions like:
  - "What could be causing this issue?"
  - "What are the recommended next steps?"
  - "Are there any similar known issues?"
- View **source citations** showing where the AI's information came from

## API Endpoints

### Tickets
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

## Development

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd ops-adapter
pip install -r requirements.txt
uvicorn main:app --reload
```

## Technology Stack

### Frontend
- React 18
- TypeScript
- Vite
- React Router
- D3.js (for charts)
- Axios

### Backend
- FastAPI
- SQLAlchemy (SQLite)
- OpenAI API (GPT-4o-mini)
- Pydantic

### Infrastructure
- Docker & Docker Compose
- nginx

## File Structure

```
.
├── frontend/              # React frontend
│   ├── src/
│   │   ├── api/          # API client and types
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── App.tsx       # Main app with routing
│   ├── Dockerfile        # Multi-stage build
│   └── nginx.conf        # nginx configuration
├── ops-adapter/          # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── models.py        # Pydantic models
│   ├── database.py      # SQLAlchemy models & DB logic
│   └── Dockerfile
├── data/                # SQLite database (auto-created)
├── docker-compose.yml   # Orchestration
└── README.md

```

## Key Features Explained

### D3.js Chart Implementation
The Backlog Aging chart uses D3.js with proper data join patterns to prevent SVG stacking bugs. It:
- Clears all elements on each render
- Implements cleanup functions to prevent memory leaks
- Handles click events for interactive filtering

### AI Chat with Citations
The chat system:
- Sends ticket context to OpenAI GPT-4o-mini
- Maintains conversation history
- Extracts citations from ticket descriptions
- Displays citations with document titles and text excerpts

### Docker Compose Setup
- Single command deployment (`docker compose up -d`)
- Automatic database initialization
- Volume persistence for data
- Environment variable configuration

## Troubleshooting

### Port already in use
If ports 3000 or 8001 are already in use, edit `docker-compose.yml` to change the port mappings.

### Database not initializing
Delete the `data/` directory and restart:
```bash
rm -rf data/
docker compose down
docker compose up -d
```

### OpenAI API errors
Verify your API key is correctly set in `.env`:
```bash
cat .env | grep OPENAI_API_KEY
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
