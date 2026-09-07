import React, { useEffect, useState } from 'react';
import { fetchAlertEvents, fetchAlerts, fetchDistricts } from '../api';

export default function AlertsView({ onDistrictClick }) {
  const [alertEvents, setAlertEvents] = useState([]);
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [districts, setDistricts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDistricts().then(setDistricts).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const district = selectedDistrict || undefined;
    Promise.all([
      fetchAlertEvents(district, 100),
      fetchAlerts(district),
    ])
      .then(([events, active]) => {
        setAlertEvents(events);
        setActiveAlerts(active);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [selectedDistrict]);

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="view-title">Alert Center</h1>
          <p className="view-subtitle">Flood risk alerts and event history</p>
        </div>
        <select
          className="filter-select"
          value={selectedDistrict}
          onChange={(e) => setSelectedDistrict(e.target.value)}
        >
          <option value="">All Districts</option>
          {districts.map(d => (
            <option key={d.name} value={d.name}>{d.name}</option>
          ))}
        </select>
      </div>

      {/* Active High-Risk Alerts */}
      {activeAlerts.length > 0 && (
        <div className="active-alerts-section">
          <h3 className="section-title">🔴 Active High-Risk Alerts</h3>
          <div className="active-alerts-grid">
            {activeAlerts.map((alert, i) => (
              <div
                key={i}
                className="active-alert-card"
                onClick={() => onDistrictClick(alert.district)}
              >
                <div className="active-alert-header">
                  <span className="active-alert-district">{alert.district}</span>
                  <span className="active-alert-prob">
                    {Math.round((alert.flood_probability || 0) * 100)}%
                  </span>
                </div>
                <div className="active-alert-factors">
                  {alert.main_factors?.slice(0, 3).map((f, j) => (
                    <span key={j} className="factor-tag">{f}</span>
                  ))}
                </div>
                <div className="active-alert-score">
                  ORI: {alert.operational_risk_index || 0} · Confidence: {Math.round((alert.confidence_score || 0) * 100)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Alert Event History */}
      <div className="panel">
        <h3 className="panel-title">📋 Alert History</h3>
        {loading ? (
          <div className="loading-state"><div className="loading-spinner" /><p>Loading alerts...</p></div>
        ) : alertEvents.length === 0 ? (
          <p className="empty-msg">No alert events recorded yet. Run an alert check from the backend to generate alerts.</p>
        ) : (
          <div className="alert-table-wrapper">
            <table className="alert-table">
              <thead>
                <tr>
                  <th>District</th>
                  <th>Locality</th>
                  <th>Predicted Date</th>
                  <th>Risk</th>
                  <th>Triggered</th>
                  <th>Notified</th>
                </tr>
              </thead>
              <tbody>
                {alertEvents.map((event) => (
                  <tr
                    key={event.id}
                    className="alert-row"
                    onClick={() => onDistrictClick(event.district)}
                  >
                    <td className="alert-district">{event.district}</td>
                    <td>{event.locality}</td>
                    <td>{event.predicted_date}</td>
                    <td>
                      <span className={`badge ${event.risk_level?.toLowerCase()}`}>
                        {event.risk_level}
                      </span>
                    </td>
                    <td className="alert-time">
                      {new Date(event.triggered_at).toLocaleString()}
                    </td>
                    <td>
                      <span className={`notify-status ${event.notified ? 'sent' : 'pending'}`}>
                        {event.notified ? '✓ Sent' : '○ Pending'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
