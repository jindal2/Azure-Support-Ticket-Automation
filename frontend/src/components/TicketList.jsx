import React, { useState } from 'react';
import { StatusBadge } from './StatusBadge';

export function TicketList({
  tickets,
  total,
  loading,
  error,
  selectedTicketId,
  onSelectTicket,
  onRefresh,
  filters,
  onFilterChange
}) {
  const [searchInput, setSearchInput] = useState(filters.search || '');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    onFilterChange({ ...filters, search: searchInput });
  };

  const handleClearFilters = () => {
    setSearchInput('');
    onFilterChange({
      search: '',
      category: '',
      priority: '',
      review_status: ''
    });
  };

  return (
    <div className="card ticket-list-card">
      <div className="card-header list-card-header">
        <div>
          <h3 className="card-title">Support Tickets ({total})</h3>
          <p className="card-description">Chronological list of all ingested tickets and review states</p>
        </div>
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={onRefresh}
          disabled={loading}
          title="Refresh ticket records"
        >
          {loading ? 'Refreshing...' : '↻ Refresh List'}
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="filter-bar">
        <form onSubmit={handleSearchSubmit} className="search-form">
          <input
            type="text"
            className="text-input search-input"
            placeholder="Search by ID, keyword, or summary..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
          <button type="submit" className="btn btn-secondary btn-sm">
            Search
          </button>
        </form>

        <div className="filter-dropdowns">
          <select
            className="select-input select-sm"
            value={filters.category || ''}
            onChange={(e) => onFilterChange({ ...filters, category: e.target.value })}
          >
            <option value="">All Categories</option>
            <option value="Billing">Billing</option>
            <option value="Technical">Technical</option>
            <option value="Access">Access</option>
            <option value="General">General</option>
          </select>

          <select
            className="select-input select-sm"
            value={filters.priority || ''}
            onChange={(e) => onFilterChange({ ...filters, priority: e.target.value })}
          >
            <option value="">All Priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            className="select-input select-sm"
            value={filters.review_status || ''}
            onChange={(e) => onFilterChange({ ...filters, review_status: e.target.value })}
          >
            <option value="">All Review Statuses</option>
            <option value="NEEDS_REVIEW">Needs Review</option>
            <option value="PENDING_REVIEW">Pending Review</option>
            <option value="READY">Ready</option>
            <option value="REJECTED">Rejected</option>
          </select>

          {(filters.search || filters.category || filters.priority || filters.review_status) && (
            <button
              type="button"
              className="btn-text"
              onClick={handleClearFilters}
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠</span>
          <div className="alert-content">Error loading tickets: {error}</div>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="table-loading-overlay">
          <div className="spinner-sm"></div>
          <span>Loading ticket records...</span>
        </div>
      )}

      {/* Empty state */}
      {!loading && (!tickets || tickets.length === 0) && (
        <div className="empty-state">
          <div className="empty-icon">🗂</div>
          <h4>No tickets found</h4>
          <p>No support tickets match the current filter criteria, or the database is empty.</p>
        </div>
      )}

      {/* Ticket Table */}
      {!loading && tickets && tickets.length > 0 && (
        <div className="table-responsive">
          <table className="ticket-table">
            <thead>
              <tr>
                <th>Ticket ID</th>
                <th>Category</th>
                <th>Priority</th>
                <th>Assigned Team</th>
                <th>Status</th>
                <th>Confidence</th>
                <th>Created</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((t) => {
                const isSelected = selectedTicketId === t.ticket_id;
                const formattedDate = new Date(t.created_at).toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                });

                return (
                  <tr
                    key={t.ticket_id}
                    className={`ticket-row ${isSelected ? 'row-selected' : ''}`}
                    onClick={() => onSelectTicket(t.ticket_id)}
                  >
                    <td>
                      <strong className="ticket-id-text">{t.ticket_id}</strong>
                    </td>
                    <td>
                      <StatusBadge type="category" value={t.predicted_category} />
                    </td>
                    <td>
                      <StatusBadge type="priority" value={t.priority} />
                    </td>
                    <td className="team-cell">{t.assigned_team}</td>
                    <td>
                      <StatusBadge type="status" value={t.review_status} />
                    </td>
                    <td>
                      <span className="conf-score">
                        {t.confidence_score !== null && t.confidence_score !== undefined
                          ? `${(t.confidence_score * 100).toFixed(0)}%`
                          : 'N/A'}
                      </span>
                    </td>
                    <td className="date-cell">{formattedDate}</td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-secondary btn-xs"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectTicket(t.ticket_id);
                        }}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
