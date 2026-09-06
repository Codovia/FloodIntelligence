import React, { useState } from 'react';

const SHELTERS = [
  {
    id: 1,
    name: "Kanteerava Indoor Stadium",
    location: "Bengaluru Urban",
    capacity: 500,
    current_occupancy: 450,
    status: "ACTIVE"
  },
  {
    id: 2,
    name: "Mysuru Town Hall",
    location: "Mysuru District",
    capacity: 200,
    current_occupancy: 200,
    status: "FULL"
  },
  {
    id: 3,
    name: "Udupi District Hall",
    location: "Udupi",
    capacity: 300,
    current_occupancy: 210,
    status: "ACTIVE"
  },
  {
    id: 4,
    name: "Hubli Primary School",
    location: "Dharwad District",
    capacity: 150,
    current_occupancy: 0,
    status: "CANDIDATE"
  },
  {
    id: 5,
    name: "Mangaluru Community Centre",
    location: "Dakshina Kannada",
    capacity: 400,
    current_occupancy: 0,
    status: "CANDIDATE"
  }
];

export default function ShelterPanel() {
  const [shelters, setShelters] = useState(SHELTERS);

  const activeShelters    = shelters.filter(s => s.status === 'ACTIVE').length;
  const fullShelters      = shelters.filter(s => s.status === 'FULL').length;
  const candidateShelters = shelters.filter(s => s.status === 'CANDIDATE').length;

  const handleActivate = (id) => {
    setShelters(prev =>
      prev.map(s => s.id === id ? { ...s, status: 'ACTIVE' } : s)
    );
  };

  return (
    <div className="side-panel">
      {/* Header */}
      <div className="panel-header">
        <h2>⛺ Emergency Shelters</h2>
        <p>Karnataka State Disaster Management</p>
        <div className="panel-summary">
          <div className="summary-stat">
            <div className="value active-val">{activeShelters}</div>
            <div className="label">Active</div>
          </div>
          <div className="summary-stat">
            <div className="value full-val">{fullShelters}</div>
            <div className="label">Full</div>
          </div>
          <div className="summary-stat">
            <div className="value candidate-val">{candidateShelters}</div>
            <div className="label">Pending</div>
          </div>
        </div>
      </div>

      {/* Shelter Cards */}
      <div className="shelters-list">
        {shelters.map(shelter => {
          const pct = Math.round((shelter.current_occupancy / shelter.capacity) * 100);
          const isDanger = pct >= 85;
          return (
            <div
              key={shelter.id}
              className={`shelter-card status-${shelter.status.toLowerCase()}`}
            >
              <div className="shelter-header">
                <div className="shelter-meta">
                  <div className="shelter-name">{shelter.name}</div>
                  <div className="shelter-location">📍 {shelter.location}</div>
                </div>
                <span className={`badge ${shelter.status.toLowerCase()}`}>
                  {shelter.status}
                </span>
              </div>

              <div className="shelter-occupancy-row">
                <span className="occupancy-label">Occupancy</span>
                <span className="occupancy-value">
                  {shelter.current_occupancy.toLocaleString()} / {shelter.capacity.toLocaleString()}
                  <span style={{ color: isDanger ? 'var(--alert-red)' : 'var(--text-muted)', marginLeft: '6px' }}>
                    ({pct}%)
                  </span>
                </span>
              </div>

              <div className="progress-bar-bg">
                <div
                  className={`progress-bar-fill${isDanger ? ' danger' : ''}`}
                  style={{ width: `${pct}%` }}
                ></div>
              </div>

              {shelter.status === 'CANDIDATE' && (
                <button className="btn" onClick={() => handleActivate(shelter.id)}>
                  ✓ Activate Shelter
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="panel-footer">
        <p className="footer-note">
          Data provenance: <strong>USER_REPORTED</strong><br />
          Last synced: {new Date().toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
