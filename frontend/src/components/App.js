// React hook for local component state management.
import React, { useState } from "react";
import "../styles/App.css";  // Importing the CSS file for styling

// Constants for API and Hidden Defaults
// Backend API base URL used by prediction and history calls.
const API_BASE = "http://localhost:8000";
// Hidden default sensor values not entered directly in the UI form.
const DEFAULTS = {
  axis: 0.1,
  speed: 60,
  steering_angle: 5,
};

// Status theme configuration
// Visual style and labels for each normalized prediction status.
const STATUS_THEME = {
  "SAFE": {
    bg: "#e8f5e9",
    border: "#43a047",
    text: "#1b5e20",
    label: "SAFE",
    emoji: "✅",
  },
  "RISK": {
    bg: "#fffde7",
    border: "#fdd835",
    text: "#7c5000",
    label: "RISK",
    emoji: "⚠️",
  },
  "HIGH RISK": {
    bg: "#ffebee",
    border: "#e53935",
    text: "#7f0000",
    label: "HIGH RISK",
    emoji: "🚨",
  },
};

// Normalize backend status variants into canonical keys used in UI.
const normalizeStatus = (status) => {
  if (!status) return "SAFE";
  const key = String(status).trim().toUpperCase();
  if (key === "WARNING") return "RISK";
  if (key === "DANGER") return "HIGH RISK";
  return key;
};

// Default form structure
// Controlled input defaults for the prediction form.
const initialForm = { distance: "", ttc: "", relative_velocity: "" };

// Instructions for each status
// Advisory text shown below prediction result card.
const INSTRUCTIONS = {
  "SAFE": "You are good to go! Keep driving safely.",
  "RISK": "Caution! Potential hazard detected, be prepared to slow down.",
  "HIGH RISK": "Immediate action required! Brake ASAP to avoid collision.",
};

function App() {
  // Form values for user-entered sensor inputs.
  const [form, setForm] = useState(initialForm);
  // Latest prediction response from backend.
  const [result, setResult] = useState(null);
  // Loading state for prediction request.
  const [loading, setLoading] = useState(false);
  // Error message shown on failed validation/request.
  const [error, setError] = useState(null);
  // Snapshot of payload sent for latest prediction.
  const [submittedData, setSubmittedData] = useState(null);
  // Cached prediction history list.
  const [history, setHistory] = useState([]);
  // Toggle for history panel visibility.
  const [showHistory, setShowHistory] = useState(false);
  // Loading state for history request.
  const [histLoading, setHistLoading] = useState(false);

  // Handle form input changes
  const handleChange = (e) => {
    // Update only changed field while preserving other inputs.
    setForm({ ...form, [e.target.name]: e.target.value });
    setError(null); // Reset error on input change
  };

  // Reset form to initial state
  const resetForm = () => {
    // Clear form and previous prediction state.
    setForm(initialForm);
    setResult(null);
    setError(null);
  };

  // Submit form and fetch prediction result
  const handleSubmit = async (e) => {
    // Stop browser default form submit/reload.
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    // Validate form fields
    if (!form.distance || !form.ttc || !form.relative_velocity) {
      setError("All fields are required.");
      setLoading(false);
      return;
    }

    const payload = {
      // Convert string inputs to numbers expected by backend schema.
      distance: parseFloat(form.distance),
      ttc: parseFloat(form.ttc),
      relative_velocity: parseFloat(form.relative_velocity),
      // Append hidden defaults for remaining model features.
      ...DEFAULTS,
    };

    try {
      // Send prediction request to backend API.
      const response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Prediction failed.");
      }

      const data = await response.json();
      // Store API output and submitted input snapshot.
      setResult(data);
      setSubmittedData(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch the prediction history
  const fetchHistory = async () => {
    setHistLoading(true);
    try {
      // Pull latest 20 prediction rows for history table.
      const res = await fetch(`${API_BASE}/history?limit=20`);
      setHistory(await res.json());
    } catch {
      setHistory([]);
    } finally {
      setHistLoading(false);
    }
  };

  const toggleHistory = () => {
    // Lazy-load history only when opening the panel first.
    if (!showHistory) fetchHistory();
    setShowHistory(!showHistory);
  };

  // Determine theme based on result status
  // Pick color/emojis by normalized prediction status.
  const theme = result ? STATUS_THEME[normalizeStatus(result.predicted_status)] : null;

  return (
    <div className="page">
      {/* Header */}
      <header className="header">
        <h1>Vehicle Safety Prediction</h1>
        <p>Real-time risk assessment based on sensor data</p>
      </header>

      <main className="main">
        {/* Input Form */}
        <section className="card">
          <h2>Enter Sensor Data</h2>

          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Distance to Object (m)</label>
              <input
                type="number"
                name="distance"
                value={form.distance}
                onChange={handleChange}
                placeholder="e.g. 15"
              />
            </div>

            <div className="field">
              <label>Time-to-Collision (s)</label>
              <input
                type="number"
                name="ttc"
                value={form.ttc}
                onChange={handleChange}
                placeholder="e.g. 1.8"
              />
            </div>

            <div className="field">
              <label>Relative Velocity (m/s)</label>
              <input
                type="number"
                name="relative_velocity"
                value={form.relative_velocity}
                onChange={handleChange}
                placeholder="e.g. -10"
              />
            </div>

            {error && <div className="error">{error}</div>}

            <div className="buttonRow">
              <button type="submit" disabled={loading} className="button">
                {loading ? "⏳  Analyzing..." : "🔍  Predict"}
              </button>
              <button type="button" onClick={resetForm} className="resetButton">
                Reset
              </button>
            </div>
          </form>
        </section>

        {/* Prediction Result */}
        <section className="card">
          <h2>Prediction Result</h2>

          {!result && !loading && (
            <div className="placeholder">
              <p>Submit sensor data to see the prediction result.</p>
            </div>
          )}

          {loading && <div className="placeholder">Analyzing data...</div>}

          {result && theme && (
            <div className="statusBanner" style={{ background: theme.bg, border: `2px solid ${theme.border}` }}>
              <div className="statusEmoji">{theme.emoji}</div>
              <div>
                <div className="statusLabel" style={{ color: theme.text }}>{theme.label}</div>
                <div>{result.message}</div>
              </div>
            </div>
          )}

          {/* Display Instructions */}
          {result && (
            <div className="instruction">
              <p>{INSTRUCTIONS[normalizeStatus(result.predicted_status)]}</p>
            </div>
          )}

          {submittedData && (
            <div className="submittedData">
              <strong>Submitted Values:</strong>
              <div>Distance: {submittedData.distance} m</div>
              <div>TTC: {submittedData.ttc} s</div>
              <div>Relative Velocity: {submittedData.relative_velocity} m/s</div>
            </div>
          )}
        </section>

        {/* Prediction History */}
        <section className="card">
          <button onClick={toggleHistory} className="historyButton">
            {showHistory ? "▲ Hide History" : "▼ Show History"}
          </button>

          {showHistory && (
            <div className="historyCard">
              {histLoading ? <p>Loading...</p> : history.length === 0 ? <p>No predictions yet.</p> : (
                <table className="historyTable">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Distance</th>
                      <th>TTC</th>
                      <th>Relative Velocity</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((row) => {
                      // Apply same status normalization and color mapping in table rows.
                      const normalizedStatus = normalizeStatus(row.predicted_status);
                      const t = STATUS_THEME[normalizedStatus] || STATUS_THEME.SAFE;
                      return (
                        <tr key={row.id}>
                          <td>{row.id}</td>
                          <td>{row.distance.toFixed(1)} m</td>
                          <td>{row.ttc.toFixed(2)} s</td>
                          <td>{row.relative_velocity.toFixed(1)} m/s</td>
                          <td style={{ background: t.bg, color: t.text }}>
                            {t.emoji} {normalizedStatus}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="footer">
        Vehicle Safety Prediction System · FastAPI + React · ML Project
      </footer>
    </div>
  );
}

export default App;
