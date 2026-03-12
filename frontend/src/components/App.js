import React, { useState } from "react";
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
      setError("Distance and relative velocity are required.");
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
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (limit = 20) => {
    setHistLoading(true);
    try {
      const res = await fetch(`${API_BASE}/history?limit=${limit}`);
      setHistory(await res.json());
    } catch {
      setHistory([]);
    } finally {
      setHistLoading(false);
    }
  };

  const switchView = (view) => {
    setActiveView(view);
    if (view === "history") {
      fetchHistory(20);
    } else if (view === "statistics") {
      fetchHistory(100);
    }
  };

  return (
    <div className="page">
      <header className="header">
        <h1>Vehicle Safety Prediction</h1>
      </header>

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
          <StatisticsView history={history} histLoading={histLoading} />
        )}
      </main>
    </div>
  );
}

export default App;
