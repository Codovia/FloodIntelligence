/**
 * api.js — Centralized API service for FloodPulse frontend.
 * Wraps all backend endpoints with error handling.
 */
import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Health & Dashboard ─────────────────────────────
export const fetchHealth = () => api.get('/health').then(r => r.data);
export const fetchDashboardStats = () => api.get('/dashboard/stats').then(r => r.data);

// ── Districts ──────────────────────────────────────
export const fetchDistricts = () => api.get('/districts').then(r => r.data);

// ── Summary / Live Risk ────────────────────────────
export const fetchSummary = () => api.get('/summary').then(r => r.data);
export const fetchLiveRisk = (district) =>
  api.get('/live-risk', { params: district ? { district } : {} }).then(r => r.data);

// ── Rainfall ───────────────────────────────────────
export const fetchRainfallForecast = (district) =>
  api.get('/rainfall/forecast', { params: district ? { district } : {} }).then(r => r.data);

// ── Predictions ────────────────────────────────────
export const fetchAutoPrediction = (district) =>
  api.get('/predict/flood/auto', { params: { district } }).then(r => r.data);

// ── Map ────────────────────────────────────────────
export const fetchMapRisk = () => api.get('/map/risk').then(r => r.data);
export const fetchMapHotspots = () => api.get('/map/hotspots').then(r => r.data);

// ── Alerts ─────────────────────────────────────────
export const fetchAlerts = (district) =>
  api.get('/alerts', { params: district ? { district } : {} }).then(r => r.data);
export const fetchAlertEvents = (district, limit = 50) =>
  api.get('/alert-events', { params: { ...(district ? { district } : {}), limit } }).then(r => r.data);

// ── Shelters ───────────────────────────────────────
export const fetchShelters = (district, status) =>
  api.get('/shelters', { params: { ...(district ? { district } : {}), ...(status ? { status } : {}) } }).then(r => r.data);
export const createShelter = (data) => api.post('/shelters', data).then(r => r.data);
export const updateShelterStatus = (id, status, changedBy, reason) =>
  api.patch(`/shelters/${id}/status`, { status, changed_by: changedBy, reason }).then(r => r.data);

// ── Subscriptions ──────────────────────────────────
export const subscribe = (data) => api.post('/subscribe', data).then(r => r.data);
export const unsubscribe = (id) => api.delete(`/subscribe/${id}`).then(r => r.data);
export const fetchSubscribers = (district) =>
  api.get('/subscribe', { params: district ? { district } : {} }).then(r => r.data);

// ── Model ──────────────────────────────────────────
export const fetchModelPerformance = () => api.get('/model/performance').then(r => r.data);

// ── Localities ─────────────────────────────────────
export const fetchLocalities = (district) =>
  api.get('/localities', { params: district ? { district } : {} }).then(r => r.data);

export default api;
