"""Ops Intelligence Copilot - Backend API."""
import os
from typing import List
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from openai import OpenAI

from models import (
    Ticket, TicketListResponse, TicketDetailResponse,
    ChatRequest, ChatResponse, Citation,
    KPIBacklogAgingResponse, BucketInfo
)
from database import (
    init_db, get_db, get_all_tickets, get_ticket_by_id,
    calculate_bucket, TicketDB
)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI app
app = FastAPI(
    title="Ops Intelligence Copilot API",
    description="Backend API for ticket management and AI-powered operations assistance",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database with mock data."""
    init_db()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


def db_ticket_to_pydantic(db_ticket: TicketDB) -> Ticket:
    """Convert SQLAlchemy ticket to Pydantic model."""
    return Ticket(
        id=db_ticket.id,
        title=db_ticket.title,
        status=db_ticket.status,
        priority=db_ticket.priority,
        created_at=db_ticket.created_at,
        updated_at=db_ticket.updated_at,
        description=db_ticket.description,
        bucket=calculate_bucket(db_ticket.created_at)
    )


@app.get("/api/tickets", response_model=TicketListResponse)
def get_tickets(
    status: str = None,
    bucket: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all tickets with optional filtering.

    Query parameters:
    - status: Filter by ticket status
    - bucket: Filter by aging bucket ("0-7 days", "8-14 days", etc.)
    """
    tickets_db = get_all_tickets(db)
    tickets = [db_ticket_to_pydantic(t) for t in tickets_db]

    # Apply filters
    if status:
        tickets = [t for t in tickets if t.status == status]
    if bucket:
        tickets = [t for t in tickets if t.bucket == bucket]

    return TicketListResponse(tickets=tickets, total=len(tickets))


@app.get("/api/tickets/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Get a single ticket by ID."""
    ticket_db = get_ticket_by_id(db, ticket_id)
    if not ticket_db:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket = db_ticket_to_pydantic(ticket_db)
    return TicketDetailResponse(ticket=ticket)


@app.get("/api/kpis/backlog-aging", response_model=KPIBacklogAgingResponse)
def get_backlog_aging(db: Session = Depends(get_db)):
    """
    Get backlog aging KPI with 4 buckets.

    Returns count of tickets in each aging bucket:
    - 0-7 days
    - 8-14 days
    - 15-30 days
    - 30+ days
    """
    tickets_db = get_all_tickets(db)

    # Initialize buckets
    buckets = {
        "0-7 days": {"label": "0-7 days", "count": 0, "ticket_ids": []},
        "8-14 days": {"label": "8-14 days", "count": 0, "ticket_ids": []},
        "15-30 days": {"label": "15-30 days", "count": 0, "ticket_ids": []},
        "30+ days": {"label": "30+ days", "count": 0, "ticket_ids": []},
    }

    # Count tickets by bucket
    for ticket_db in tickets_db:
        bucket = calculate_bucket(ticket_db.created_at)
        buckets[bucket]["count"] += 1
        buckets[bucket]["ticket_ids"].append(ticket_db.id)

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
def chat_with_ticket(
    ticket_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat with AI copilot about a specific ticket.

    The copilot uses the ticket context to provide relevant answers
    and citations from the ticket description.
    """
    # Get ticket
    ticket_db = get_ticket_by_id(db, ticket_id)
    if not ticket_db:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket = db_ticket_to_pydantic(ticket_db)

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
            "content": """You are an AI operations assistant helping engineers troubleshoot and resolve tickets.
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
        # Split description into sentences for citation snippets
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
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
