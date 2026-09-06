import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, ZoomControl } from 'react-leaflet';

// Free OSM tiles with a dark, desaturated look — no API key needed
const TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
const TILE_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

// Karnataka districts with sample risk probabilities
const DISTRICT_GEOJSON = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: { name: "Uttara Kannada", district: "Coastal", flood_probability: 0.91 },
      geometry: {
        type: "Polygon",
        coordinates: [[[74.1,14.2],[75.2,14.2],[75.2,15.2],[74.1,15.2],[74.1,14.2]]]
      }
    },
    {
      type: "Feature",
      properties: { name: "Udupi", district: "Coastal", flood_probability: 0.82 },
      geometry: {
        type: "Polygon",
        coordinates: [[[74.5,13.3],[75.1,13.3],[75.1,13.9],[74.5,13.9],[74.5,13.3]]]
      }
    },
    {
      type: "Feature",
      properties: { name: "Dakshina Kannada", district: "Coastal", flood_probability: 0.78 },
      geometry: {
        type: "Polygon",
        coordinates: [[[74.7,12.6],[75.4,12.6],[75.4,13.2],[74.7,13.2],[74.7,12.6]]]
      }
    },
    {
      type: "Feature",
      properties: { name: "Kodagu", district: "Malnad", flood_probability: 0.65 },
      geometry: {
        type: "Polygon",
        coordinates: [[[75.5,12.2],[76.2,12.2],[76.2,12.8],[75.5,12.8],[75.5,12.2]]]
      }
    },
    {
      type: "Feature",
      properties: { name: "Belagavi", district: "North", flood_probability: 0.54 },
      geometry: {
        type: "Polygon",
        coordinates: [[[74.4,15.5],[75.6,15.5],[75.6,16.5],[74.4,16.5],[74.4,15.5]]]
      }
    },
    {
      type: "Feature",
      properties: { name: "Bengaluru Urban", district: "South", flood_probability: 0.35 },
      geometry: {
        type: "Polygon",
        coordinates: [[[77.4,12.8],[77.8,12.8],[77.8,13.2],[77.4,13.2],[77.4,12.8]]]
      }
    },
    {
      type: "Feature",
      properties: { name: "Mysuru", district: "South", flood_probability: 0.18 },
      geometry: {
        type: "Polygon",
        coordinates: [[[76.3,11.9],[76.9,11.9],[76.9,12.5],[76.3,12.5],[76.3,11.9]]]
      }
    },
    {
      type: "Feature",
      properties: { name: "Kalaburagi", district: "Hyderabad-Karnataka", flood_probability: 0.12 },
      geometry: {
        type: "Polygon",
        coordinates: [[[76.5,17.0],[77.7,17.0],[77.7,17.8],[76.5,17.8],[76.5,17.0]]]
      }
    }
  ]
};

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

export default function MapDashboard() {
  const getStyle = (feature) => ({
    fillColor: getRiskColor(feature.properties.flood_probability),
    weight: 1.5,
    opacity: 0.9,
    color: 'rgba(255,255,255,0.25)',
    fillOpacity: 0.55
  });

  const onEachFeature = (feature, layer) => {
    const { name, flood_probability } = feature.properties;
    const pct = Math.round(flood_probability * 100);
    const label = getRiskLabel(flood_probability);
    const color = getRiskColor(flood_probability);

    layer.bindTooltip(`
      <div style="min-width:140px">
        <div style="font-weight:700;font-size:14px;margin-bottom:6px">${name}</div>
        <div style="display:flex;align-items:center;gap:8px">
          <div style="width:10px;height:10px;border-radius:50%;background:${color};flex-shrink:0"></div>
          <span style="font-size:12px;color:#7fb3d3">Risk: </span>
          <span style="font-size:12px;font-weight:700;color:${color}">${label} (${pct}%)</span>
        </div>
      </div>
    `, { sticky: true });

    layer.on({
      mouseover: (e) => {
        e.target.setStyle({ fillOpacity: 0.8, weight: 2.5, color: 'rgba(255,255,255,0.7)' });
      },
      mouseout: (e) => {
        e.target.setStyle({ fillOpacity: 0.55, weight: 1.5, color: 'rgba(255,255,255,0.25)' });
      }
    });
  };

  // Count by risk
  const critical = DISTRICT_GEOJSON.features.filter(f => f.properties.flood_probability > 0.75).length;
  const high     = DISTRICT_GEOJSON.features.filter(f => f.properties.flood_probability > 0.5 && f.properties.flood_probability <= 0.75).length;

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
            <span>{critical} Critical Districts</span>
          </div>
          <div className="stat-pill">
            <div className="dot orange"></div>
            <span>{high} High Risk</span>
          </div>
          <div className="stat-pill">
            <div className="dot green"></div>
            <span>Live · Updated Now</span>
          </div>
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
        <TileLayer
          url={TILE_URL}
          attribution={TILE_ATTRIBUTION}
          className="dark-tiles"
        />
        <GeoJSON
          data={DISTRICT_GEOJSON}
          style={getStyle}
          onEachFeature={onEachFeature}
        />
      </MapContainer>
    </div>
  );
}
