import React, { useState } from 'react';
import { api } from '../services/api';

export function ReviewPanel({ ticket, onActionComplete }) {
  const [reviewerIdentity, setReviewerIdentity] = useState('Agent Sarah Jenkins');
  const [confirmed, setConfirmed] = useState(false);
  const [approvalNotes, setApprovalNotes] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);

  if (!ticket) return null;

  const isLocked = ticket.review_status === 'READY' || ticket.review_status === 'REJECTED';

  const handleApprove = async () => {
    setActionError(null);
    setActionSuccess(null);

    const trimmedReviewer = reviewerIdentity.trim();
    if (!trimmedReviewer) {
      setActionError('Reviewer identity is required to authorize this response.');
      return;
    }

    if (!confirmed) {
      setActionError('You must check the explicit confirmation checkbox to approve the draft.');
      return;
    }

    setLoading(true);

    try {
      const updated = await api.approveTicket(ticket.ticket_id, {
        reviewer_identity: trimmedReviewer,
        confirmed: true,
        notes: approvalNotes.trim() || undefined
      });

      setActionSuccess(`Draft response approved successfully by ${trimmedReviewer}! Status transitioned to READY.`);
      setConfirmed(false);
      setApprovalNotes('');

      if (onActionComplete) {
        onActionComplete(updated);
      }
    } catch (err) {
      setActionError(err.message || 'Failed to approve ticket draft.');
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setActionError(null);
    setActionSuccess(null);

    const trimmedReviewer = reviewerIdentity.trim();
    const trimmedReason = rejectionReason.trim();

    if (!trimmedReviewer) {
      setActionError('Reviewer identity is required.');
      return;
    }

    if (!trimmedReason) {
      setActionError('A clear rejection reason must be provided before sending back for revision.');
      return;
    }

    setLoading(true);

    try {
      const updated = await api.rejectTicket(ticket.ticket_id, {
        reviewer_identity: trimmedReviewer,
        rejection_reason: trimmedReason
      });

      setActionSuccess(`Draft response rejected by ${trimmedReviewer}. Status transitioned to REJECTED.`);
      setRejectionReason('');

      if (onActionComplete) {
        onActionComplete(updated);
      }
    } catch (err) {
      setActionError(err.message || 'Failed to reject ticket draft.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="review-panel-card">
      <div className="review-header">
        <h4 className="review-title">Human-in-the-Loop Review & Approval</h4>
        <span className="prototype-disclaimer">
          Prototype Note: Reviewer identity is self-reported for local demo; production requires Azure AD authentication.
        </span>
      </div>

      {actionError && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠</span>
          <div className="alert-content">{actionError}</div>
        </div>
      )}

      {actionSuccess && (
        <div className="alert alert-success">
          <span className="alert-icon">✓</span>
          <div className="alert-content">{actionSuccess}</div>
        </div>
      )}

      {isLocked ? (
        <div className={`status-locked-notice ${ticket.review_status === 'READY' ? 'notice-ready' : 'notice-rejected'}`}>
          {ticket.review_status === 'READY' ? (
            <>
              <strong>✓ TICKET APPROVED & READY:</strong> Authorized by{' '}
              <em>{ticket.reviewer_identity || 'Reviewer'}</em> on{' '}
              {ticket.approval_timestamp ? new Date(ticket.approval_timestamp).toLocaleString() : 'N/A'}.
              Automated response is now cleared for customer dispatch.
            </>
          ) : (
            <>
              <strong>✕ TICKET REJECTED:</strong> Rejected by{' '}
              <em>{ticket.reviewer_identity || 'Reviewer'}</em>.
              <div className="rejection-reason-box">Reason: {ticket.rejection_reason}</div>
            </>
          )}
        </div>
      ) : (
        <div className="review-actions-form">
          <div className="form-group">
            <label className="form-label" htmlFor="reviewerIdentity">
              Reviewer Name / Employee ID <span className="text-red">*</span>
            </label>
            <input
              id="reviewerIdentity"
              type="text"
              className="text-input"
              value={reviewerIdentity}
              onChange={(e) => setReviewerIdentity(e.target.value)}
              disabled={loading}
              placeholder="e.g. Lead Agent Sarah Jenkins"
            />
          </div>

          <div className="action-split-grid">
            {/* Approval Block */}
            <div className="action-block approval-block">
              <h5>Approve Draft to READY</h5>
              <p className="block-description">
                Validates draft accuracy and clears message for customer delivery.
              </p>

              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={confirmed}
                    onChange={(e) => setConfirmed(e.target.checked)}
                    disabled={loading}
                  />
                  <span>I confirm this response has been verified and meets support guidelines.</span>
                </label>
              </div>

              <div className="form-group">
                <input
                  type="text"
                  className="text-input text-input-sm"
                  placeholder="Optional review notes..."
                  value={approvalNotes}
                  onChange={(e) => setApprovalNotes(e.target.value)}
                  disabled={loading}
                />
              </div>

              <button
                type="button"
                className="btn btn-success"
                onClick={handleApprove}
                disabled={loading || !confirmed}
              >
                {loading ? 'Authorizing...' : 'Approve & Mark READY'}
              </button>
            </div>

            {/* Rejection Block */}
            <div className="action-block rejection-block">
              <h5>Reject Draft</h5>
              <p className="block-description">
                Marks draft as REJECTED and documents the revision requirement.
              </p>

              <div className="form-group">
                <textarea
                  className="textarea-input textarea-sm"
                  rows="2"
                  placeholder="Enter mandatory rejection reason (e.g. incorrect plan quote, missing steps)..."
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  disabled={loading}
                ></textarea>
              </div>

              <button
                type="button"
                className="btn btn-danger"
                onClick={handleReject}
                disabled={loading || !rejectionReason.trim()}
              >
                {loading ? 'Rejecting...' : 'Reject Draft'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
