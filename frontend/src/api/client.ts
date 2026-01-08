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
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001";

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
