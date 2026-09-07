import React, { useEffect, useState, useCallback } from 'react';
import { MapContainer, TileLayer, GeoJSON, ZoomControl, CircleMarker, Popup } from 'react-leaflet';
import { fetchMapRisk, fetchShelters } from '../api';

const TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
const TILE_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';

function getRiskColor(prob) {
  if (prob > 0.75) return '#ff4757';
  if (prob > 0.5)  return '#ffa502';
  if (prob > 0.25) return '#f9ca24';
  return '#2ed573';
}

function getRiskLabel(prob) {
  if (prob > 0.75) return 'CRITICAL';
  if (prob > 0.5)  return 'HIGH';
  if (prob > 0.25) return 'MODERATE';
  return 'LOW';
}

export default function MapDashboard({ onDistrictClick }) {
  const [geojson, setGeojson] = useState(null);
  const [shelters, setShelters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({ critical: 0, high: 0, total: 0 });
  const [showShelters, setShowShelters] = useState(true);

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([
      fetchMapRisk(),
      fetchShelters(),
    ])
      .then(([geo, shlt]) => {
        setGeojson(geo);
        setShelters(shlt);

        const features = geo?.features || [];
        const critical = features.filter(f => (f.properties?.flood_probability || 0) > 0.75).length;
        const high = features.filter(f => {
          const p = f.properties?.flood_probability || 0;
          return p > 0.5 && p <= 0.75;
        }).length;
        setStats({ critical, high, total: features.length });
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 180000); // refresh every 3 min
    return () => clearInterval(interval);
  }, [loadData]);

  const getStyle = (feature) => ({
    fillColor: getRiskColor(feature.properties?.flood_probability || 0),
    weight: 1.5,
    opacity: 0.9,
    color: 'rgba(255,255,255,0.25)',
    fillOpacity: 0.55,
  });

  const onEachFeature = (feature, layer) => {
    const { name, flood_probability, risk_level, main_factors } = feature.properties || {};
    const pct = Math.round((flood_probability || 0) * 100);
    const label = getRiskLabel(flood_probability || 0);
    const color = getRiskColor(flood_probability || 0);

    layer.bindTooltip(`
      <div style="min-width:160px">
        <div style="font-weight:700;font-size:14px;margin-bottom:6px">${name || 'Unknown'}</div>
        <div style="display:flex;align-items:center;gap:8px">
          <div style="width:10px;height:10px;border-radius:50%;background:${color};flex-shrink:0"></div>
          <span style="font-size:12px;color:#7fb3d3">Risk: </span>
          <span style="font-size:12px;font-weight:700;color:${color}">${label} (${pct}%)</span>
        </div>
        ${main_factors?.length ? `<div style="font-size:11px;color:#4a7a9b;margin-top:6px">${main_factors.slice(0, 2).join(' · ')}</div>` : ''}
        <div style="font-size:10px;color:#4a7a9b;margin-top:4px">Click for details →</div>
      </div>
    `, { sticky: true });

    layer.on({
      mouseover: (e) => e.target.setStyle({ fillOpacity: 0.8, weight: 2.5, color: 'rgba(255,255,255,0.7)' }),
      mouseout: (e) => e.target.setStyle({ fillOpacity: 0.55, weight: 1.5, color: 'rgba(255,255,255,0.25)' }),
      click: () => onDistrictClick && onDistrictClick(name),
    });
  };

  if (error) {
    return (
      <div className="map-wrapper">
        <div className="map-error-overlay">
          <span className="error-icon">⚠️</span>
          <h3>Failed to load map data</h3>
          <p>{error}</p>
          <button className="btn" onClick={loadData}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="map-wrapper">
      {/* Floating header */}
      <div className="map-header">
        <div className="app-brand">
          <div className="brand-icon">🌊</div>
          <div className="brand-text">
            <h1>FloodPulse</h1>
            <p>Karnataka Early Warning System</p>
          </div>
        </div>
        <div className="header-stats">
          <div className="stat-pill">
            <div className="dot red"></div>
            <span>{stats.critical} Critical</span>
          </div>
          <div className="stat-pill">
            <div className="dot orange"></div>
            <span>{stats.high} High Risk</span>
          </div>
          <div className="stat-pill">
            <div className="dot green"></div>
            <span>{loading ? 'Loading...' : 'Live · Updated Now'}</span>
          </div>
          <button
            className={`stat-pill toggle-pill ${showShelters ? 'active' : ''}`}
            onClick={() => setShowShelters(!showShelters)}
          >
            <span>⛺ {showShelters ? 'Hide' : 'Show'} Shelters</span>
          </button>
        </div>
      </div>

      {/* Risk Legend */}
      <div className="risk-legend">
        <h4>Flood Risk Level</h4>
        <div className="legend-bar"></div>
        <div className="legend-labels">
          <span>Low</span>
          <span>Moderate</span>
          <span>Critical</span>
        </div>
      </div>

      <MapContainer
        center={[14.5, 76.0]}
        zoom={7}
        zoomControl={false}
        style={{ height: "100%", width: "100%" }}
      >
        <ZoomControl position="bottomright" />
        <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} className="dark-tiles" />
        {geojson && (
          <GeoJSON
            key={JSON.stringify(geojson).slice(0, 100)}
            data={geojson}
            style={getStyle}
            onEachFeature={onEachFeature}
          />
        )}

        {/* Shelter markers */}
        {showShelters && shelters.map(s => (
          s.lat && s.lon && (
            <CircleMarker
              key={s.id}
              center={[s.lat, s.lon]}
              radius={6}
              pathOptions={{
                color: s.status === 'ACTIVE' ? '#2ed573' : s.status === 'FULL' ? '#ff4757' : '#ffa502',
                fillColor: s.status === 'ACTIVE' ? '#2ed573' : s.status === 'FULL' ? '#ff4757' : '#ffa502',
                fillOpacity: 0.8,
                weight: 2,
              }}
            >
              <Popup>
                <div style={{ fontFamily: 'Inter, sans-serif', color: '#1a1a2e' }}>
                  <strong>{s.name}</strong><br />
                  <span style={{ fontSize: '12px' }}>📍 {s.district} · {s.locality}</span><br />
                  <span style={{ fontSize: '12px' }}>Capacity: {s.capacity} · Status: {s.status}</span>
                </div>
              </Popup>
            </CircleMarker>
          )
        ))}
      </MapContainer>
    </div>
  );
}
