import React, { useEffect, useState } from 'react';
import { fetchAutoPrediction, fetchRainfallForecast, fetchShelters, fetchLocalities } from '../api';

function RainfallChart({ forecast }) {
  if (!forecast || forecast.length === 0) return null;
  const maxRain = Math.max(...forecast.map(d => d.rainfall_mm), 1);

  return (
    <div className="rainfall-chart">
      <div className="chart-bars">
        {forecast.map((day, i) => {
          const height = Math.max(4, (day.rainfall_mm / maxRain) * 100);
          const isHeavy = day.rainfall_mm > 30;
          return (
            <div key={i} className="chart-bar-col">
              <div className="chart-bar-value">{day.rainfall_mm}mm</div>
              <div
                className={`chart-bar ${isHeavy ? 'heavy' : ''}`}
                style={{ height: `${height}%` }}
              />
              <div className="chart-bar-label">
                {new Date(day.date).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric' })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function DistrictDetail({ district, onBack }) {
  const [prediction, setPrediction] = useState(null);
  const [weather, setWeather] = useState(null);
  const [shelters, setShelters] = useState([]);
  const [localities, setLocalities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchAutoPrediction(district).catch(() => null),
      fetchRainfallForecast(district).catch(() => null),
      fetchShelters(district).catch(() => []),
      fetchLocalities(district).catch(() => []),
    ]).then(([pred, wthr, shlt, locs]) => {
      setPrediction(pred);
      setWeather(wthr);
      setShelters(shlt);
      setLocalities(locs);
      setLoading(false);
    });
  }, [district]);

  if (loading) {
    return (
      <div className="view-container">
        <div className="loading-state"><div className="loading-spinner" /><p>Loading {district} data...</p></div>
      </div>
    );
  }

  const prob = prediction?.flood_probability || 0;
  const pct = Math.round(prob * 100);
  const riskColor = prediction?.risk_level === 'High' ? 'var(--alert-red)' :
    prediction?.risk_level === 'Medium' ? 'var(--alert-orange)' : 'var(--success-green)';

  return (
    <div className="view-container">
      {/* Header with back button */}
      <div className="view-header">
        <div>
          <button className="back-btn" onClick={onBack}>← Back to Map</button>
          <h1 className="view-title district-title">{district}</h1>
          <p className="view-subtitle">Detailed flood risk analysis</p>
        </div>
        <div className="district-risk-badge" style={{ borderColor: riskColor }}>
          <span className="drb-label">Risk Level</span>
          <span className="drb-value" style={{ color: riskColor }}>
            {prediction?.risk_level || 'N/A'}
          </span>
          <span className="drb-pct" style={{ color: riskColor }}>{pct}%</span>
        </div>
      </div>

      {/* Main metrics */}
      <div className="district-metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">📊</div>
          <div className="metric-label">Flood Probability</div>
          <div className="metric-value" style={{ color: riskColor }}>{pct}%</div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">🎯</div>
          <div className="metric-label">Confidence</div>
          <div className="metric-value">{Math.round((prediction?.confidence_score || 0) * 100)}%</div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">📈</div>
          <div className="metric-label">Operational Risk</div>
          <div className="metric-value">{prediction?.operational_risk_index || 0}/100</div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">💧</div>
          <div className="metric-label">Drainage Risk</div>
          <div className="metric-value">{prediction?.drainage_risk_level || 'N/A'}</div>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="dashboard-panels">
        {/* 7-day Rainfall Forecast */}
        <div className="panel">
          <h3 className="panel-title">🌧️ 7-Day Rainfall Forecast</h3>
          {weather?.forecast ? (
            <>
              <RainfallChart forecast={weather.forecast} />
              <div className="rainfall-summary">
                <span>Total 7-day: <strong>{weather.total_7day_mm}mm</strong></span>
                <span className="rainfall-source">Source: {weather.source}</span>
              </div>
            </>
          ) : (
            <p className="empty-msg">Weather data unavailable</p>
          )}
        </div>

        {/* Risk Factors */}
        <div className="panel">
          <h3 className="panel-title">⚠️ Contributing Factors</h3>
          <div className="factors-list">
            {prediction?.main_factors?.map((factor, i) => (
              <div key={i} className="factor-item">
                <span className="factor-bullet">•</span>
                {factor}
              </div>
            ))}
            {(!prediction?.main_factors || prediction.main_factors.length === 0) && (
              <p className="empty-msg">No significant risk factors</p>
            )}
          </div>

          <div className="reservoir-status-section">
            <h4>Reservoir: <span className={`reservoir-badge ${(prediction?.reservoir_status || '').toLowerCase()}`}>
              {prediction?.reservoir_status || 'N/A'}
            </span></h4>
          </div>
        </div>
      </div>

      {/* Shelters in this district */}
      {shelters.length > 0 && (
        <div className="panel">
          <h3 className="panel-title">⛺ Shelters in {district}</h3>
          <div className="shelter-mini-grid">
            {shelters.map((s) => (
              <div key={s.id} className={`shelter-mini-card status-${s.status?.toLowerCase()}`}>
                <div className="smc-name">{s.name}</div>
                <div className="smc-row">
                  <span className={`badge ${s.status?.toLowerCase()}`}>{s.status}</span>
                  <span className="smc-cap">Capacity: {s.capacity}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Localities */}
      {localities.length > 0 && (
        <div className="panel">
          <h3 className="panel-title">📍 Localities ({localities.length})</h3>
          <div className="locality-grid">
            {localities.slice(0, 12).map((loc, i) => (
              <div key={i} className="locality-chip">
                <span className="locality-name">{loc.name}</span>
                <span className="locality-coords">{loc.lat?.toFixed(2)}, {loc.lon?.toFixed(2)}</span>
              </div>
            ))}
            {localities.length > 12 && (
              <div className="locality-chip more">+{localities.length - 12} more</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
