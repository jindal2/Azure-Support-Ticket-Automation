import React, { useState } from 'react';
import { api } from '../services/api';

const PRESET_SCENARIOS = [
  {
    label: 'Billing: Double Charge',
    id: `BILL-${Math.floor(100 + Math.random() * 900)}`,
    message: 'I was charged twice on my credit card for the monthly subscription.'
  },
  {
    label: 'Technical: PDF Crash',
    id: `TECH-${Math.floor(100 + Math.random() * 900)}`,
    message: 'The application crashes immediately whenever I upload a PDF.'
  },
  {
    label: 'Access: Password Reset',
    id: `ACC-${Math.floor(100 + Math.random() * 900)}`,
    message: 'I cannot reset my password and access my account.'
  },
  {
    label: 'General: Subscription Plans',
    id: `GEN-${Math.floor(100 + Math.random() * 900)}`,
    message: 'Could you explain the available subscription plans?'
  },
  {
    label: 'Ambiguous (Requires Review)',
    id: `AMB-${Math.floor(100 + Math.random() * 900)}`,
    message: 'Payment went through yesterday but my account is locked and I cannot sign in to check the billing receipt.'
  },
  {
    label: 'Critical Outage (Safety Override)',
    id: `CRIT-${Math.floor(100 + Math.random() * 900)}`,
    message: 'CRITICAL OUTAGE: Entire production service is down, all users are receiving 500 errors across all endpoints.'
  },
  {
    label: 'Suspected Security Incident',
    id: `SEC-${Math.floor(100 + Math.random() * 900)}`,
    message: 'URGENT: Suspected security breach, unauthorized logins detected from unfamiliar foreign IP addresses.'
  }
];

export function TicketForm({ onTicketCreated }) {
  const [ticketId, setTicketId] = useState('');
  const [customerMessage, setCustomerMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const handleSelectPreset = (e) => {
    const idx = e.target.value;
    if (idx === '') return;
    const preset = PRESET_SCENARIOS[parseInt(idx, 10)];
    if (preset) {
      setTicketId(preset.id);
      setCustomerMessage(preset.message);
      setErrorMessage(null);
      setSuccessMessage(null);
    }
  };

  const handleGenerateId = () => {
    const prefix = 'TCK';
    const num = Math.floor(1000 + Math.random() * 9000);
    setTicketId(`${prefix}-${num}`);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    // Client-side validations
    const trimmedId = ticketId.trim();
    const trimmedMsg = customerMessage.trim();

    if (!trimmedId) {
      setErrorMessage('Ticket ID is required and cannot be whitespace only.');
      return;
    }

    if (!trimmedMsg) {
      setErrorMessage('Customer message is required and cannot be empty.');
      return;
    }

    setSubmitting(true);

    try {
      const createdTicket = await api.createTicket({
        ticket_id: trimmedId,
        customer_message: trimmedMsg
      });

      setSuccessMessage(
        `Ticket '${createdTicket.ticket_id}' processed successfully! ` +
        `Categorized as '${createdTicket.predicted_category}' with priority '${createdTicket.priority}'. ` +
        `Initial status: '${createdTicket.review_status}'.`
      );

      // Reset form
      setTicketId('');
      setCustomerMessage('');

      if (onTicketCreated) {
        onTicketCreated(createdTicket);
      }
    } catch (err) {
      if (err.status === 409) {
        setErrorMessage(`Duplicate Ticket ID Conflict (HTTP 409): Ticket ID '${trimmedId}' already exists in database.`);
      } else if (err.status === 422) {
        setErrorMessage(`Validation Error (HTTP 422): ${err.message}`);
      } else {
        setErrorMessage(err.message || 'Failed to submit ticket. Please check connection.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card ticket-form-card">
      <div className="card-header">
        <h3 className="card-title">Submit New Support Ticket</h3>
        <p className="card-description">
          Ingests customer message for ML classification, priority assignment, summary generation, and draft response creation.
        </p>
      </div>

      <div className="preset-selector-bar">
        <label htmlFor="presetSelect" className="preset-label">
          Load Sample Scenario:
        </label>
        <select
          id="presetSelect"
          className="select-input"
          onChange={handleSelectPreset}
          defaultValue=""
        >
          <option value="" disabled>-- Select a test case --</option>
          {PRESET_SCENARIOS.map((sc, idx) => (
            <option key={sc.label} value={idx}>{sc.label}</option>
          ))}
        </select>
      </div>

      {errorMessage && (
        <div className="alert alert-error" role="alert">
          <span className="alert-icon">⚠</span>
          <div className="alert-content">{errorMessage}</div>
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success" role="alert">
          <span className="alert-icon">✓</span>
          <div className="alert-content">{successMessage}</div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="ticket-form">
        <div className="form-group">
          <div className="form-label-row">
            <label htmlFor="ticketId" className="form-label">
              Ticket ID <span className="text-red">*</span>
            </label>
            <button
              type="button"
              className="btn-text"
              onClick={handleGenerateId}
            >
              Generate ID
            </button>
          </div>
          <input
            id="ticketId"
            type="text"
            className="text-input"
            placeholder="e.g. BILL-001 or TCK-1042"
            value={ticketId}
            onChange={(e) => setTicketId(e.target.value)}
            disabled={submitting}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="customerMessage" className="form-label">
            Customer Support Message <span className="text-red">*</span>
          </label>
          <textarea
            id="customerMessage"
            className="textarea-input"
            rows="4"
            placeholder="Describe customer's technical defect, billing enquiry, access lockout, or general question..."
            value={customerMessage}
            onChange={(e) => setCustomerMessage(e.target.value)}
            disabled={submitting}
            required
          ></textarea>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
          >
            {submitting ? (
              <>
                <span className="spinner-sm"></span>
                <span>Processing & Classifying...</span>
              </>
            ) : (
              'Ingest & Process Ticket'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
