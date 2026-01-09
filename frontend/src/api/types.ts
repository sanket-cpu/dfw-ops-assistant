/**
 * TypeScript types for API responses
 */

export interface Ticket {
  id: number;
  title: string;
  status: string;
  priority: string;
  created_at: string;
  updated_at: string;
  description: string;
  bucket: string;
}

export interface TicketListResponse {
  tickets: Ticket[];
  total: number;
}

export interface TicketDetailResponse {
  ticket: Ticket;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface Citation {
  doc_title: string;
  page?: string | null;
  snippet: string;
  relevance_score?: number | null;
}

export interface ChatRequest {
  message: string;
  history?: Message[];
}

export interface ChatAction {
  type: "update_status" | "none";
  new_status?: "open" | "in_progress" | "resolved" | "closed";
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  action?: ChatAction | null;
}

export interface TicketUpdateResponse {
  ticket: Ticket;
  message: string;
}

// RAG Document Q&A types
export interface AskResponse {
  query: string;
  answer: string;
  sources: Array<{
    title: string;
    page: string;
    snippet: string;
  }>;
  error?: string;
}

export interface BucketInfo {
  label: string;
  count: number;
  ticket_ids: number[];
}

export interface KPIBacklogAgingResponse {
  buckets: BucketInfo[];
}
