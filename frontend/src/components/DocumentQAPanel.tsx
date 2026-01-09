/**
 * RAG Document Q&A Chat Bubble
 * Bottom-right floating chat widget for DFW Airport documentation
 */
import { useState } from "react";
import { askDocument } from "../api/client";

// WHY local Message interface instead of importing from types: This component needs a sources
// array specific to RAG responses. The shared Message type (used in CopilotChat) doesn't have
// sources. Creating a local type avoids polluting shared types with domain-specific fields.
interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Array<{
    title: string;
    page: string;
    snippet: string;
  }>;
}

interface DocumentQAPanelProps {
  isOpen: boolean;
  onToggle: () => void;
}

export default function DocumentQAPanel({ isOpen, onToggle }: DocumentQAPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    // WHY clear input immediately: Provides instant UI feedback that the message was "sent".
    // If we waited for API response, slow networks would leave user uncertain whether click
    // registered. User message appears in chat immediately, reinforcing the action.
    setInputMessage("");
    setError(null);

    // Add user message
    const newMessages: Message[] = [...messages, { role: "user", content: userMessage }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const response = await askDocument(userMessage);

      // WHY check error field on 200 response: The RAG API returns HTTP 200 with error in body
      // for "soft" failures (no documents found, ChromaDB issues). This allows UI to show
      // partial results or graceful messages. Only network/server failures throw to catch block.
      if (response.error) {
        setError(response.error);
      } else {
        setMessages([
          ...newMessages,
          {
            role: "assistant",
            content: response.answer,
            sources: response.sources,
          },
        ]);
      }
    } catch (err) {
      setError("Failed to get response. Please try again.");
      console.error("Document Q&A error:", err);
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

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  // Chat bubble button (always visible)
  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        style={{
          position: "fixed",
          bottom: "24px",
          right: "24px",
          width: "64px",
          height: "64px",
          borderRadius: "50%",
          backgroundColor: "#4F46E5",
          color: "#fff",
          border: "none",
          cursor: "pointer",
          boxShadow: "0 4px 12px rgba(79, 70, 229, 0.4)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "28px",
          zIndex: 1000,
          transition: "transform 0.2s, box-shadow 0.2s",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = "scale(1.1)";
          e.currentTarget.style.boxShadow = "0 6px 16px rgba(79, 70, 229, 0.5)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = "scale(1)";
          e.currentTarget.style.boxShadow = "0 4px 12px rgba(79, 70, 229, 0.4)";
        }}
        title="Ask about DFW documentation"
      >
        {String.fromCodePoint(0x1F4AC)}
      </button>
    );
  }

  // Expanded chat panel
  return (
    <div
      style={{
        position: "fixed",
        bottom: "24px",
        right: "24px",
        width: "380px",
        height: "520px",
        backgroundColor: "#fff",
        borderRadius: "16px",
        boxShadow: "0 8px 32px rgba(0, 0, 0, 0.15)",
        display: "flex",
        flexDirection: "column",
        zIndex: 1000,
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "16px",
          backgroundColor: "#4F46E5",
          color: "#fff",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <div style={{ fontWeight: "bold", fontSize: "16px" }}>
            {String.fromCodePoint(0x1F4DA)} DFW Doc Assistant
          </div>
          <div style={{ fontSize: "12px", opacity: 0.9 }}>
            Ask about operations & design manuals
          </div>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button
            onClick={clearChat}
            style={{
              padding: "4px 8px",
              backgroundColor: "rgba(255,255,255,0.2)",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              fontSize: "11px",
              cursor: "pointer",
            }}
          >
            Clear
          </button>
          <button
            onClick={onToggle}
            style={{
              padding: "4px 10px",
              backgroundColor: "rgba(255,255,255,0.2)",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              fontSize: "16px",
              cursor: "pointer",
              lineHeight: 1,
            }}
          >
            {String.fromCodePoint(0x2715)}
          </button>
        </div>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "12px",
          backgroundColor: "#f9fafb",
        }}
      >
        {messages.length === 0 && (
          <div style={{ textAlign: "center", color: "#6b7280", marginTop: "40px", padding: "0 16px" }}>
            <div style={{ fontSize: "32px", marginBottom: "12px" }}>
              {String.fromCodePoint(0x1F4DA)}
            </div>
            <p style={{ marginBottom: "8px", fontSize: "14px" }}>
              Ask about DFW documentation
            </p>
            <div style={{ fontSize: "12px", color: "#9ca3af", lineHeight: "1.6" }}>
              <p style={{ fontStyle: "italic", margin: "4px 0" }}>
                "What are the HVAC requirements?"
              </p>
              <p style={{ fontStyle: "italic", margin: "4px 0" }}>
                "FOD inspection procedures?"
              </p>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              marginBottom: "12px",
              display: "flex",
              flexDirection: "column",
              alignItems: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div
              style={{
                padding: "10px 14px",
                borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                backgroundColor: msg.role === "user" ? "#4F46E5" : "#fff",
                color: msg.role === "user" ? "#fff" : "#374151",
                maxWidth: "85%",
                boxShadow: msg.role === "assistant" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
                fontSize: "14px",
                lineHeight: "1.5",
              }}
            >
              <div style={{ whiteSpace: "pre-wrap" }}>{msg.content}</div>

              {/* Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div
                  style={{
                    marginTop: "10px",
                    paddingTop: "10px",
                    borderTop: "1px solid #e5e7eb",
                    fontSize: "11px",
                  }}
                >
                  <div style={{ fontWeight: "600", color: "#6b7280", marginBottom: "6px" }}>
                    Sources:
                  </div>
                  {/* WHY slice(0, 2): Chat bubble has limited space (380px width). Showing all 3
                      retrieved sources would overflow. Two sources provide sufficient attribution
                      while keeping the UI compact. Full sources visible in API response for debugging. */}
                  {msg.sources.slice(0, 2).map((source, sIdx) => (
                    <div
                      key={sIdx}
                      style={{
                        marginBottom: "4px",
                        padding: "6px",
                        backgroundColor: "#f3f4f6",
                        borderRadius: "4px",
                      }}
                    >
                      <div style={{ fontWeight: "600", color: "#4B5563" }}>
                        {source.title}
                        {source.page && source.page !== "N/A" && ` (p.${source.page})`}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ display: "flex", alignItems: "flex-start" }}>
            <div
              style={{
                padding: "10px 14px",
                borderRadius: "16px 16px 16px 4px",
                backgroundColor: "#fff",
                color: "#6b7280",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                fontSize: "14px",
              }}
            >
              Searching documents...
            </div>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div
          style={{
            padding: "8px 12px",
            backgroundColor: "#FEE2E2",
            color: "#DC2626",
            fontSize: "12px",
          }}
        >
          {error}
        </div>
      )}

      {/* Input */}
      <div
        style={{
          padding: "12px",
          borderTop: "1px solid #e5e7eb",
          backgroundColor: "#fff",
        }}
      >
        <div style={{ display: "flex", gap: "8px" }}>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question..."
            disabled={isLoading}
            style={{
              flex: 1,
              padding: "10px 14px",
              border: "1px solid #e5e7eb",
              borderRadius: "20px",
              fontSize: "14px",
              outline: "none",
            }}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !inputMessage.trim()}
            style={{
              padding: "10px 16px",
              backgroundColor: isLoading || !inputMessage.trim() ? "#9CA3AF" : "#4F46E5",
              color: "#fff",
              border: "none",
              borderRadius: "20px",
              fontSize: "14px",
              fontWeight: "600",
              cursor: isLoading || !inputMessage.trim() ? "not-allowed" : "pointer",
            }}
          >
            {String.fromCodePoint(0x2191)}
          </button>
        </div>
      </div>
    </div>
  );
}
