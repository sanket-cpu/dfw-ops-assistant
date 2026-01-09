/**
 * Copilot Chat Component with Citation Rendering and Status Actions
 */
import { useState } from "react";
import { chatWithTicket, updateTicketStatus } from "../api/client";
import type { Message, Citation, Ticket } from "../api/types";

interface CopilotChatProps {
  ticketId: number;
  currentStatus: string;
  onStatusChange?: (newStatus: string, updatedTicket: Ticket) => void;
}

export default function CopilotChat({ ticketId, currentStatus, onStatusChange }: CopilotChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // WHY separate pendingAction state: Creates a "confirmation buffer" between AI suggestion and
  // execution. User must explicitly click button to change status - prevents accidental changes
  // if AI misinterprets "resolved" in casual conversation vs. actual intent to close ticket.
  const [pendingAction, setPendingAction] = useState<{ type: string; new_status: string } | null>(null);
  // WHY separate isUpdatingStatus from isLoading: These are independent operations. User might
  // be updating status while a previous chat response is still being processed. Separate flags
  // allow correct button states for each action without blocking the other.
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  const handleSend = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setError(null);
    setPendingAction(null);

    // Add user message to UI
    const newMessages = [...messages, { role: "user" as const, content: userMessage }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const response = await chatWithTicket(ticketId, {
        message: userMessage,
        history: messages,
      });

      // Add assistant response
      setMessages([
        ...newMessages,
        { role: "assistant" as const, content: response.answer },
      ]);
      setCitations(response.citations);

      // Check for action
      if (response.action && response.action.type === "update_status" && response.action.new_status) {
        setPendingAction({
          type: response.action.type,
          new_status: response.action.new_status,
        });
      }
    } catch (err) {
      setError("Failed to get response. Please try again.");
      console.error("Chat error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStatusUpdate = async () => {
    if (!pendingAction || !pendingAction.new_status) return;

    setIsUpdatingStatus(true);
    try {
      console.log(`Updating ticket ${ticketId} to status: ${pendingAction.new_status}`);
      const response = await updateTicketStatus(ticketId, pendingAction.new_status);
      console.log("Update response:", response);

      // Notify parent component
      if (onStatusChange) {
        onStatusChange(pendingAction.new_status, response.ticket);
      }

      // Add confirmation message
      setMessages([
        ...messages,
        {
          role: "assistant" as const,
          content: `Ticket status updated to "${pendingAction.new_status}".`
        },
      ]);

      setPendingAction(null);
    } catch (err: any) {
      // WHY deeply nested error path: Axios wraps HTTP errors in response.data. FastAPI's
      // HTTPException puts message in "detail" field. This chain extracts user-friendly message
      // from API errors, falls back to JS error message, then to generic string. Each ?. prevents
      // crashes if structure differs (network error vs API error vs unknown).
      const errorMsg = err?.response?.data?.detail || err?.message || "Failed to update ticket status";
      setError(errorMsg);
      console.error("Status update error:", err);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "resolved": return "#10B981";
      case "closed": return "#6B7280";
      case "in_progress": return "#F59E0B";
      case "open": return "#EF4444";
      default: return "#6B7280";
    }
  };

  return (
    <div className="copilot-chat" style={{ marginTop: "24px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <h3 style={{ fontSize: "18px", fontWeight: "bold", margin: 0 }}>
          AI Troubleshooting Copilot
        </h3>
        <span style={{
          padding: "4px 12px",
          borderRadius: "12px",
          fontSize: "12px",
          fontWeight: "600",
          backgroundColor: getStatusColor(currentStatus) + "20",
          color: getStatusColor(currentStatus),
          textTransform: "uppercase",
        }}>
          {currentStatus}
        </span>
      </div>

      {/* Messages */}
      <div
        className="messages"
        style={{
          border: "1px solid #e5e7eb",
          borderRadius: "8px",
          padding: "16px",
          minHeight: "300px",
          maxHeight: "500px",
          overflowY: "auto",
          marginBottom: "16px",
          backgroundColor: "#f9fafb",
        }}
      >
        {messages.length === 0 && (
          <div style={{ color: "#6b7280", textAlign: "center", marginTop: "60px" }}>
            <p style={{ marginBottom: "12px", fontSize: "16px" }}>
              Ask the AI copilot to help troubleshoot this ticket...
            </p>
            <p style={{ fontSize: "13px", color: "#9ca3af" }}>
              Try: "What steps should I take to resolve this?" or "Mark as resolved"
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              marginBottom: "16px",
              padding: "12px",
              borderRadius: "8px",
              backgroundColor: msg.role === "user" ? "#EEF2FF" : "#fff",
              border: msg.role === "assistant" ? "1px solid #e5e7eb" : "none",
            }}
          >
            <div
              style={{
                fontWeight: "bold",
                marginBottom: "8px",
                color: msg.role === "user" ? "#4F46E5" : "#10B981",
              }}
            >
              {msg.role === "user" ? "You" : "AI Copilot"}
            </div>
            <div style={{ whiteSpace: "pre-wrap", lineHeight: "1.5" }}>{msg.content}</div>
          </div>
        ))}

        {isLoading && (
          <div
            style={{
              padding: "12px",
              borderRadius: "8px",
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              color: "#6b7280",
            }}
          >
            <div style={{ fontWeight: "bold", marginBottom: "8px", color: "#10B981" }}>
              AI Copilot
            </div>
            Analyzing ticket and generating recommendations...
          </div>
        )}
      </div>

      {/* WHY prominent green UI for resolved/closed: Closing a ticket is a "success" action that
          deserves celebration. The large green button makes it easy to click and provides strong
          visual feedback. Other status changes (in_progress, reopen) are less final, so they get
          a subtler purple box. This UX pattern guides users toward completing tickets. */}
      {pendingAction && (pendingAction.new_status === "resolved" || pendingAction.new_status === "closed") && (
        <div
          style={{
            marginBottom: "16px",
            padding: "20px",
            border: "2px solid #10B981",
            borderRadius: "12px",
            backgroundColor: "#ECFDF5",
            textAlign: "center",
          }}
        >
          <div style={{
            fontSize: "16px",
            fontWeight: "600",
            marginBottom: "16px",
            color: "#065F46",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px"
          }}>
            <span style={{ fontSize: "20px" }}>{String.fromCodePoint(0x2705)}</span>
            Ready to close this ticket?
          </div>
          <button
            onClick={handleStatusUpdate}
            disabled={isUpdatingStatus}
            style={{
              padding: "14px 48px",
              backgroundColor: isUpdatingStatus ? "#9CA3AF" : "#10B981",
              color: "#fff",
              border: "none",
              borderRadius: "8px",
              fontSize: "16px",
              fontWeight: "700",
              cursor: isUpdatingStatus ? "not-allowed" : "pointer",
              boxShadow: "0 4px 6px -1px rgba(16, 185, 129, 0.3)",
              transition: "all 0.2s",
              width: "100%",
              maxWidth: "300px",
            }}
          >
            {isUpdatingStatus ? "Closing..." : "CLOSE TICKET"}
          </button>
          <div style={{ marginTop: "12px" }}>
            <button
              onClick={() => setPendingAction(null)}
              disabled={isUpdatingStatus}
              style={{
                padding: "8px 16px",
                backgroundColor: "transparent",
                color: "#6B7280",
                border: "none",
                fontSize: "14px",
                cursor: "pointer",
                textDecoration: "underline",
              }}
            >
              Keep working on this ticket
            </button>
          </div>
        </div>
      )}

      {/* Other Status Changes - Standard action box */}
      {pendingAction && pendingAction.new_status !== "resolved" && pendingAction.new_status !== "closed" && (
        <div
          style={{
            marginBottom: "16px",
            padding: "16px",
            border: "2px solid #4F46E5",
            borderRadius: "8px",
            backgroundColor: "#EEF2FF",
          }}
        >
          <div style={{ fontWeight: "600", marginBottom: "12px", color: "#4F46E5" }}>
            Update Status
          </div>
          <p style={{ marginBottom: "12px", color: "#374151" }}>
            Change ticket status to <strong>"{pendingAction.new_status}"</strong>?
          </p>
          <div style={{ display: "flex", gap: "12px" }}>
            <button
              onClick={handleStatusUpdate}
              disabled={isUpdatingStatus}
              style={{
                padding: "10px 20px",
                backgroundColor: "#4F46E5",
                color: "#fff",
                border: "none",
                borderRadius: "6px",
                fontSize: "14px",
                fontWeight: "600",
                cursor: isUpdatingStatus ? "not-allowed" : "pointer",
                opacity: isUpdatingStatus ? 0.7 : 1,
              }}
            >
              {isUpdatingStatus ? "Updating..." : `Yes, mark as ${pendingAction.new_status}`}
            </button>
            <button
              onClick={() => setPendingAction(null)}
              disabled={isUpdatingStatus}
              style={{
                padding: "10px 20px",
                backgroundColor: "#fff",
                color: "#374151",
                border: "1px solid #d1d5db",
                borderRadius: "6px",
                fontSize: "14px",
                fontWeight: "500",
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Citations */}
      {citations.length > 0 && (
        <div
          className="citations"
          style={{
            marginBottom: "16px",
            padding: "16px",
            border: "1px solid #e5e7eb",
            borderRadius: "8px",
            backgroundColor: "#FFF7ED",
          }}
        >
          <h4 style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "12px" }}>
            Sources
          </h4>
          {citations.map((citation, idx) => (
            <div
              key={idx}
              className="citation"
              style={{
                marginBottom: "12px",
                padding: "12px",
                backgroundColor: "#fff",
                borderRadius: "6px",
                border: "1px solid #FED7AA",
              }}
            >
              <div
                className="citation-header"
                style={{
                  fontSize: "13px",
                  fontWeight: "600",
                  marginBottom: "8px",
                  color: "#EA580C",
                }}
              >
                {citation.doc_title}
                {citation.page && ` - Page ${citation.page}`}
              </div>
              <div
                className="citation-snippet"
                style={{
                  fontSize: "13px",
                  color: "#6b7280",
                  fontStyle: "italic",
                }}
              >
                "{citation.snippet}"
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          style={{
            padding: "12px",
            marginBottom: "16px",
            backgroundColor: "#FEE2E2",
            color: "#DC2626",
            borderRadius: "8px",
            border: "1px solid #FCA5A5",
          }}
        >
          {error}
        </div>
      )}

      {/* Input */}
      <div style={{ display: "flex", gap: "12px" }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask for troubleshooting help or say 'mark as resolved'..."
          disabled={isLoading}
          style={{
            flex: 1,
            padding: "12px",
            border: "1px solid #e5e7eb",
            borderRadius: "8px",
            fontSize: "14px",
          }}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !inputMessage.trim()}
          style={{
            padding: "12px 24px",
            backgroundColor: isLoading || !inputMessage.trim() ? "#9CA3AF" : "#4F46E5",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            fontSize: "14px",
            fontWeight: "600",
            cursor: isLoading || !inputMessage.trim() ? "not-allowed" : "pointer",
          }}
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}
