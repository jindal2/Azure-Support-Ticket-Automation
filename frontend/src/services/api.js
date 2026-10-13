/**
 * Support Ticket Automation System
 * Central API Client Service
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  try {
    const response = await fetch(url, { ...options, headers });
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data?.detail || data?.message || `HTTP ${response.status}: Request failed`;
      const error = new Error(errorMsg);
      error.status = response.status;
      error.details = data;
      throw error;
    }

    return data;
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      const netError = new Error(`Cannot connect to backend server at ${API_BASE}. Please ensure FastAPI is running.`);
      netError.status = 0;
      throw netError;
    }
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => request('/health'),

  // Metrics
  getMetrics: () => request('/metrics'),

  // Tickets
  listTickets: (params = {}) => {
    const query = new URLSearchParams();
    if (params.skip !== undefined) query.append('skip', params.skip);
    if (params.limit !== undefined) query.append('limit', params.limit);
    if (params.search) query.append('search', params.search);
    if (params.category) query.append('category', params.category);
    if (params.priority) query.append('priority', params.priority);
    if (params.review_status) query.append('review_status', params.review_status);

    const qs = query.toString();
    return request(`/tickets${qs ? `?${qs}` : ''}`);
  },

  getTicket: (ticketId) => request(`/tickets/${encodeURIComponent(ticketId)}`),

  createTicket: (data) =>
    request('/tickets', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Human Review Actions
  approveTicket: (ticketId, data) =>
    request(`/tickets/${encodeURIComponent(ticketId)}/approve`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  rejectTicket: (ticketId, data) =>
    request(`/tickets/${encodeURIComponent(ticketId)}/reject`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Audit Trail
  getAuditHistory: (ticketId) =>
    request(`/tickets/${encodeURIComponent(ticketId)}/audit`)
};
