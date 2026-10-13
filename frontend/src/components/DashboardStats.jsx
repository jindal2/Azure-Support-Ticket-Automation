import React from 'react';

export function DashboardStats({ metrics, loading, onRefresh }) {
  if (loading && !metrics) {
    return (
      <div className="stats-container stats-loading">
        <div className="spinner-sm"></div>
        <span>Loading metrics...</span>
      </div>
    );
  }

  const {
    total_tickets = 0,
    needs_review_count = 0,
    pending_review_count = 0,
    approved_count = 0,
    rejected_count = 0,
    categories = {},
    priorities = {}
  } = metrics || {};

  return (
    <div className="stats-section">
      <div className="stats-header">
        <h2 className="section-title">System Metrics & Processing Overview</h2>
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={onRefresh}
          title="Refresh metrics from backend"
        >
          ↻ Refresh Metrics
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Ingested</div>
          <div className="stat-value">{total_tickets}</div>
          <div className="stat-subtitle">All support tickets</div>
        </div>

        <div className="stat-card stat-alert">
          <div className="stat-label">Needs Review</div>
          <div className="stat-value text-amber">{needs_review_count}</div>
          <div className="stat-subtitle">Low confidence / Critical risk</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Pending Review</div>
          <div className="stat-value text-blue">{pending_review_count}</div>
          <div className="stat-subtitle">Awaiting agent sign-off</div>
        </div>

        <div className="stat-card stat-success">
          <div className="stat-label">Ready (Approved)</div>
          <div className="stat-value text-green">{approved_count}</div>
          <div className="stat-subtitle">Authorized customer drafts</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Rejected</div>
          <div className="stat-value text-red">{rejected_count}</div>
          <div className="stat-subtitle">Drafts sent back for revision</div>
        </div>
      </div>

      <div className="breakdown-grid">
        <div className="breakdown-card">
          <h4 className="breakdown-title">Category Breakdown</h4>
          <div className="pill-list">
            <span className="pill">Billing: <strong>{categories.Billing || 0}</strong></span>
            <span className="pill">Technical: <strong>{categories.Technical || 0}</strong></span>
            <span className="pill">Access: <strong>{categories.Access || 0}</strong></span>
            <span className="pill">General: <strong>{categories.General || 0}</strong></span>
          </div>
        </div>

        <div className="breakdown-card">
          <h4 className="breakdown-title">Priority Distribution</h4>
          <div className="pill-list">
            <span className="pill pill-crit">Critical: <strong>{priorities.CRITICAL || 0}</strong></span>
            <span className="pill pill-high">High: <strong>{priorities.HIGH || 0}</strong></span>
            <span className="pill pill-med">Medium: <strong>{priorities.MEDIUM || 0}</strong></span>
            <span className="pill pill-low">Low: <strong>{priorities.LOW || 0}</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
}
