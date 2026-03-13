import React, { useEffect, useState } from "react";
import StatusBadge from "./StatusBadge";
import { normalizeStatus } from "./statusConfig";

const RECORDS_PER_PAGE = 10;
const SORT_OPTIONS = [
  { value: "newest", label: "Newest" },
  { value: "oldest", label: "Oldest" },
  { value: "highest-ttc", label: "Highest TTC" },
  { value: "lowest-ttc", label: "Lowest TTC" },
];

function sortHistory(records, sortBy) {
  const sorted = [...records];

  sorted.sort((a, b) => {
    if (sortBy === "oldest") {
      return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
    }

    if (sortBy === "highest-ttc" || sortBy === "lowest-ttc") {
      const aTtc = a.ttc === null ? Number.POSITIVE_INFINITY : a.ttc;
      const bTtc = b.ttc === null ? Number.POSITIVE_INFINITY : b.ttc;
      return sortBy === "highest-ttc" ? bTtc - aTtc : aTtc - bTtc;
    }

    return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
  });

  return sorted;
}

function HistoryView({ history, histLoading }) {
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("All");
  const [sortBy, setSortBy] = useState("newest");

  const statusOptions = [
    "All",
    ...new Set(history.map((row) => normalizeStatus(row.predicted_status)).filter(Boolean)),
  ];
  const filteredHistory =
    statusFilter === "All"
      ? history
      : history.filter((row) => normalizeStatus(row.predicted_status) === statusFilter);
  const sortedHistory = sortHistory(filteredHistory, sortBy);

  useEffect(() => {
    setCurrentPage(1);
  }, [history, histLoading, statusFilter, sortBy]);

  const totalPages = Math.ceil(sortedHistory.length / RECORDS_PER_PAGE);
  const startIndex = (currentPage - 1) * RECORDS_PER_PAGE;
  const visibleHistory = sortedHistory.slice(startIndex, startIndex + RECORDS_PER_PAGE);
  const pageStart = sortedHistory.length === 0 ? 0 : startIndex + 1;
  const pageEnd = Math.min(startIndex + RECORDS_PER_PAGE, sortedHistory.length);

  return (
    <section className="panel mainPanel">
      <div className="historyViewHeader">
        <h2>Prediction History</h2>
        <div className="historyControls">
          <label className="historyFilter">
            <span>Status</span>
            <select
              className="historyFilterSelect"
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
            >
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
          <label className="historyFilter">
            <span>Sort</span>
            <select
              className="historyFilterSelect"
              value={sortBy}
              onChange={(event) => setSortBy(event.target.value)}
            >
              {SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="historyCard">
        {histLoading ? (
          <div className="tableSkeleton" aria-hidden="true">
            <div className="skeletonLine skeletonLineWide" />
            <div className="skeletonLine" />
            <div className="skeletonLine" />
            <div className="skeletonLine" />
          </div>
        ) : history.length === 0 ? (
          <div className="emptyState">
            <strong>No history yet</strong>
            <p>Prediction records will appear here after you run the first safety check.</p>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="emptyState">
            <strong>No matching records</strong>
            <p>Try another status filter to see more prediction history.</p>
          </div>
        ) : (
          <>
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
                {visibleHistory.map((row) => (
                  <tr key={row.id}>
                    <td>{row.id}</td>
                    <td>{row.distance.toFixed(1)} m</td>
                    <td>{row.ttc === null ? "N/A" : `${row.ttc.toFixed(2)} s`}</td>
                    <td>{row.relative_velocity.toFixed(1)} m/s</td>
                    <td>
                      <StatusBadge status={row.predicted_status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="historyPagination">
              <span className="historyPageInfo">
                Showing {pageStart}-{pageEnd} of {sortedHistory.length} records
              </span>

              {totalPages > 1 ? (
                <div className="historyPaginationActions">
                  <span className="historyPageInfo">
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    type="button"
                    className="historyPageButton"
                    onClick={() => setCurrentPage((page) => page - 1)}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </button>
                  <button
                    type="button"
                    className="historyPageButton"
                    onClick={() => setCurrentPage((page) => page + 1)}
                    disabled={currentPage === totalPages}
                  >
                    Next Page
                  </button>
                </div>
              ) : null}
            </div>
          </>
        )}
      </div>
    </section>
  );
}

export default HistoryView;
