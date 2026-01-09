/**
 * API client for Ops Intelligence Copilot backend
 */
import axios from "axios";
import type {
  TicketListResponse,
  TicketDetailResponse,
  ChatRequest,
  ChatResponse,
  KPIBacklogAgingResponse,
  TicketUpdateResponse,
  AskResponse,
} from "./types";

// WHY default to port 8000: uvicorn's default port is 8000 (used when running `uvicorn api:app`).
// This lets developers start the backend without any configuration. Production deployments set
// VITE_API_BASE_URL to the actual backend URL. The fallback prevents broken builds when env is missing.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Get all tickets with optional filtering
 */
export async function getTickets(params?: {
  status?: string;
  bucket?: string;
}): Promise<TicketListResponse> {
  const response = await apiClient.get<TicketListResponse>("/api/tickets", {
    params,
  });
  return response.data;
}

/**
 * Get a single ticket by ID
 */
export async function getTicket(ticketId: number): Promise<TicketDetailResponse> {
  const response = await apiClient.get<TicketDetailResponse>(
    `/api/tickets/${ticketId}`
  );
  return response.data;
}

/**
 * Get backlog aging KPI data
 */
export async function getBacklogAging(): Promise<KPIBacklogAgingResponse> {
  const response = await apiClient.get<KPIBacklogAgingResponse>(
    "/api/kpis/backlog-aging"
  );
  return response.data;
}

/**
 * Chat with AI about a specific ticket
 */
export async function chatWithTicket(
  ticketId: number,
  request: ChatRequest
): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>(
    `/api/tickets/${ticketId}/chat`,
    request
  );
  return response.data;
}

/**
 * Update a ticket's status
 *
 * WHY PATCH instead of PUT: HTTP semantics matter. PATCH means "partial update" - we're only
 * changing the status field, not replacing the entire ticket. PUT would imply sending the full
 * ticket object. Using correct HTTP methods helps with caching, proxies, and API documentation.
 */
export async function updateTicketStatus(
  ticketId: number,
  status: string
): Promise<TicketUpdateResponse> {
  const response = await apiClient.patch<TicketUpdateResponse>(
    `/api/tickets/${ticketId}`,
    { status }
  );
  return response.data;
}

/**
 * Ask a question using RAG Document Q&A
 */
export async function askDocument(query: string): Promise<AskResponse> {
  const response = await apiClient.get<AskResponse>("/ask", {
    params: { query },
  });
  return response.data;
}
