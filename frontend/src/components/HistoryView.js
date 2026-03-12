import React from "react";

function HistoryView({ history, histLoading }) {
  return (
    <section className="panel mainPanel">
      <div className="historyViewHeader">
        <h2>Prediction History</h2>
      </div>

      <div className="historyCard">
        {histLoading ? <p>Loading...</p> : history.length === 0 ? <p>No predictions yet.</p> : (
          <table className="historyTable">
            <thead>
              <tr>
                <th>#</th>
                <th>Distance</th>
                <th>TTC</th>
                <th>Rel. Velocity</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {history.map((row) => (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td>{row.distance.toFixed(1)} m</td>
                  <td>{row.ttc === null ? "N/A" : `${row.ttc.toFixed(2)} s`}</td>
                  <td>{row.relative_velocity.toFixed(1)} m/s</td>
                  <td>{row.predicted_status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}

export default HistoryView;
