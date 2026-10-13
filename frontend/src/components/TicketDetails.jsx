import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { StatusBadge } from './StatusBadge';
import { ReviewPanel } from './ReviewPanel';

export function TicketDetails({ ticketId, onClose, onTicketUpdated }) {
  const [ticket, setTicket] = useState(null);
  const [auditEvents, setAuditEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copyFeedback, setCopyFeedback] = useState(false);

  const fetchDetails = async () => {
    if (!ticketId) return;
    setLoading(true);
    setError(null);

    try {
      const [ticketData, auditData] = await Promise.all([
        api.getTicket(ticketId),
        api.getAuditHistory(ticketId)
      ]);
      setTicket(ticketData);
      setAuditEvents(auditData);
    } catch (err) {
      setError(err.message || 'Failed to load ticket details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [ticketId]);

  const handleCopyDraft = () => {
    if (!ticket?.draft_response) return;
    navigator.clipboard.writeText(ticket.draft_response);
    setCopyFeedback(true);
    setTimeout(() => setCopyFeedback(false), 2000);
  };

  const handleActionComplete = (updatedTicket) => {
    setTicket(updatedTicket);
    // Refresh audit history
    api.getAuditHistory(ticketId).then(setAuditEvents).catch(() => {});
    if (onTicketUpdated) {
      onTicketUpdated(updatedTicket);
    }
  };

  if (!ticketId) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-group">
            <span className="modal-subtitle">Ticket Inspector & Human Approval</span>
            <h2 className="modal-ticket-id">{ticketId}</h2>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close inspector modal"
          >
            ✕
          </button>
        </div>

        {loading && (
          <div className="modal-loading">
            <div className="spinner"></div>
            <p>Loading ticket intelligence and audit trail...</p>
          </div>
        )}

        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">⚠</span>
            <div className="alert-content">{error}</div>
          </div>
        )}

        {!loading && ticket && (
          <div className="modal-body">
            {/* Top metadata cards */}
            <div className="meta-card-grid">
              <div className="meta-card">
                <span className="meta-title">Review Status</span>
                <StatusBadge type="status" value={ticket.review_status} />
              </div>

              <div className="meta-card">
                <span className="meta-title">Priority</span>
                <StatusBadge type="priority" value={ticket.priority} />
              </div>

              <div className="meta-card">
                <span className="meta-title">Predicted Category</span>
                <StatusBadge type="category" value={ticket.predicted_category} />
              </div>

              <div className="meta-card">
                <span className="meta-title">Model Confidence</span>
                <span className="meta-value">
                  {ticket.confidence_score !== null
                    ? `${(ticket.confidence_score * 100).toFixed(1)}%`
                    : 'N/A'}
                  {ticket.confidence_score < 0.40 && (
                    <span className="uncertain-tag" title="Flagged below confidence threshold">
                      (Low / Uncertain)
                    </span>
                  )}
                </span>
              </div>

              <div className="meta-card">
                <span className="meta-title">Assigned Support Team</span>
                <span className="meta-value font-medium">{ticket.assigned_team}</span>
              </div>
            </div>

            {/* Original Customer Message */}
            <div className="detail-section">
              <h4 className="detail-heading">Original Customer Message</h4>
              <div className="customer-message-box">
                "{ticket.customer_message}"
              </div>
            </div>

            {/* AI Summary */}
            <div className="detail-section">
              <h4 className="detail-heading">Extractive Issue Summary</h4>
              <p className="summary-text">{ticket.summary}</p>
            </div>

            {/* Draft Response */}
            <div className="detail-section">
              <div className="section-header-flex">
                <h4 className="detail-heading">Suggested Customer Response (Draft)</h4>
                <button
                  type="button"
                  className="btn btn-secondary btn-xs"
                  onClick={handleCopyDraft}
                >
                  {copyFeedback ? '✓ Copied!' : 'Copy Draft'}
                </button>
              </div>
              <div className="draft-response-box">
                <pre className="draft-pre">{ticket.draft_response}</pre>
              </div>
            </div>

            {/* Review Action Panel */}
            <ReviewPanel
              ticket={ticket}
              onActionComplete={handleActionComplete}
            />

            {/* Chronological Audit Trail */}
            <div className="detail-section audit-trail-section">
              <h4 className="detail-heading">Audit Trail & Action History ({auditEvents.length})</h4>
              {auditEvents.length === 0 ? (
                <p className="text-muted">No audit events recorded.</p>
              ) : (
                <div className="timeline">
                  {auditEvents.map((evt, idx) => (
                    <div key={evt.id || idx} className="timeline-item">
                      <div className="timeline-marker"></div>
                      <div className="timeline-content">
                        <div className="timeline-header">
                          <span className="timeline-action">{evt.action}</span>
                          <span className="timeline-date">
                            {new Date(evt.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <div className="timeline-status-change">
                          Transition:{' '}
                          <span className="status-change-pill">
                            {evt.previous_status || 'INIT'} → {evt.new_status}
                          </span>
                        </div>
                        {evt.reviewer_identity && (
                          <div className="timeline-reviewer">
                            Actor: <strong>{evt.reviewer_identity}</strong>
                          </div>
                        )}
                        {evt.action_reason && (
                          <div className="timeline-reason">
                            Note: {evt.action_reason}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        <div className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
