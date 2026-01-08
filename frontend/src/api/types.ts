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

export interface ChatResponse {
  answer: string;
  citations: Citation[];
}

export interface BucketInfo {
  label: string;
  count: number;
  ticket_ids: number[];
}

export interface KPIBacklogAgingResponse {
  buckets: BucketInfo[];
}
