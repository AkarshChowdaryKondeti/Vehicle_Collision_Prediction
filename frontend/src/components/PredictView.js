import React from "react";
import { STATUS_THEME } from "./statusConfig";

function PredictView({
  form,
  loading,
  error,
  result,
  submittedData,
  onChange,
  onSubmit,
  onReset,
}) {
  const theme = result ? (STATUS_THEME[result.predicted_status] || STATUS_THEME.SAFE) : null;

  return (
    <section className="panel mainPanel">
      <div className="panelContent">
        <div className="panelColumn">
          <h2>Input</h2>
          <form onSubmit={onSubmit}>
            <div className="field">
              <label>Distance to Object (m)</label>
              <input
                type="number"
                name="distance"
                value={form.distance}
                onChange={onChange}
                placeholder="e.g. 15"
              />
            </div>

            <div className="field">
              <label>Relative Velocity (m/s)</label>
              <input
                type="number"
                name="relative_velocity"
                value={form.relative_velocity}
                onChange={onChange}
                placeholder="e.g. 10"
              />
            </div>

            {error && <div className="error">{error}</div>}

            <div className="buttonRow">
              <button type="submit" disabled={loading} className="button">
                {loading ? "Predicting..." : "Predict"}
              </button>
              <button type="button" onClick={onReset} className="resetButton">
                Reset
              </button>
            </div>
          </form>
        </div>

        <div className="panelColumn panelOutput">
          <h2>Output</h2>

          {!result && !loading && (
            <div className="placeholder">
              <p>Enter distance and relative velocity to generate a prediction.</p>
            </div>
          )}

          {loading && <div className="placeholder">Predicting...</div>}

          {result && theme && (
            <div
              className="statusBanner"
              style={{ background: theme.bg, border: `2px solid ${theme.border}` }}
            >
              <div>
                <div className="statusLabel" style={{ color: theme.text }}>
                  {result.predicted_status}
                </div>
                <div className="metricRow">
                  <span>Time To Collision</span>
                  <strong>{result.ttc === null ? "N/A" : `${result.ttc.toFixed(2)} s`}</strong>
                </div>
                <div className="messageText">{result.message}</div>
              </div>
            </div>
          )}

          {submittedData && (
            <div className="submittedData">
              <strong>Last Input</strong>
              <div>Distance: {submittedData.distance} m</div>
              <div>Relative Velocity: {submittedData.relative_velocity} m/s</div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export default PredictView;
