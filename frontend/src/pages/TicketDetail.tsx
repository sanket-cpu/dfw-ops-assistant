/**
 * Ticket Detail Page
 * Shows ticket information and Copilot chat
 */
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getTicket } from "../api/client";
import CopilotChat from "../components/CopilotChat";
import type { Ticket } from "../api/types";

export default function TicketDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    loadTicket(parseInt(id));
  }, [id]);

  const loadTicket = async (ticketId: number) => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getTicket(ticketId);
      setTicket(data.ticket);
    } catch (err) {
      setError("Failed to load ticket. Please try again.");
      console.error("Error loading ticket:", err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: "24px", textAlign: "center" }}>
        <h1 style={{ fontSize: "24px", fontWeight: "bold" }}>Loading...</h1>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div style={{ padding: "24px" }}>
        <button
          onClick={() => navigate("/")}
          style={{
            padding: "8px 16px",
            backgroundColor: "#4F46E5",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            marginBottom: "16px",
          }}
        >
          ← Back to Dashboard
        </button>
        <div
          style={{
            padding: "16px",
            backgroundColor: "#FEE2E2",
            color: "#DC2626",
            borderRadius: "8px",
            border: "1px solid #FCA5A5",
          }}
        >
          {error || "Ticket not found"}
        </div>
      </div>
    );
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical":
        return "#DC2626";
      case "high":
        return "#EA580C";
      case "medium":
        return "#D97706";
      case "low":
        return "#65A30D";
      default:
        return "#6B7280";
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case "open":
        return "#3B82F6";
      case "in_progress":
        return "#8B5CF6";
      case "resolved":
        return "#10B981";
      case "closed":
        return "#6B7280";
      default:
        return "#6B7280";
    }
  };

  return (
    <div style={{ padding: "24px", maxWidth: "1200px", margin: "0 auto" }}>
      {/* Header */}
      <button
        onClick={() => navigate("/")}
        style={{
          padding: "8px 16px",
          backgroundColor: "#4F46E5",
          color: "#fff",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
          marginBottom: "24px",
        }}
      >
        ← Back to Dashboard
      </button>

      {/* Ticket Info */}
      <div
        style={{
          padding: "24px",
          border: "1px solid #e5e7eb",
          borderRadius: "8px",
          backgroundColor: "#fff",
          marginBottom: "24px",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
          <div>
            <div style={{ fontSize: "14px", color: "#6b7280", marginBottom: "8px" }}>
              Ticket #{ticket.id}
            </div>
            <h1 style={{ fontSize: "28px", fontWeight: "bold", marginBottom: "16px" }}>
              {ticket.title}
            </h1>
          </div>
          <div style={{ display: "flex", gap: "12px" }}>
            <span
              style={{
                padding: "6px 12px",
                borderRadius: "6px",
                fontSize: "14px",
                fontWeight: "600",
                backgroundColor: getStatusBadgeColor(ticket.status) + "20",
                color: getStatusBadgeColor(ticket.status),
              }}
            >
              {ticket.status.replace("_", " ")}
            </span>
            <span
              style={{
                padding: "6px 12px",
                borderRadius: "6px",
                fontSize: "14px",
                fontWeight: "600",
                backgroundColor: getPriorityColor(ticket.priority) + "20",
                color: getPriorityColor(ticket.priority),
              }}
            >
              {ticket.priority}
            </span>
          </div>
        </div>

        {/* Metadata */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "16px",
            marginTop: "24px",
            paddingTop: "24px",
            borderTop: "1px solid #e5e7eb",
          }}
        >
          <div>
            <div style={{ fontSize: "12px", color: "#6b7280", marginBottom: "4px" }}>
              Created
            </div>
            <div style={{ fontSize: "14px", fontWeight: "500" }}>
              {new Date(ticket.created_at).toLocaleString()}
            </div>
          </div>
          <div>
            <div style={{ fontSize: "12px", color: "#6b7280", marginBottom: "4px" }}>
              Updated
            </div>
            <div style={{ fontSize: "14px", fontWeight: "500" }}>
              {new Date(ticket.updated_at).toLocaleString()}
            </div>
          </div>
          <div>
            <div style={{ fontSize: "12px", color: "#6b7280", marginBottom: "4px" }}>
              Age
            </div>
            <div style={{ fontSize: "14px", fontWeight: "500" }}>{ticket.bucket}</div>
          </div>
        </div>

        {/* Description */}
        <div style={{ marginTop: "24px" }}>
          <h3 style={{ fontSize: "16px", fontWeight: "bold", marginBottom: "12px" }}>
            Description
          </h3>
          <p style={{ color: "#374151", lineHeight: "1.6" }}>{ticket.description}</p>
        </div>
      </div>

      {/* Chat */}
      <div
        style={{
          padding: "24px",
          border: "1px solid #e5e7eb",
          borderRadius: "8px",
          backgroundColor: "#fff",
        }}
      >
        <CopilotChat ticketId={ticket.id} />
      </div>
    </div>
  );
}
