/**
 * Toast Notification Component
 */
import { useEffect } from "react";

interface ToastProps {
  message: string;
  type: "success" | "error" | "info";
  isVisible: boolean;
  onClose: () => void;
  duration?: number;
}

export default function Toast({ message, type, isVisible, onClose, duration = 3000 }: ToastProps) {
  useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onClose]);

  if (!isVisible) return null;

  const bgColor = {
    success: "#10B981",
    error: "#EF4444",
    info: "#3B82F6",
  }[type];

  const icon = {
    success: String.fromCodePoint(0x2705),
    error: String.fromCodePoint(0x274C),
    info: String.fromCodePoint(0x2139),
  }[type];

  return (
    <div
      style={{
        position: "fixed",
        top: "24px",
        right: "24px",
        padding: "16px 24px",
        backgroundColor: bgColor,
        color: "#fff",
        borderRadius: "8px",
        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
        display: "flex",
        alignItems: "center",
        gap: "12px",
        zIndex: 2000,
        animation: "slideIn 0.3s ease",
        fontSize: "15px",
        fontWeight: "500",
      }}
    >
      <span style={{ fontSize: "18px" }}>{icon}</span>
      <span>{message}</span>
      <button
        onClick={onClose}
        style={{
          marginLeft: "8px",
          padding: "4px 8px",
          backgroundColor: "rgba(255,255,255,0.2)",
          color: "#fff",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
          fontSize: "14px",
        }}
      >
        {String.fromCodePoint(0x2715)}
      </button>
      <style>
        {`
          @keyframes slideIn {
            from {
              transform: translateX(100%);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
        `}
      </style>
    </div>
  );
}
