"""
DFW Operations Intelligence Copilot - Unified Backend API.

Combines RAG document assistant with ticket management and AI copilot.

Architecture Note:
    WHY unified backend: The RAG document assistant and ticket management are kept
    in one API to share the OpenAI client and environment configuration. This avoids
    API key duplication and simplifies deployment. The two systems have different
    safety models - RAG uses strict grounding while ticket chat allows action execution.
"""

import os
import logging
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

from chatbot import retrieve_document, ask_question
from mock_data import get_all_tickets, get_ticket_by_id, calculate_bucket, update_ticket_status
from models import (
    Ticket, TicketListResponse, TicketDetailResponse,
    ChatRequest, ChatResponse, Citation, ChatAction,
    KPIBacklogAgingResponse, BucketInfo,
    TicketStatusUpdate, TicketUpdateResponse
)
from env_loader import load_env_robust

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables with encoding fallback
if not load_env_robust():
    logger.warning("Failed to load .env file, using system environment variables only")

# Initialize OpenAI client for ticket chat
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI app
app = FastAPI(
    title="DFW Operations Intelligence Copilot",
    description="AI-powered assistant combining RAG document Q&A with ticket management",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# RAG Document Assistant Endpoints
# ==============================================================================

class DocumentResponse(BaseModel):
    documents: List
    total: int
    query: str
    error: str = None


class AskResponse(BaseModel):
    query: str
    answer: str
    sources: List[dict] = []
    error: str = None


@app.get("/")
def read_root():
    """Health check and service info."""
    return {
        "service": "DFW Operations Intelligence Copilot",
        "description": "AI-powered assistant for DFW Airport operations, documentation, and ticket management",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "rag": ["/documents/{query}", "/ask"],
            "tickets": ["/api/tickets", "/api/tickets/{id}", "/api/kpis/backlog-aging", "/api/tickets/{id}/chat"]
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/documents/{query}")
def search_documents(query: str) -> DocumentResponse:
    """Search documents using RAG retrieval."""
    try:
        documents = retrieve_document(query)
        return {"documents": documents, "total": len(documents), "query": query}
    except Exception as e:
        logger.error(f"Error searching documents: {e}", exc_info=True)
        return {"error": str(e), "documents": [], "total": 0, "query": query}


@app.get("/ask")
def ask(query: str) -> AskResponse:
    """Ask a question using RAG Q&A."""
    try:
        result = ask_question(query)
        return {
            "query": query,
            "answer": result["answer"],
            "sources": result["sources"]
        }
    except Exception as e:
        logger.error(f"Error asking question: {e}", exc_info=True)
        return {"error": str(e), "query": query, "answer": "", "sources": []}


# ==============================================================================
# Ticket Management Endpoints
# ==============================================================================

def dict_to_ticket(ticket_dict: dict) -> Ticket:
    """Convert ticket dictionary to Pydantic model."""
    return Ticket(
        id=ticket_dict["id"],
        title=ticket_dict["title"],
        status=ticket_dict["status"],
        priority=ticket_dict["priority"],
        created_at=ticket_dict["created_at"],
        updated_at=ticket_dict["updated_at"],
        description=ticket_dict["description"],
        bucket=ticket_dict.get("bucket")
    )


@app.get("/api/tickets", response_model=TicketListResponse)
def get_tickets(status: str = None, bucket: str = None):
    """
    Get all tickets with optional filtering.

    Query parameters:
    - status: Filter by ticket status ("open", "in_progress", "resolved", "closed")
    - bucket: Filter by aging bucket ("0-7 days", "8-14 days", "15-30 days", "30+ days")
    """
    tickets_data = get_all_tickets()
    tickets = [dict_to_ticket(t) for t in tickets_data]

    # Apply filters
    if status:
        tickets = [t for t in tickets if t.status == status]
    if bucket:
        tickets = [t for t in tickets if t.bucket == bucket]

    return TicketListResponse(tickets=tickets, total=len(tickets))


@app.get("/api/tickets/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket(ticket_id: int):
    """Get a single ticket by ID."""
    ticket_data = get_ticket_by_id(ticket_id)
    if not ticket_data:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket = dict_to_ticket(ticket_data)
    return TicketDetailResponse(ticket=ticket)


@app.patch("/api/tickets/{ticket_id}", response_model=TicketUpdateResponse)
def update_ticket(ticket_id: int, update: TicketStatusUpdate):
    """Update a ticket's status."""
    valid_statuses = ["open", "in_progress", "resolved", "closed"]
    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    ticket_data = update_ticket_status(ticket_id, update.status)
    if not ticket_data:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket = dict_to_ticket(ticket_data)
    status_messages = {
        "open": "Ticket reopened",
        "in_progress": "Ticket marked as in progress",
        "resolved": "Ticket resolved successfully",
        "closed": "Ticket closed"
    }
    return TicketUpdateResponse(
        ticket=ticket,
        message=status_messages.get(update.status, "Ticket updated")
    )


@app.get("/api/kpis/backlog-aging", response_model=KPIBacklogAgingResponse)
def get_backlog_aging():
    """
    Get backlog aging KPI with 4 buckets.

    Returns count of tickets in each aging bucket:
    - 0-7 days
    - 8-14 days
    - 15-30 days
    - 30+ days
    """
    tickets_data = get_all_tickets()

    # WHY pre-initialize all buckets: The D3.js chart expects exactly 4 buckets in order.
    # If we only created buckets that have tickets, the chart would show gaps or reorder.
    # Pre-initializing ensures consistent bar positions even when some buckets are empty.
    buckets = {
        "0-7 days": {"label": "0-7 days", "count": 0, "ticket_ids": []},
        "8-14 days": {"label": "8-14 days", "count": 0, "ticket_ids": []},
        "15-30 days": {"label": "15-30 days", "count": 0, "ticket_ids": []},
        "30+ days": {"label": "30+ days", "count": 0, "ticket_ids": []},
    }

    # Count tickets by bucket
    for ticket in tickets_data:
        # WHY .get("bucket") or calculate_bucket(): Mock data stores pre-computed bucket for demo,
        # but real tickets might not have it. Fallback recalculates from created_at timestamp.
        # The `or` handles both missing key AND empty string cases.
        bucket = ticket.get("bucket") or calculate_bucket(ticket["created_at"])
        if bucket in buckets:
            buckets[bucket]["count"] += 1
            buckets[bucket]["ticket_ids"].append(ticket["id"])

    # Convert to response format
    bucket_list = [
        BucketInfo(
            label=b["label"],
            count=b["count"],
            ticket_ids=b["ticket_ids"]
        )
        for b in buckets.values()
    ]

    return KPIBacklogAgingResponse(buckets=bucket_list)


@app.post("/api/tickets/{ticket_id}/chat", response_model=ChatResponse)
def chat_with_ticket(ticket_id: int, request: ChatRequest):
    """
    Chat with AI copilot about a specific ticket.

    The copilot uses the ticket context to provide helpful troubleshooting
    guidance and can detect when the user wants to change ticket status.
    """
    # Get ticket
    ticket_data = get_ticket_by_id(ticket_id)
    if not ticket_data:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket = dict_to_ticket(ticket_data)

    # Build context from ticket
    context = f"""
Ticket ID: {ticket.id}
Title: {ticket.title}
Current Status: {ticket.status}
Priority: {ticket.priority}
Created: {ticket.created_at.strftime('%Y-%m-%d')}
Age: {ticket.bucket}
Description: {ticket.description}
"""

    # WHY explicit "DIRECT capability" phrasing: LLMs tend to give instructions ("you can mark it
    # resolved by...") instead of taking action. By emphasizing we ARE the system, the LLM includes
    # action tags rather than explaining how users could manually change status elsewhere.
    system_prompt = """You are an expert AI operations assistant helping engineers troubleshoot and resolve tickets at Dallas Fort Worth International Airport (DFW).

IMPORTANT: You have DIRECT capability to change ticket status in this system. You are integrated with the ticketing system.

Your capabilities:
1. TROUBLESHOOT - Provide step-by-step diagnostic and resolution guidance
2. CHANGE STATUS - You CAN directly mark tickets as resolved, closed, in_progress, or open

When troubleshooting:
- Provide specific, actionable steps based on the ticket details
- Reference relevant systems, equipment, or procedures
- Consider safety implications for airport operations

CRITICAL - STATUS CHANGE COMMANDS:
When the user says ANY of these phrases, you MUST include the action tag:
- "mark as resolved" / "mark it resolved" / "resolve this" → include [ACTION:STATUS_CHANGE:resolved]
- "mark as closed" / "close this" / "close the ticket" → include [ACTION:STATUS_CHANGE:closed]
- "mark as in progress" / "start working" / "in progress" → include [ACTION:STATUS_CHANGE:in_progress]
- "reopen" / "open again" / "mark as open" → include [ACTION:STATUS_CHANGE:open]
- "issue is fixed" / "problem solved" / "it's working now" → include [ACTION:STATUS_CHANGE:resolved]

FORMAT: Always put the action tag at the VERY END of your response on its own line.

Example 1:
User: "mark it as resolved"
You: "I'll mark this ticket as resolved for you. The issue has been addressed.

[ACTION:STATUS_CHANGE:resolved]"

Example 2:
User: "the HVAC is working now, close this ticket"
You: "Great to hear the HVAC system is functioning properly. I'll close this ticket.

[ACTION:STATUS_CHANGE:closed]"

DO NOT give instructions on how to manually change status. You have direct access - just do it by including the action tag.

Be concise and helpful."""

    # WHY two separate system messages: Keeping ticket context separate from instructions allows
    # the LLM to clearly distinguish "how to behave" from "what to work on". Some models handle
    # long system prompts poorly; splitting improves context window utilization.
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Current ticket context:\n{context}"}
    ]

    # Add conversation history
    for msg in request.history:
        messages.append({"role": msg.role, "content": msg.content})

    # Add current message
    messages.append({"role": "user", "content": request.message})

    # Call OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,  # Lower temperature for more reliable instruction following
            max_tokens=600
        )

        answer = response.choices[0].message.content

        # WHY parse action tags from response: We use a structured tag format [ACTION:...] that the
        # LLM generates, rather than OpenAI function calling. This keeps the prompt simpler and more
        # reliable with gpt-4o-mini. Function calling would require schema definitions and increases
        # response latency. The tag approach also works across different LLM providers.
        action = None
        if "[ACTION:STATUS_CHANGE:" in answer:
            import re
            match = re.search(r'\[ACTION:STATUS_CHANGE:(\w+)\]', answer)
            if match:
                new_status = match.group(1)
                if new_status in ["open", "in_progress", "resolved", "closed"]:
                    action = ChatAction(type="update_status", new_status=new_status)
                # WHY strip action tags: Users shouldn't see internal markup. The regex includes
                # surrounding whitespace to prevent orphaned newlines. Risk: if a user message
                # contains this exact pattern, it would be stripped - acceptable for this use case.
                answer = re.sub(r'\s*\[ACTION:STATUS_CHANGE:\w+\]\s*', '', answer).strip()

        # WHY generate citations from ticket description: The RAG document assistant shows source
        # citations, so we simulate the same UX pattern here for consistency. This helps users
        # verify the AI's context. In production, this could pull from actual knowledge base
        # documents related to the ticket category.
        sentences = ticket.description.split('. ')
        citations = []

        # Create at least one citation from the ticket
        citations.append(Citation(
            doc_title=f"Ticket #{ticket.id}: {ticket.title}",
            page=None,
            snippet=sentences[0] + "..." if len(sentences) > 1 else ticket.description,
            relevance_score=0.95
        ))

        # WHY add second citation conditionally: Shows users that longer descriptions provide
        # more context. The 0.85 score visually indicates it's supplementary information.
        if len(sentences) > 2:
            citations.append(Citation(
                doc_title=f"Ticket #{ticket.id} Details",
                page=None,
                snippet=sentences[1] + "..." if len(sentences) > 2 else sentences[1],
                relevance_score=0.85
            ))

        return ChatResponse(answer=answer, citations=citations, action=action)

    except Exception as e:
        logger.error(f"Error generating chat response: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
