"""Database layer for Ops Intelligence Copilot."""
import os
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/tickets.db")
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class TicketDB(Base):
    """SQLAlchemy Ticket model."""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)


def init_db():
    """Initialize database with tables and mock data."""
    Base.metadata.create_all(bind=engine)

    # Check if data already exists
    db = SessionLocal()
    try:
        count = db.query(TicketDB).count()
        if count > 0:
            print(f"Database already initialized with {count} tickets")
            return

        # Create mock tickets across 4 aging buckets
        now = datetime.now()
        mock_tickets = [
            # Bucket 1: 0-7 days (5 tickets)
            TicketDB(
                title="Server latency spike in production",
                status="open",
                priority="high",
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(days=1),
                description="Production servers experiencing 200ms+ latency. Users reporting slow page loads."
            ),
            TicketDB(
                title="API rate limiting not working correctly",
                status="in_progress",
                priority="medium",
                created_at=now - timedelta(days=5),
                updated_at=now - timedelta(days=1),
                description="Rate limiting middleware allowing more requests than configured threshold."
            ),
            TicketDB(
                title="Dashboard charts not rendering on mobile",
                status="open",
                priority="low",
                created_at=now - timedelta(days=3),
                updated_at=now - timedelta(days=2),
                description="D3 charts fail to render properly on iOS Safari. Console shows viewport errors."
            ),
            TicketDB(
                title="Database backup job failing",
                status="open",
                priority="critical",
                created_at=now - timedelta(days=1),
                updated_at=now - timedelta(days=1),
                description="Automated backup cron job failing with permission errors on /backup directory."
            ),
            TicketDB(
                title="Update SSL certificates for staging environment",
                status="open",
                priority="medium",
                created_at=now - timedelta(days=6),
                updated_at=now - timedelta(days=4),
                description="SSL certs expire in 14 days. Need to renew Let's Encrypt certificates."
            ),

            # Bucket 2: 8-14 days (6 tickets)
            TicketDB(
                title="Memory leak in backend service",
                status="in_progress",
                priority="high",
                created_at=now - timedelta(days=10),
                updated_at=now - timedelta(days=2),
                description="Backend memory usage growing 100MB/hour. Service requires restart every 24h."
            ),
            TicketDB(
                title="Add dark mode to admin panel",
                status="open",
                priority="low",
                created_at=now - timedelta(days=12),
                updated_at=now - timedelta(days=8),
                description="Customer request: implement dark mode theme toggle for admin interface."
            ),
            TicketDB(
                title="Optimize database query performance",
                status="in_progress",
                priority="medium",
                created_at=now - timedelta(days=9),
                updated_at=now - timedelta(days=3),
                description="Several queries taking 5+ seconds. Need indexing and query optimization."
            ),
            TicketDB(
                title="Fix broken image uploads",
                status="open",
                priority="high",
                created_at=now - timedelta(days=8),
                updated_at=now - timedelta(days=6),
                description="Image upload endpoint returning 500 errors. Storage quota may be exceeded."
            ),
            TicketDB(
                title="Implement two-factor authentication",
                status="open",
                priority="medium",
                created_at=now - timedelta(days=14),
                updated_at=now - timedelta(days=10),
                description="Security requirement: add TOTP-based 2FA for admin accounts."
            ),
            TicketDB(
                title="Update dependencies to fix security vulnerabilities",
                status="open",
                priority="high",
                created_at=now - timedelta(days=11),
                updated_at=now - timedelta(days=9),
                description="npm audit showing 3 high severity vulnerabilities. Need dependency updates."
            ),

            # Bucket 3: 15-30 days (5 tickets)
            TicketDB(
                title="Migrate legacy authentication system",
                status="in_progress",
                priority="medium",
                created_at=now - timedelta(days=22),
                updated_at=now - timedelta(days=5),
                description="Migrate from custom auth to OAuth 2.0. 40% complete, blocked on user migration."
            ),
            TicketDB(
                title="Refactor monolithic service into microservices",
                status="open",
                priority="low",
                created_at=now - timedelta(days=28),
                updated_at=now - timedelta(days=20),
                description="Architecture improvement: split monolith into auth, api, and worker services."
            ),
            TicketDB(
                title="Fix email notification delivery issues",
                status="in_progress",
                priority="high",
                created_at=now - timedelta(days=18),
                updated_at=now - timedelta(days=4),
                description="Users not receiving password reset emails. SMTP configuration issue suspected."
            ),
            TicketDB(
                title="Add export to CSV feature",
                status="open",
                priority="low",
                created_at=now - timedelta(days=25),
                updated_at=now - timedelta(days=22),
                description="Feature request: allow users to export data tables as CSV files."
            ),
            TicketDB(
                title="Improve search functionality",
                status="open",
                priority="medium",
                created_at=now - timedelta(days=20),
                updated_at=now - timedelta(days=15),
                description="Search not returning relevant results. Consider implementing full-text search."
            ),

            # Bucket 4: 30+ days (6 tickets)
            TicketDB(
                title="Redesign landing page",
                status="open",
                priority="low",
                created_at=now - timedelta(days=45),
                updated_at=now - timedelta(days=40),
                description="Marketing request: modernize landing page design to improve conversion rates."
            ),
            TicketDB(
                title="Implement real-time analytics dashboard",
                status="open",
                priority="medium",
                created_at=now - timedelta(days=35),
                updated_at=now - timedelta(days=30),
                description="Add WebSocket-based real-time metrics visualization for ops team."
            ),
            TicketDB(
                title="Fix timezone handling in reports",
                status="open",
                priority="medium",
                created_at=now - timedelta(days=52),
                updated_at=now - timedelta(days=48),
                description="Reports showing incorrect timestamps. Need proper UTC/local timezone conversion."
            ),
            TicketDB(
                title="Add API versioning support",
                status="open",
                priority="low",
                created_at=now - timedelta(days=60),
                updated_at=now - timedelta(days=55),
                description="Implement versioned API endpoints to support backward compatibility."
            ),
            TicketDB(
                title="Performance testing and benchmarking",
                status="open",
                priority="low",
                created_at=now - timedelta(days=38),
                updated_at=now - timedelta(days=35),
                description="Establish baseline performance metrics and automated load testing."
            ),
            TicketDB(
                title="Documentation overhaul",
                status="in_progress",
                priority="low",
                created_at=now - timedelta(days=70),
                updated_at=now - timedelta(days=10),
                description="Comprehensive update of API documentation and developer guides."
            ),
        ]

        db.add_all(mock_tickets)
        db.commit()
        print(f"Initialized database with {len(mock_tickets)} mock tickets")
    finally:
        db.close()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_all_tickets(db: Session) -> List[TicketDB]:
    """Get all tickets."""
    return db.query(TicketDB).order_by(TicketDB.created_at.desc()).all()


def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[TicketDB]:
    """Get ticket by ID."""
    return db.query(TicketDB).filter(TicketDB.id == ticket_id).first()


def calculate_bucket(created_at: datetime) -> str:
    """Calculate aging bucket for a ticket."""
    days_old = (datetime.now() - created_at).days

    if days_old <= 7:
        return "0-7 days"
    elif days_old <= 14:
        return "8-14 days"
    elif days_old <= 30:
        return "15-30 days"
    else:
        return "30+ days"
