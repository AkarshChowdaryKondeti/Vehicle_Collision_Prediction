import React, { useEffect, useState } from "react";
import "../styles/App.css";
import HistoryView from "./HistoryView";
import PredictView from "./PredictView";
import StatisticsView from "./StatisticsView";

const API_BASE = "http://localhost:8000";
const initialForm = { distance: "", relative_velocity: "" };

function App() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [submittedData, setSubmittedData] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeView, setActiveView] = useState("predict");
  const [histLoading, setHistLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "info") => {
    setToast({ message, type });
  };

  useEffect(() => {
    if (!toast) {
      return undefined;
    }

    const timer = window.setTimeout(() => {
      setToast(null);
    }, 3200);

    return () => window.clearTimeout(timer);
  }, [toast]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError(null);
  };

  const resetForm = () => {
    setForm(initialForm);
    setResult(null);
    setError(null);
    setSubmittedData(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    if (form.distance === "" || form.relative_velocity === "") {
      const message = "Distance and relative velocity are required.";
      setError(message);
      showToast(message, "error");
      setLoading(false);
      return;
    }

    const payload = {
      distance: parseFloat(form.distance),
      relative_velocity: parseFloat(form.relative_velocity),
    };

    try {
      const response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Prediction failed.");
      }

      const data = await response.json();
      setResult(data);
      setSubmittedData(payload);
      setForm(initialForm);
      showToast(`Prediction saved with status ${data.predicted_status}.`, "success");
    } catch (err) {
      setError(err.message);
      showToast(err.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (limit = null) => {
    setHistLoading(true);
    try {
      const historyUrl = limit === null ? `${API_BASE}/history` : `${API_BASE}/history?limit=${limit}`;
      const res = await fetch(historyUrl);
      if (!res.ok) {
        throw new Error("Unable to load prediction history.");
      }
      setHistory(await res.json());
    } catch {
      setHistory([]);
      showToast("Unable to load prediction history.", "error");
    } finally {
      setHistLoading(false);
    }
  };

  const switchView = (view) => {
    setActiveView(view);
    if (view === "history") {
      fetchHistory();
    } else if (view === "statistics") {
      fetchHistory();
    }
  };

  return (
    <div className="page">
      <header className="header">
        <h1>Vehicle Safety Prediction</h1>
      </header>

      {toast ? (
        <div className={`toast toast${toast.type[0].toUpperCase()}${toast.type.slice(1)}`}>
          {toast.message}
        </div>
      ) : null}

      <main className="dashboardSingle">
        <div className="viewSwitch">
          <button
            type="button"
            className={`viewTab ${activeView === "predict" ? "activeTab" : ""}`}
            onClick={() => switchView("predict")}
          >
            Predict
          </button>
          <button
            type="button"
            className={`viewTab ${activeView === "history" ? "activeTab" : ""}`}
            onClick={() => switchView("history")}
          >
            History
          </button>
          <button
            type="button"
            className={`viewTab ${activeView === "statistics" ? "activeTab" : ""}`}
            onClick={() => switchView("statistics")}
          >
            Statistics
          </button>
        </div>

        {activeView === "predict" ? (
          <PredictView
            form={form}
            loading={loading}
            error={error}
            result={result}
            submittedData={submittedData}
            onChange={handleChange}
            onSubmit={handleSubmit}
            onReset={resetForm}
          />
        ) : activeView === "history" ? (
          <HistoryView history={history} histLoading={histLoading} />
        ) : (
          <StatisticsView history={history} histLoading={histLoading} onToast={showToast} />
        )}
      </main>
    </div>
  );
}

export default App;