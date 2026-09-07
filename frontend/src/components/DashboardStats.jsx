import React, { useEffect, useState } from 'react';
import { fetchDashboardStats, fetchHealth } from '../api';

function StatCard({ icon, label, value, color, subtitle }) {
  return (
    <div className="stat-card">
      <div className="stat-card-icon" style={{ background: color }}>{icon}</div>
      <div className="stat-card-body">
        <div className="stat-card-value">{value ?? '—'}</div>
        <div className="stat-card-label">{label}</div>
        {subtitle && <div className="stat-card-subtitle">{subtitle}</div>}
      </div>
    </div>
  );
}

function RiskDistrictRow({ district, probability, risk_level, onClick }) {
  const color = risk_level === 'High' ? 'var(--alert-red)' : risk_level === 'Medium' ? 'var(--alert-orange)' : 'var(--success-green)';
  const pct = Math.round(probability * 100);
  return (
    <div className="risk-row" onClick={() => onClick(district)}>
      <div className="risk-row-name">{district}</div>
      <div className="risk-row-bar-bg">
        <div className="risk-row-bar" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="risk-row-pct" style={{ color }}>{pct}%</span>
    </div>
  );
}

export default function DashboardStats({ onDistrictClick, onNavigate }) {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    Promise.all([fetchDashboardStats(), fetchHealth()])
      .then(([s, h]) => {
        if (mounted) { setStats(s); setHealth(h); setLoading(false); }
      })
      .catch(err => {
        if (mounted) { setError(err.message); setLoading(false); }
      });
    return () => { mounted = false; };
  }, []);

  if (loading) {
    return (
      <div className="view-container">
        <div className="loading-state">
          <div className="loading-spinner" />
          <p>Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="view-container">
        <div className="error-state">
          <span className="error-icon">⚠️</span>
          <h3>Connection Error</h3>
          <p>{error}</p>
          <p className="error-hint">Make sure the backend is running on port 8001</p>
        </div>
      </div>
    );
  }

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="view-title">Dashboard</h1>
          <p className="view-subtitle">Real-time flood risk overview for Karnataka</p>
        </div>
        <div className="header-badge live-badge">
          <span className="live-dot" />
          Live
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <StatCard icon="📍" label="Total Districts" value={stats?.total_districts} color="linear-gradient(135deg, #3b82f6, #06b6d4)" />
        <StatCard icon="🔴" label="High Risk" value={stats?.high_risk} color="linear-gradient(135deg, #ef4444, #f97316)" subtitle="Immediate attention" />
        <StatCard icon="🟡" label="Medium Risk" value={stats?.medium_risk} color="linear-gradient(135deg, #f59e0b, #eab308)" subtitle="Monitor closely" />
        <StatCard icon="🟢" label="Low Risk" value={stats?.low_risk} color="linear-gradient(135deg, #22c55e, #10b981)" />
        <StatCard icon="⛺" label="Active Shelters" value={stats?.active_shelters} color="linear-gradient(135deg, #8b5cf6, #a78bfa)" subtitle={`${stats?.total_shelter_capacity?.toLocaleString() || 0} capacity`} />
        <StatCard icon="🤖" label="Model Status" value={stats?.model_loaded ? 'Active' : 'Offline'} color={stats?.model_loaded ? 'linear-gradient(135deg, #06b6d4, #0891b2)' : 'linear-gradient(135deg, #6b7280, #9ca3af)'} subtitle={stats?.model_loaded ? `v${stats.model_version}` : ''} />
      </div>

      {/* Two-column section */}
      <div className="dashboard-panels">
        {/* Top Risk Districts */}
        <div className="panel">
          <div className="panel-title-row">
            <h3 className="panel-title">🔥 Highest Risk Districts</h3>
            <button className="link-btn" onClick={() => onNavigate('map')}>View Map →</button>
          </div>
          <div className="risk-list">
            {stats?.top_risk_districts?.map((d, i) => (
              <RiskDistrictRow key={i} {...d} onClick={onDistrictClick} />
            ))}
            {(!stats?.top_risk_districts || stats.top_risk_districts.length === 0) && (
              <p className="empty-msg">No high-risk districts currently</p>
            )}
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="panel">
          <div className="panel-title-row">
            <h3 className="panel-title">🔔 Recent Alerts</h3>
            <button className="link-btn" onClick={() => onNavigate('alerts')}>View All →</button>
          </div>
          <div className="alerts-mini-list">
            {stats?.recent_alerts?.slice(0, 5).map((a, i) => (
              <div key={i} className="alert-mini-item" onClick={() => onDistrictClick(a.district)}>
                <div className="alert-mini-header">
                  <span className="alert-mini-district">{a.district}</span>
                  <span className={`badge ${a.risk_level?.toLowerCase()}`}>{a.risk_level}</span>
                </div>
                <div className="alert-mini-meta">
                  {a.locality} · {a.predicted_date}
                </div>
              </div>
            ))}
            {(!stats?.recent_alerts || stats.recent_alerts.length === 0) && (
              <p className="empty-msg">No recent alerts</p>
            )}
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="panel system-health">
        <h3 className="panel-title">⚙️ System Health</h3>
        <div className="health-indicators">
          <div className={`health-dot ${health?.status === 'ok' ? 'green' : 'red'}`} />
          <span>API: {health?.status || 'unknown'}</span>
          <div className={`health-dot ${health?.model_loaded ? 'green' : 'red'}`} />
          <span>ML Model: {health?.model_loaded ? 'loaded' : 'offline'}</span>
          <div className={`health-dot ${health?.dataset_loaded ? 'green' : 'red'}`} />
          <span>Dataset: {health?.dataset_loaded ? 'loaded' : 'missing'}</span>
          <div className="health-dot green" />
          <span>Districts: {health?.districts || 0}</span>
        </div>
      </div>
    </div>
  );
}
