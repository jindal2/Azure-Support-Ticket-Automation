import React from 'react';

export function StatusBadge({ type, value }) {
  if (!value) return null;

  let className = 'badge';
  let label = value;

  if (type === 'priority') {
    switch (value.toUpperCase()) {
      case 'CRITICAL':
        className += ' badge-critical';
        break;
      case 'HIGH':
        className += ' badge-high';
        break;
      case 'MEDIUM':
        className += ' badge-medium';
        break;
      case 'LOW':
        className += ' badge-low';
        break;
      default:
        className += ' badge-neutral';
    }
  } else if (type === 'status') {
    switch (value.toUpperCase()) {
      case 'READY':
        className += ' badge-ready';
        label = '✓ READY';
        break;
      case 'NEEDS_REVIEW':
        className += ' badge-needs-review';
        label = '⚠ NEEDS REVIEW';
        break;
      case 'PENDING_REVIEW':
        className += ' badge-pending';
        label = '⧗ PENDING REVIEW';
        break;
      case 'REJECTED':
        className += ' badge-rejected';
        label = '✕ REJECTED';
        break;
      default:
        className += ' badge-neutral';
    }
  } else if (type === 'category') {
    className += ` badge-cat-${value.toLowerCase()}`;
  }

  return <span className={className}>{label}</span>;
}
