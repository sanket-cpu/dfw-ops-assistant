/**
 * Dashboard Page
 * Shows Backlog Aging Chart and Tickets Table
 */
import { useState, useEffect } from "react";
import BacklogAgingChart from "../components/BacklogAgingChart";
import TicketsTable from "../components/TicketsTable";
import { getTickets, getBacklogAging } from "../api/client";
import type { Ticket, BucketInfo } from "../api/types";

export default function Dashboard() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [filteredTickets, setFilteredTickets] = useState<Ticket[]>([]);
  const [buckets, setBuckets] = useState<BucketInfo[]>([]);
  const [selectedBucket, setSelectedBucket] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    // Filter tickets when bucket selection changes
    if (selectedBucket) {
      const filtered = tickets.filter((t) => t.bucket === selectedBucket);
      setFilteredTickets(filtered);
    } else {
      setFilteredTickets(tickets);
    }
  }, [selectedBucket, tickets]);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [ticketsData, kpiData] = await Promise.all([
        getTickets(),
        getBacklogAging(),
      ]);

      setTickets(ticketsData.tickets);
      setFilteredTickets(ticketsData.tickets);
      setBuckets(kpiData.buckets);
    } catch (err) {
      setError("Failed to load data. Please try again.");
      console.error("Error loading dashboard data:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBucketClick = (bucket: string) => {
    // Toggle bucket selection
    setSelectedBucket((prev) => (prev === bucket ? null : bucket));
  };

  if (isLoading) {
    return (
      <div style={{ padding: "24px", textAlign: "center" }}>
        <h1 style={{ fontSize: "24px", fontWeight: "bold", marginBottom: "16px" }}>
          Loading...
        </h1>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "24px" }}>
        <div
          style={{
            padding: "16px",
            backgroundColor: "#FEE2E2",
            color: "#DC2626",
            borderRadius: "8px",
            border: "1px solid #FCA5A5",
          }}
        >
          {error}
          <button
            onClick={loadData}
            style={{
              marginLeft: "16px",
              padding: "8px 16px",
              backgroundColor: "#DC2626",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "24px", maxWidth: "1400px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "32px", fontWeight: "bold", marginBottom: "24px" }}>
        Ops Intelligence Copilot
      </h1>

      {/* Filter Info */}
      {selectedBucket && (
        <div
          style={{
            padding: "12px 16px",
            backgroundColor: "#EEF2FF",
            border: "1px solid #C7D2FE",
            borderRadius: "8px",
            marginBottom: "24px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span style={{ color: "#4F46E5", fontWeight: "500" }}>
            Filtered by: {selectedBucket}
          </span>
          <button
            onClick={() => setSelectedBucket(null)}
            style={{
              padding: "6px 12px",
              backgroundColor: "#4F46E5",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              fontSize: "14px",
              cursor: "pointer",
            }}
          >
            Clear Filter
          </button>
        </div>
      )}

      {/* Dashboard Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "600px 1fr",
          gap: "24px",
          marginBottom: "24px",
        }}
      >
        {/* Chart */}
        <div>
          <BacklogAgingChart data={buckets} onBucketClick={handleBucketClick} />
          <p
            style={{
              marginTop: "12px",
              fontSize: "14px",
              color: "#6b7280",
              textAlign: "center",
            }}
          >
            Click a bar to filter tickets
          </p>
        </div>

        {/* Summary Stats */}
        <div>
          <h2
            style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "16px" }}
          >
            Summary
          </h2>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "16px",
            }}
          >
            {buckets.map((bucket) => (
              <div
                key={bucket.label}
                style={{
                  padding: "16px",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  backgroundColor:
                    selectedBucket === bucket.label ? "#EEF2FF" : "#fff",
                  cursor: "pointer",
                }}
                onClick={() => handleBucketClick(bucket.label)}
              >
                <div
                  style={{
                    fontSize: "14px",
                    color: "#6b7280",
                    marginBottom: "8px",
                  }}
                >
                  {bucket.label}
                </div>
                <div
                  style={{
                    fontSize: "32px",
                    fontWeight: "bold",
                    color: "#4F46E5",
                  }}
                >
                  {bucket.count}
                </div>
                <div style={{ fontSize: "12px", color: "#9ca3af" }}>tickets</div>
              </div>
            ))}
          </div>

          <div
            style={{
              marginTop: "24px",
              padding: "16px",
              backgroundColor: "#F0FDF4",
              border: "1px solid #BBF7D0",
              borderRadius: "8px",
            }}
          >
            <div
              style={{
                fontSize: "14px",
                color: "#15803D",
                fontWeight: "600",
                marginBottom: "8px",
              }}
            >
              Total Backlog
            </div>
            <div style={{ fontSize: "40px", fontWeight: "bold", color: "#15803D" }}>
              {tickets.length}
            </div>
          </div>
        </div>
      </div>

      {/* Tickets Table */}
      <TicketsTable tickets={filteredTickets} />
    </div>
  );
}
