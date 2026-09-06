import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import axios from 'axios';

// A darker OpenStreetMap tile configuration for our dark theme
const TILE_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
const TILE_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>';

export default function MapDashboard() {
  const [districtData, setDistrictData] = useState(null);

  useEffect(() => {
    // In a real scenario, we'd fetch the KGIS geojson from our backend or public URL
    // For now, we mock a single polygon over Karnataka to test the map render
    const mockGeoJson = {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          properties: { name: "Bengaluru Urban", flood_probability: 0.85 },
          geometry: {
            type: "Polygon",
            coordinates: [
              [[77.4, 12.8], [77.7, 12.8], [77.7, 13.1], [77.4, 13.1], [77.4, 12.8]]
            ]
          }
        },
        {
          type: "Feature",
          properties: { name: "Mysuru", flood_probability: 0.2 },
          geometry: {
            type: "Polygon",
            coordinates: [
              [[76.5, 12.2], [76.8, 12.2], [76.8, 12.5], [76.5, 12.5], [76.5, 12.2]]
            ]
          }
        }
      ]
    };
    setDistrictData(mockGeoJson);
  }, []);

  const getStyle = (feature) => {
    const prob = feature.properties.flood_probability;
    // Map probability (0-1) to a color gradient (Green -> Red)
    // We'll use a simplified mapping for the prototype
    let fillColor = '#10b981'; // Green
    if (prob > 0.4) fillColor = '#f59e0b'; // Orange
    if (prob > 0.7) fillColor = '#ef4444'; // Red

    return {
      fillColor: fillColor,
      weight: 2,
      opacity: 1,
      color: 'rgba(255,255,255,0.2)',
      fillOpacity: 0.6
    };
  };

  const onEachFeature = (feature, layer) => {
    const probPct = Math.round(feature.properties.flood_probability * 100);
    layer.bindTooltip(`
      <div style="font-family: Inter, sans-serif; text-align: center;">
        <strong>${feature.properties.name}</strong><br/>
        Risk: ${probPct}%
      </div>
    `, { sticky: true, className: 'custom-tooltip' });
  };

  return (
    <div className="map-wrapper">
      <div className="map-overlay">
        <h1>FloodPulse</h1>
        <p>Live Inundation Risk Map</p>
      </div>
      <MapContainer 
        center={[14.5, 76.0]} // Center of Karnataka roughly
        zoom={7} 
        zoomControl={false}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} />
        {districtData && (
          <GeoJSON 
            data={districtData} 
            style={getStyle}
            onEachFeature={onEachFeature}
          />
        )}
      </MapContainer>
    </div>
  );
}
