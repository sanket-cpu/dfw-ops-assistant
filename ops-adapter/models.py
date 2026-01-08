"""Data models for Ops Intelligence Copilot."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    """Ticket model."""
    id: int
    title: str
    status: str  # "open", "in_progress", "resolved", "closed"
    priority: str  # "low", "medium", "high", "critical"
    created_at: datetime
    updated_at: datetime
    description: str
    bucket: Optional[str] = None  # Computed: "0-7 days", "8-14 days", etc.

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    """Response for GET /api/tickets."""
    tickets: List[Ticket]
    total: int


class TicketDetailResponse(BaseModel):
    """Response for GET /api/tickets/{id}."""
    ticket: Ticket


class Message(BaseModel):
    """Chat message."""
    role: str  # "user" or "assistant"
    content: str


class Citation(BaseModel):
    """Source citation for chat response."""
    doc_title: str
    page: Optional[str] = None
    snippet: str
    relevance_score: Optional[float] = None


class ChatRequest(BaseModel):
    """Request for POST /api/tickets/{id}/chat."""
    message: str
    history: Optional[List[Message]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Response for POST /api/tickets/{id}/chat."""
    answer: str
    citations: List[Citation]


class BucketInfo(BaseModel):
    """Backlog aging bucket info."""
    label: str
    count: int
    ticket_ids: List[int]


class KPIBacklogAgingResponse(BaseModel):
    """Response for GET /api/kpis/backlog-aging."""
    buckets: List[BucketInfo]
