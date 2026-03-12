export const STATUS_THEME = {
  SAFE: { border: "#2e7d32", text: "#1b5e20", bg: "#edf7ed" },
  RISK: { border: "#d32f2f", text: "#8a1c1c", bg: "#fdecea" },
  "HIGH RISK": { border: "#b71c1c", text: "#7f0000", bg: "#ffebee" },
  COLLIDED: { border: "#4a148c", text: "#4a148c", bg: "#f3e5f5" },
};

export const STATUS_ORDER = ["SAFE", "RISK", "HIGH RISK", "COLLIDED"];

export const STATUS_COLORS = {
  SAFE: "#2e7d32",
  RISK: "#ef6c00",
  "HIGH RISK": "#c62828",
  COLLIDED: "#6a1b9a",
};

export function normalizeStatus(status) {
  const value = String(status || "").trim().toUpperCase();

  if (value === "SAFE") return "SAFE";
  if (value === "RISK") return "RISK";
  if (value === "HIGH RISK" || value === "HIGH_RISK" || value === "HIGHRISK") {
    return "HIGH RISK";
  }
  if (value === "COLLIDED" || value === "COLLISION") return "COLLIDED";
  return null;
}
