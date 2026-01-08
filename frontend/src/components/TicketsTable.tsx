/**
 * Tickets Table Component
 */
import { useNavigate } from "react-router-dom";
import type { Ticket } from "../api/types";

interface TicketsTableProps {
  tickets: Ticket[];
}

export default function TicketsTable({ tickets }: TicketsTableProps) {
  const navigate = useNavigate();

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
    <div className="table-container">
      <h2 style={{ marginBottom: "20px", fontSize: "20px", fontWeight: "bold" }}>
        Tickets ({tickets.length})
      </h2>
      <div style={{ overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            border: "1px solid #e5e7eb",
            borderRadius: "8px",
          }}
        >
          <thead>
            <tr style={{ backgroundColor: "#f9fafb" }}>
              <th style={{ padding: "12px", textAlign: "left", borderBottom: "2px solid #e5e7eb" }}>
                ID
              </th>
              <th style={{ padding: "12px", textAlign: "left", borderBottom: "2px solid #e5e7eb" }}>
                Title
              </th>
              <th style={{ padding: "12px", textAlign: "left", borderBottom: "2px solid #e5e7eb" }}>
                Status
              </th>
              <th style={{ padding: "12px", textAlign: "left", borderBottom: "2px solid #e5e7eb" }}>
                Priority
              </th>
              <th style={{ padding: "12px", textAlign: "left", borderBottom: "2px solid #e5e7eb" }}>
                Age
              </th>
              <th style={{ padding: "12px", textAlign: "left", borderBottom: "2px solid #e5e7eb" }}>
                Created
              </th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((ticket) => (
              <tr
                key={ticket.id}
                onClick={() => navigate(`/ticket/${ticket.id}`)}
                style={{
                  cursor: "pointer",
                  backgroundColor: "#fff",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = "#f9fafb";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = "#fff";
                }}
              >
                <td style={{ padding: "12px", borderBottom: "1px solid #e5e7eb" }}>
                  #{ticket.id}
                </td>
                <td style={{ padding: "12px", borderBottom: "1px solid #e5e7eb" }}>
                  {ticket.title}
                </td>
                <td style={{ padding: "12px", borderBottom: "1px solid #e5e7eb" }}>
                  <span
                    style={{
                      padding: "4px 8px",
                      borderRadius: "4px",
                      fontSize: "12px",
                      fontWeight: "500",
                      backgroundColor: getStatusBadgeColor(ticket.status) + "20",
                      color: getStatusBadgeColor(ticket.status),
                    }}
                  >
                    {ticket.status.replace("_", " ")}
                  </span>
                </td>
                <td
                  style={{
                    padding: "12px",
                    borderBottom: "1px solid #e5e7eb",
                    color: getPriorityColor(ticket.priority),
                    fontWeight: "500",
                  }}
                >
                  {ticket.priority}
                </td>
                <td style={{ padding: "12px", borderBottom: "1px solid #e5e7eb" }}>
                  {ticket.bucket}
                </td>
                <td style={{ padding: "12px", borderBottom: "1px solid #e5e7eb" }}>
                  {new Date(ticket.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
