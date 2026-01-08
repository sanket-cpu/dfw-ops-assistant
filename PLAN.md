# Ops Intelligence Copilot - Implementation Plan

## Phase 1: Exploration Summary

**Existing Backend Analysis:**
- Location: `./backend` (not `./rag-backend` - will adapt)
- Type: DFW Airport RAG system using LangChain + ChromaDB + OpenAI
- Endpoints: `/ask?query=`, `/documents/{query}`
- Tech: FastAPI, LangChain, ChromaDB, OpenAI GPT-4
- Not directly compatible with required ticket/KPI endpoints

## Architecture Decisions

### 1. Service Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend  │─────▶│  ops-adapter │─────▶│ rag-backend  │
│ (React/Vite)│      │   (FastAPI)  │      │  (existing)  │
└─────────────┘      └──────────────┘      └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   tickets.db │
                     │   (SQLite)   │
                     └──────────────┘
```

**Decision: Create adapter service**
- **Why:** Existing backend is domain-specific (airport docs), not ticket management
- **What:** New FastAPI service (`ops-adapter`) provides ticket/KPI endpoints
- **Integration:** Adapter can leverage existing RAG for document-based answers
- **Data:** Use SQLite for ticket persistence + mock data initialization

### 2. Frontend Architecture

**Tech Stack:**
- React 18 + TypeScript
- Vite (build tool)
- D3.js (only for Backlog Aging chart)
- React Router (navigation)
- Axios (API client)

**Pages:**
1. **Dashboard** (`/`)
   - Backlog Aging chart (D3.js bar chart)
   - Tickets table with filtering
   - Chart bar click → filters table by bucket
   - Ticket row click → navigates to detail

2. **Ticket Detail** (`/ticket/:id`)
   - Ticket metadata display
   - Copilot chat interface
   - Citation rendering (inline snippets + metadata)

**D3 Chart Implementation:**
- Use D3 data join pattern to prevent SVG stacking
- Clear or update pattern: `svg.selectAll("*").remove()` before redraw OR proper enter/update/exit pattern
- Refs: `useRef<SVGSVGElement>(null)` + `useEffect` for D3 mounting

### 3. Docker Compose Structure

```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:80"]
    depends_on: [ops-adapter]

  ops-adapter:
    build: ./ops-adapter
    ports: ["8001:8001"]
    volumes: ["./data:/app/data"]
    env_file: .env

  rag-backend: (optional - only if integrating)
    build: ./backend
    ports: ["8000:8000"]
    volumes: ["./data:/app/data"]
    env_file: .env
```

**Decision:** Use 2 services (frontend + ops-adapter)
- Adapter can import/reuse RAG logic from existing backend OR operate standalone
- Simpler than 3-service architecture
- ChromaDB embedded in adapter, no separate service needed

### 4. API Specification

**ops-adapter endpoints:**

```
GET /api/tickets
Response: { tickets: Ticket[], total: number }
Ticket: { id, title, status, priority, created_at, updated_at, description, bucket }

GET /api/tickets/{id}
Response: { ticket: Ticket }

POST /api/tickets/{id}/chat
Request: { message: string, history?: Message[] }
Response: { answer: string, citations: Citation[] }
Citation: { doc_title, page, snippet, relevance_score }

GET /api/kpis/backlog-aging
Response: { buckets: [{ label, count, ticket_ids }] }
Buckets: "0-7 days", "8-14 days", "15-30 days", "30+ days"
```

## Implementation Checklist

### Phase 2: Planning ✓

- [x] Analyze existing backend
- [x] Design service architecture
- [x] Define API contracts
- [x] Create PLAN.md

### Phase 3: Backend (ops-adapter)

1. [ ] Initialize ops-adapter FastAPI project
   - Directory structure: `ops-adapter/`
   - `requirements.txt`, `Dockerfile`, `main.py`
   - CORS configuration for frontend

2. [ ] Create data models (Pydantic)
   - `Ticket`, `Message`, `Citation`, `KPIResponse`
   - Type validation

3. [ ] Implement SQLite database
   - `database.py` with SQLAlchemy models
   - Init script with 20+ mock tickets across 4 buckets
   - Aging calculation logic

4. [ ] Implement ticket endpoints
   - `GET /api/tickets` with optional filtering
   - `GET /api/tickets/{id}`

5. [ ] Implement KPI endpoint
   - `GET /api/kpis/backlog-aging`
   - Calculate days old, group into 4 buckets
   - Return counts + ticket IDs per bucket

6. [ ] Implement chat endpoint
   - `POST /api/tickets/{id}/chat`
   - Load ticket context into prompt
   - Use OpenAI (reuse existing pattern from backend)
   - Generate mock citations from ticket description
   - Return answer + citations

7. [ ] Add health check endpoint
   - `GET /health`

**Commit:** "feat: implement ops-adapter backend with tickets, KPI, and chat endpoints"

### Phase 4: Frontend

8. [ ] Initialize React + TypeScript + Vite project
   - `npm create vite@latest frontend -- --template react-ts`
   - Install deps: `react-router-dom`, `axios`, `d3`, `@types/d3`

9. [ ] Create API client
   - `src/api/client.ts` with TypeScript interfaces
   - Axios instance with base URL
   - Functions: `getTickets()`, `getTicket(id)`, `chatWithTicket(id, message)`, `getBacklogAging()`

10. [ ] Implement Dashboard page
    - `src/pages/Dashboard.tsx`
    - Fetch tickets + KPI data
    - Loading/error states

11. [ ] Implement D3 Backlog Aging chart
    - `src/components/BacklogAgingChart.tsx`
    - D3 bar chart with 4 buckets
    - Data join pattern: clear on unmount, update on data change
    - Bar click handler: `onBucketClick(bucket)`
    - Use `useRef` + `useEffect` pattern

**Subagent verification:** Check for SVG stacking bugs

12. [ ] Implement tickets table
    - `src/components/TicketsTable.tsx`
    - Display filtered tickets
    - Row click navigates to detail

13. [ ] Implement Ticket Detail page
    - `src/pages/TicketDetail.tsx`
    - Display ticket metadata
    - Embed chat component

14. [ ] Implement Copilot chat component
    - `src/components/CopilotChat.tsx`
    - Message input + send button
    - Message history display
    - Citation rendering with excerpts

**Subagent verification:** Check citation rendering

15. [ ] Add routing
    - `src/App.tsx` with React Router
    - Routes: `/`, `/ticket/:id`

16. [ ] Create Dockerfile for frontend
    - Multi-stage: build with Node, serve with nginx
    - `nginx.conf` for SPA routing

**Commit:** "feat: implement React frontend with dashboard, tickets, and chat UI"

### Phase 5: Docker Compose

17. [ ] Create docker-compose.yml
    - Services: frontend, ops-adapter
    - Network configuration
    - Volume mounts for persistence
    - Port mappings

18. [ ] Create .env.example
    - `OPENAI_API_KEY=your_key_here`
    - `API_BASE_URL=http://localhost:8001`

19. [ ] Update .gitignore
    - Add frontend/dist, node_modules
    - Add .env (keep .env.example)

20. [ ] Test docker compose up
    - Build all images
    - Verify services start
    - Check logs

**Commit:** "feat: add Docker Compose orchestration with .env.example"

### Phase 6: Verification

21. [ ] Subagent: Test acceptance criteria
    - Start services: `docker compose up -d`
    - Verify dashboard loads with chart + table
    - Test chart bar click filtering
    - Test ticket detail navigation
    - Test chat with citation rendering
    - Verify at least 1 citation returned

22. [ ] Fix any issues found

23. [ ] Final commit
    - Update README.md with usage instructions
    - Document architecture

**Commit:** "docs: add README with setup and usage instructions"

## Verification Criteria

✅ `docker compose up -d` starts all services without manual steps
✅ Dashboard shows 4-bucket Backlog Aging chart
✅ Dashboard shows tickets table
✅ Clicking chart bar filters table by bucket
✅ Clicking ticket row opens detail page
✅ Chat interface works and returns answer
✅ Chat response includes ≥1 citation with visible excerpt
✅ No SVG stacking in D3 chart on rerender
✅ Loading/error states work correctly
✅ TypeScript types are correct (no `any`)

## Key Implementation Notes

### D3 Chart Pattern (Prevent Stacking)

```tsx
useEffect(() => {
  if (!svgRef.current || !data) return;

  const svg = d3.select(svgRef.current);

  // METHOD 1: Clear everything
  svg.selectAll("*").remove();

  // METHOD 2: Data join with enter/update/exit
  const bars = svg.selectAll("rect").data(data);
  bars.enter().append("rect").merge(bars).attr(...);
  bars.exit().remove();

  // Cleanup
  return () => { svg.selectAll("*").remove(); };
}, [data]);
```

### Citation Rendering

```tsx
<div className="citation">
  <div className="citation-header">
    📄 {citation.doc_title} - Page {citation.page}
  </div>
  <div className="citation-snippet">
    {citation.snippet}
  </div>
</div>
```

### Docker Compose Command

```bash
# .env file must exist with OPENAI_API_KEY
docker compose up -d
# Access at http://localhost:3000
```

## Timeline

- **Phase 3 (Backend):** Items 1-7 (~7 commits)
- **Phase 4 (Frontend):** Items 8-16 (~9 commits)
- **Phase 5 (Docker):** Items 17-20 (~4 commits)
- **Phase 6 (Verification):** Items 21-23 (~3 commits)

**Total: ~23 commits, executed sequentially**

## Next Steps

Execute Phase 3 starting with item 1: Initialize ops-adapter FastAPI project.
