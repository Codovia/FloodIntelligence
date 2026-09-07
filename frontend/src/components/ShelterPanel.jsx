import React, { useEffect, useState, useCallback } from 'react';
import { fetchShelters, updateShelterStatus, fetchDistricts } from '../api';

export default function ShelterPanel() {
  const [shelters, setShelters] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [filterDistrict, setFilterDistrict] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(null);

  const loadShelters = useCallback(() => {
    setLoading(true);
    const district = filterDistrict || undefined;
    const status = filterStatus || undefined;
    fetchShelters(district, status)
      .then((data) => { setShelters(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [filterDistrict, filterStatus]);

  useEffect(() => {
    fetchDistricts().then(setDistricts).catch(() => {});
  }, []);

  useEffect(() => {
    loadShelters();
  }, [loadShelters]);

  const handleStatusChange = async (id, newStatus) => {
    setUpdating(id);
    try {
      await updateShelterStatus(id, newStatus, 'admin', `Status changed to ${newStatus}`);
      loadShelters();
    } catch (e) {
      console.error('Failed to update shelter:', e);
    }
    setUpdating(null);
  };

  const activeShelters = shelters.filter(s => s.status === 'ACTIVE').length;
  const fullShelters = shelters.filter(s => s.status === 'FULL').length;
  const candidateShelters = shelters.filter(s => s.status === 'CANDIDATE').length;
  const closedShelters = shelters.filter(s => s.status === 'CLOSED').length;
  const totalCapacity = shelters.reduce((sum, s) => sum + (s.capacity || 0), 0);

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="view-title">Emergency Shelters</h1>
          <p className="view-subtitle">Karnataka State Disaster Management</p>
        </div>
        <div className="filter-row">
          <select className="filter-select" value={filterDistrict} onChange={e => setFilterDistrict(e.target.value)}>
            <option value="">All Districts</option>
            {districts.map(d => <option key={d.name} value={d.name}>{d.name}</option>)}
          </select>
          <select className="filter-select" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
            <option value="">All Status</option>
            <option value="ACTIVE">Active</option>
            <option value="CANDIDATE">Candidate</option>
            <option value="FULL">Full</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>
      </div>

      {/* Summary stats */}
      <div className="shelter-summary-row">
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
        <div className="summary-stat">
          <div className="value" style={{ color: 'var(--text-muted)' }}>{closedShelters}</div>
          <div className="label">Closed</div>
        </div>
        <div className="summary-stat">
          <div className="value" style={{ color: 'var(--accent-cyan)' }}>{totalCapacity.toLocaleString()}</div>
          <div className="label">Total Capacity</div>
        </div>
      </div>

      {/* Shelter Cards */}
      {loading ? (
        <div className="loading-state"><div className="loading-spinner" /><p>Loading shelters...</p></div>
      ) : shelters.length === 0 ? (
        <p className="empty-msg">No shelters found matching your filters.</p>
      ) : (
        <div className="shelters-grid">
          {shelters.map(shelter => {
            const pct = shelter.capacity > 0 ? Math.round((shelter.current_occupancy / shelter.capacity) * 100) : 0;
            const isDanger = pct >= 85;
            return (
              <div key={shelter.id} className={`shelter-card status-${shelter.status?.toLowerCase()}`}>
                <div className="shelter-header">
                  <div className="shelter-meta">
                    <div className="shelter-name">{shelter.name}</div>
                    <div className="shelter-location">📍 {shelter.district}{shelter.locality ? ` · ${shelter.locality}` : ''}</div>
                  </div>
                  <span className={`badge ${shelter.status?.toLowerCase()}`}>{shelter.status}</span>
                </div>

                <div className="shelter-occupancy-row">
                  <span className="occupancy-label">Occupancy</span>
                  <span className="occupancy-value">
                    {shelter.current_occupancy?.toLocaleString()} / {shelter.capacity?.toLocaleString()}
                    <span style={{ color: isDanger ? 'var(--alert-red)' : 'var(--text-muted)', marginLeft: '6px' }}>
                      ({pct}%)
                    </span>
                  </span>
                </div>

                <div className="progress-bar-bg">
                  <div className={`progress-bar-fill${isDanger ? ' danger' : ''}`} style={{ width: `${pct}%` }} />
                </div>

                {/* Admin actions */}
                <div className="shelter-actions">
                  {shelter.status === 'CANDIDATE' && (
                    <button className="btn btn-success" onClick={() => handleStatusChange(shelter.id, 'ACTIVE')} disabled={updating === shelter.id}>
                      ✓ Activate
                    </button>
                  )}
                  {shelter.status === 'ACTIVE' && (
                    <>
                      <button className="btn btn-warning" onClick={() => handleStatusChange(shelter.id, 'FULL')} disabled={updating === shelter.id}>
                        Mark Full
                      </button>
                      <button className="btn btn-outline" onClick={() => handleStatusChange(shelter.id, 'CLOSED')} disabled={updating === shelter.id}>
                        Close
                      </button>
                    </>
                  )}
                  {shelter.status === 'FULL' && (
                    <button className="btn btn-success" onClick={() => handleStatusChange(shelter.id, 'ACTIVE')} disabled={updating === shelter.id}>
                      Reopen
                    </button>
                  )}
                  {shelter.status === 'CLOSED' && (
                    <button className="btn btn-success" onClick={() => handleStatusChange(shelter.id, 'ACTIVE')} disabled={updating === shelter.id}>
                      Reactivate
                    </button>
                  )}
                </div>

                {shelter.changed_at && (
                  <div className="shelter-audit">
                    Last updated by {shelter.changed_by} · {new Date(shelter.changed_at).toLocaleString()}
                    {shelter.change_reason && <span className="audit-reason"> — {shelter.change_reason}</span>}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Footer */}
      <div className="panel-footer">
        <p className="footer-note">
          Data provenance: <strong>USER_REPORTED</strong> · Shelter data managed by KSNDMC / DDMAs<br />
          Last synced: {new Date().toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
