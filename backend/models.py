"""Pydantic models for DFW Operations Intelligence Copilot API."""

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
    # WHY Optional and computed at query time: Bucket depends on current datetime, so storing
    # it would require constant updates. Computing on read ensures accurate age classification.
    # None when not yet computed; always populated in API responses via get_all_tickets().
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


class ChatAction(BaseModel):
    """Action suggested by AI copilot.

    WHY separate from answer: The AI suggests actions but doesn't execute them automatically.
    The frontend shows a confirmation button, requiring explicit user approval before calling
    the PATCH endpoint. This prevents accidental status changes from misinterpreted prompts.
    """
    type: str  # "update_status", "none"
    new_status: Optional[str] = None  # "open", "in_progress", "resolved", "closed"


class ChatResponse(BaseModel):
    """Response for POST /api/tickets/{id}/chat."""
    answer: str
    citations: List[Citation]
    # WHY action is Optional: Not every chat message triggers an action. Only when the AI
    # detects intent to change status will it include an action. UI conditionally renders
    # the confirmation button based on action presence.
    action: Optional[ChatAction] = None  # Suggested action from AI


class TicketStatusUpdate(BaseModel):
    """Request for PATCH /api/tickets/{id}."""
    status: str  # "open", "in_progress", "resolved", "closed"


class TicketUpdateResponse(BaseModel):
    """Response for PATCH /api/tickets/{id}."""
    ticket: Ticket
    message: str


class BucketInfo(BaseModel):
    """Backlog aging bucket info."""
    label: str
    count: int
    ticket_ids: List[int]


class KPIBacklogAgingResponse(BaseModel):
    """Response for GET /api/kpis/backlog-aging."""
    buckets: List[BucketInfo]
