import React, { useState, useEffect, useCallback } from 'react';
import { api } from './services/api';
import { DashboardStats } from './components/DashboardStats';
import { TicketForm } from './components/TicketForm';
import { TicketList } from './components/TicketList';
import { TicketDetails } from './components/TicketDetails';

export function App() {
  const [metrics, setMetrics] = useState(null);
  const [metricsLoading, setMetricsLoading] = useState(true);

  const [tickets, setTickets] = useState([]);
  const [totalTickets, setTotalTickets] = useState(0);
  const [ticketsLoading, setTicketsLoading] = useState(true);
  const [ticketsError, setTicketsError] = useState(null);

  const [selectedTicketId, setSelectedTicketId] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);

  const [filters, setFilters] = useState({
    search: '',
    category: '',
    priority: '',
    review_status: ''
  });

  // Fetch system health
  const checkHealth = useCallback(async () => {
    try {
      const data = await api.getHealth();
      setSystemHealth(data);
    } catch {
      setSystemHealth({ status: 'offline' });
    }
  }, []);

  // Fetch metrics
  const fetchMetrics = useCallback(async () => {
    setMetricsLoading(true);
    try {
      const data = await api.getMetrics();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load metrics', err);
    } finally {
      setMetricsLoading(false);
    }
  }, []);

  // Fetch tickets list
  const fetchTickets = useCallback(async () => {
    setTicketsLoading(true);
    setTicketsError(null);
    try {
      const data = await api.listTickets({
        skip: 0,
        limit: 100,
        search: filters.search,
        category: filters.category,
        priority: filters.priority,
        review_status: filters.review_status
      });
      setTickets(data.items || []);
      setTotalTickets(data.total || 0);
    } catch (err) {
      setTicketsError(err.message || 'Failed to load tickets');
    } finally {
      setTicketsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    checkHealth();
    fetchMetrics();
    fetchTickets();
  }, [checkHealth, fetchMetrics, fetchTickets]);

  const handleTicketCreated = (newTicket) => {
    fetchMetrics();
    fetchTickets();
    // Automatically open inspector for newly created ticket
    if (newTicket && newTicket.ticket_id) {
      setSelectedTicketId(newTicket.ticket_id);
    }
  };

  const handleTicketUpdated = () => {
    fetchMetrics();
    fetchTickets();
  };

  return (
    <div className="app-container">
      {/* Top Navbar */}
      <header className="navbar">
        <div className="navbar-brand">
          <div className="brand-logo-badge">STA</div>
          <div>
            <h1 className="brand-title">Support Ticket Automation</h1>
            <span className="brand-subtitle">
              AI-Assisted Ticket Processing & Review Platform
            </span>
          </div>
        </div>

        <div className="navbar-actions">
          <div className="health-pill">
            <span className={`status-indicator ${systemHealth?.status === 'healthy' ? 'ind-online' : 'ind-offline'}`}></span>
            <span className="health-text">
              Backend: {systemHealth?.status === 'healthy' ? 'Online (v1.0.0)' : 'Offline'}
            </span>
          </div>
          <span className="badge badge-neutral">Local Zero-Cost Dev</span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Aggregated Metrics Dashboard */}
        <DashboardStats
          metrics={metrics}
          loading={metricsLoading}
          onRefresh={fetchMetrics}
        />

        {/* Workspace Layout: Form on Left, List on Right */}
        <div className="workspace-grid">
          <section className="form-column" aria-label="Ticket Ingestion Form">
            <TicketForm onTicketCreated={handleTicketCreated} />
          </section>

          <section className="list-column" aria-label="Ticket Management Table">
            <TicketList
              tickets={tickets}
              total={totalTickets}
              loading={ticketsLoading}
              error={ticketsError}
              selectedTicketId={selectedTicketId}
              onSelectTicket={setSelectedTicketId}
              onRefresh={() => {
                fetchTickets();
                fetchMetrics();
              }}
              filters={filters}
              onFilterChange={setFilters}
            />
          </section>
        </div>
      </main>

      {/* Ticket Details & Review Inspector Modal */}
      {selectedTicketId && (
        <TicketDetails
          ticketId={selectedTicketId}
          onClose={() => setSelectedTicketId(null)}
          onTicketUpdated={handleTicketUpdated}
        />
      )}

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <span>Support Ticket Automation Platform • Production Implementation</span>
          <span className="footer-links">
            Zero-Cost Architecture: Python • FastAPI • SQLite • scikit-learn • React • Vite
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
