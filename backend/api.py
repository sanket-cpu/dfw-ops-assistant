"""
DFW Operations Intelligence Copilot - Unified Backend API.

Combines RAG document assistant with ticket management and AI copilot.
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
from mock_data import get_all_tickets, get_ticket_by_id, calculate_bucket
from models import (
    Ticket, TicketListResponse, TicketDetailResponse,
    ChatRequest, ChatResponse, Citation,
    KPIBacklogAgingResponse, BucketInfo
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

    # Initialize buckets
    buckets = {
        "0-7 days": {"label": "0-7 days", "count": 0, "ticket_ids": []},
        "8-14 days": {"label": "8-14 days", "count": 0, "ticket_ids": []},
        "15-30 days": {"label": "15-30 days", "count": 0, "ticket_ids": []},
        "30+ days": {"label": "30+ days", "count": 0, "ticket_ids": []},
    }

    # Count tickets by bucket
    for ticket in tickets_data:
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

    The copilot uses the ticket context to provide relevant answers
    and citations from the ticket description.
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
Status: {ticket.status}
Priority: {ticket.priority}
Created: {ticket.created_at.strftime('%Y-%m-%d')}
Age: {ticket.bucket}
Description: {ticket.description}
"""

    # Build conversation history
    messages = [
        {
            "role": "system",
            "content": """You are an AI operations assistant helping engineers troubleshoot and resolve tickets at DFW Airport.
You have access to the ticket details and should provide helpful, actionable advice.
When referencing specific information from the ticket, cite it clearly.
Be concise and technical."""
        },
        {
            "role": "system",
            "content": f"Current ticket context:\n{context}"
        }
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
            temperature=0.7,
            max_tokens=500
        )

        answer = response.choices[0].message.content

        # Generate citations from ticket description
        sentences = ticket.description.split('. ')
        citations = []

        # Create at least one citation from the ticket
        citations.append(Citation(
            doc_title=f"Ticket #{ticket.id}: {ticket.title}",
            page=None,
            snippet=sentences[0] + "..." if len(sentences) > 1 else ticket.description,
            relevance_score=0.95
        ))

        # Add more citations if description is long enough
        if len(sentences) > 2:
            citations.append(Citation(
                doc_title=f"Ticket #{ticket.id} Details",
                page=None,
                snippet=sentences[1] + "..." if len(sentences) > 2 else sentences[1],
                relevance_score=0.85
            ))

        return ChatResponse(answer=answer, citations=citations)

    except Exception as e:
        logger.error(f"Error generating chat response: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
