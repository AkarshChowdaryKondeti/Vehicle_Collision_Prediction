import React from "react";
import { STATUS_THEME, normalizeStatus } from "./statusConfig";

function StatusBadge({ status }) {
  const normalizedStatus = normalizeStatus(status) || String(status || "UNKNOWN").toUpperCase();
  const theme = STATUS_THEME[normalizedStatus] || {
    border: "#94a3b8",
    text: "#334155",
    bg: "#f8fafc",
  };

  return (
    <span
      className="statusBadge"
      style={{
        "--status-border": theme.border,
        "--status-text": theme.text,
        "--status-bg": theme.bg,
      }}
    >
      {normalizedStatus}
    </span>
  );
}

export default StatusBadge;
