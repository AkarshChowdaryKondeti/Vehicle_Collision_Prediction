import React from "react";
import { STATUS_COLORS, STATUS_ORDER, normalizeStatus } from "./statusConfig";

function ChartFrame({ title, children }) {
  return (
    <div className="chartCard">
      <div className="chartTitle">{title}</div>
      {children}
    </div>
  );
}

function EmptyChart({ text }) {
  return <div className="chartEmpty">{text}</div>;
}

function PieChart({ counts, total }) {
  if (!total) {
    return <EmptyChart text="No prediction data available." />;
  }

  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  return (
    <div className="chartWrap pieWrap">
      <svg viewBox="0 0 220 220" className="pieChart" aria-label="Status distribution">
        <g transform="translate(110 110) rotate(-90)">
          {STATUS_ORDER.map((status) => {
            const value = counts[status] || 0;
            if (!value) {
              return null;
            }
            const segment = (value / total) * circumference;
            const circle = (
              <circle
                key={status}
                cx="0"
                cy="0"
                r={radius}
                fill="none"
                stroke={STATUS_COLORS[status]}
                strokeWidth="26"
                strokeDasharray={`${segment} ${circumference - segment}`}
                strokeDashoffset={-offset}
              />
            );
            offset += segment;
            return circle;
          })}
        </g>
        <text x="110" y="102" textAnchor="middle" className="chartCenterValue">
          {total}
        </text>
        <text x="110" y="124" textAnchor="middle" className="chartCenterLabel">
          Records
        </text>
      </svg>
      <div className="chartLegend">
        {STATUS_ORDER.map((status) => (
          <div key={status} className="legendRow">
            <span className="legendDot" style={{ background: STATUS_COLORS[status] }} />
            <span>{status}</span>
            <strong>{counts[status] || 0}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

function SummaryCards({ counts, total }) {
  const dominantStatus = STATUS_ORDER.reduce((current, status) => (
    (counts[status] || 0) > (counts[current] || 0) ? status : current
  ), STATUS_ORDER[0]);
  const criticalCases = (counts["HIGH RISK"] || 0) + (counts.COLLIDED || 0);

  const cards = [
    { label: "Total Records", value: total, accent: "#102542" },
    { label: "Dominant Status", value: dominantStatus, accent: STATUS_COLORS[dominantStatus] },
    { label: "Critical Cases", value: criticalCases, accent: "#b71c1c" },
    { label: "Safe Cases", value: counts.SAFE || 0, accent: STATUS_COLORS.SAFE },
  ];

  return (
    <div className="summaryCards">
      {cards.map((card) => (
        <div key={card.label} className="summaryCard">
          <div className="summaryLabel">{card.label}</div>
          <div className="summaryValue" style={{ color: card.accent }}>
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
}

function StatusBreakdownTable({ counts, total }) {
  return (
    <div className="statsTableWrap">
      <table className="statsTable">
        <thead>
          <tr>
            <th>Status</th>
            <th>Count</th>
            <th>Percentage</th>
          </tr>
        </thead>
        <tbody>
          {STATUS_ORDER.map((status) => {
            const count = counts[status] || 0;
            const percentage = total ? ((count / total) * 100).toFixed(1) : "0.0";

            return (
              <tr key={status}>
                <td>
                  <span className="statsStatus">
                    <span
                      className="legendDot"
                      style={{ background: STATUS_COLORS[status] }}
                    />
                    {status}
                  </span>
                </td>
                <td>{count}</td>
                <td>{percentage}%</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function CriticalInsight({ counts, total }) {
  const criticalCases = (counts["HIGH RISK"] || 0) + (counts.COLLIDED || 0);
  const criticalPercent = total ? ((criticalCases / total) * 100).toFixed(1) : "0.0";
  const safeCases = counts.SAFE || 0;
  const riskCases = (counts.RISK || 0) + (counts["HIGH RISK"] || 0);

  return (
    <div className="insightPanel">
      <div className="insightHeading">Critical Case Insight</div>
      <div className="insightText">
        {criticalCases} of {total} records fall into critical conditions (`HIGH RISK` or
        `COLLIDED`), representing {criticalPercent}% of the recorded predictions.
      </div>
      <div className="insightMetrics">
        <div className="insightMetric">
          <span>Safe cases</span>
          <strong>{safeCases}</strong>
        </div>
        <div className="insightMetric">
          <span>Risk-related cases</span>
          <strong>{riskCases}</strong>
        </div>
        <div className="insightMetric">
          <span>Collided cases</span>
          <strong>{counts.COLLIDED || 0}</strong>
        </div>
      </div>
    </div>
  );
}

function StatisticsView({ history, histLoading }) {
  if (histLoading) {
    return (
      <section className="panel mainPanel">
        <div className="historyViewHeader">
          <h2>Statistics</h2>
          <p>Loading prediction statistics...</p>
        </div>
      </section>
    );
  }

  const counts = STATUS_ORDER.reduce((acc, status) => ({ ...acc, [status]: 0 }), {});
  const total = history.length;

  history.forEach((row) => {
    const normalizedStatus = normalizeStatus(row.predicted_status);
    if (normalizedStatus) {
      counts[normalizedStatus] += 1;
    }
  });

  return (
    <section className="panel mainPanel">
      <div className="historyViewHeader">
        <h2>Statistics</h2>
      </div>

      {total === 0 ? (
        <div className="historyCard">
          <p>No predictions available for statistics.</p>
        </div>
      ) : (
        <div className="statsLayout">
          <ChartFrame title="Pie Chart for Status Distribution">
            <PieChart counts={counts} total={total} />
          </ChartFrame>

          <ChartFrame title="Statistics Overview">
            <SummaryCards counts={counts} total={total} />
            <StatusBreakdownTable counts={counts} total={total} />
            <CriticalInsight counts={counts} total={total} />
          </ChartFrame>
        </div>
      )}
    </section>
  );
}

export default StatisticsView;
