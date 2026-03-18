import React, { useEffect, useMemo, useState } from "react";
import StatusBadge from "./StatusBadge";
import { normalizeStatus } from "./statusConfig";

const RECORDS_PER_PAGE = 10;
const SORT_OPTIONS = [
  { value: "sort:newest", label: "Newest First" },
  { value: "sort:oldest", label: "Oldest First" },
  { value: "preset:today", label: "Today" },
  { value: "preset:yesterday", label: "Yesterday" },
  { value: "preset:last-7-days", label: "Last 7 Days" },
  { value: "preset:this-month", label: "This Month" },
];

function getDateValue(timestamp) {
  const date = new Date(timestamp);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function sortHistory(records, sortBy) {
  const sorted = [...records];

  sorted.sort((a, b) => {
    const aTime = new Date(a.timestamp).getTime();
    const bTime = new Date(b.timestamp).getTime();
    return sortBy === "oldest" ? aTime - bTime : bTime - aTime;
  });

  return sorted;
}

function matchesDatePreset(timestamp, preset) {
  if (!preset) {
    return true;
  }

  const recordDate = new Date(timestamp);
  const today = new Date();
  const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const recordStart = new Date(
    recordDate.getFullYear(),
    recordDate.getMonth(),
    recordDate.getDate(),
  );

  if (preset === "today") {
    return recordStart.getTime() === todayStart.getTime();
  }

  if (preset === "yesterday") {
    const yesterdayStart = new Date(todayStart);
    yesterdayStart.setDate(yesterdayStart.getDate() - 1);
    return recordStart.getTime() === yesterdayStart.getTime();
  }

  if (preset === "last-7-days") {
    const last7Start = new Date(todayStart);
    last7Start.setDate(last7Start.getDate() - 6);
    return recordStart >= last7Start && recordStart <= todayStart;
  }

  if (preset === "this-month") {
    return (
      recordDate.getFullYear() === today.getFullYear() &&
      recordDate.getMonth() === today.getMonth()
    );
  }

  return true;
}

function HistoryView({ history, histLoading }) {
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("All");
  const [sortSelection, setSortSelection] = useState("sort:newest");

  const statusOptions = [
    "All",
    ...new Set(history.map((row) => normalizeStatus(row.predicted_status)).filter(Boolean)),
  ];

  const selectedPreset = sortSelection.startsWith("preset:") ? sortSelection.slice(7) : "";
  const sortBy = sortSelection === "sort:oldest" ? "oldest" : "newest";

  const filteredHistory = useMemo(() => {
    return history.filter((row) => {
      const matchesStatus =
        statusFilter === "All" || normalizeStatus(row.predicted_status) === statusFilter;
      const matchesPreset = matchesDatePreset(row.timestamp, selectedPreset);
      return matchesStatus && matchesPreset;
    });
  }, [history, selectedPreset, statusFilter]);

  const sortedHistory = useMemo(() => sortHistory(filteredHistory, sortBy), [filteredHistory, sortBy]);

  useEffect(() => {
    setCurrentPage(1);
  }, [history, histLoading, sortSelection, statusFilter]);

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
              value={sortSelection}
              onChange={(event) => setSortSelection(event.target.value)}
            >
              <optgroup label="Order">
                {SORT_OPTIONS.filter((option) => option.value.startsWith("sort:")).map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Date Range">
                {SORT_OPTIONS.filter((option) => option.value.startsWith("preset:")).map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </optgroup>
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
            <p>Try another status or sort selection.</p>
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
