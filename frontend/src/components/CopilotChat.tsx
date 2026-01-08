/**
 * Copilot Chat Component with Citation Rendering
 */
import { useState } from "react";
import { chatWithTicket } from "../api/client";
import type { Message, Citation } from "../api/types";

interface CopilotChatProps {
  ticketId: number;
}

export default function CopilotChat({ ticketId }: CopilotChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setError(null);

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
    } catch (err) {
      setError("Failed to get response. Please try again.");
      console.error("Chat error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="copilot-chat" style={{ marginTop: "24px" }}>
      <h3 style={{ fontSize: "18px", fontWeight: "bold", marginBottom: "16px" }}>
        AI Copilot
      </h3>

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
          <p style={{ color: "#6b7280", textAlign: "center", marginTop: "100px" }}>
            Ask the AI copilot anything about this ticket...
          </p>
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
            <div style={{ whiteSpace: "pre-wrap" }}>{msg.content}</div>
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
            Thinking...
          </div>
        )}
      </div>

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
            📚 Sources
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
                📄 {citation.doc_title}
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
          placeholder="Ask about this ticket..."
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
