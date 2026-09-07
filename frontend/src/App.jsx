import React, { useState, useEffect, useCallback } from 'react';
import MapDashboard from './components/MapDashboard';
import ShelterPanel from './components/ShelterPanel';
import DashboardStats from './components/DashboardStats';
import AlertsView from './components/AlertsView';
import DistrictDetail from './components/DistrictDetail';

const VIEWS = {
  dashboard: { label: 'Dashboard', icon: '📊' },
  map: { label: 'Risk Map', icon: '🗺️' },
  alerts: { label: 'Alerts', icon: '🔔' },
  shelters: { label: 'Shelters', icon: '⛺' },
};

function useHashRoute() {
  const [route, setRoute] = useState(() => {
    const hash = window.location.hash.slice(1) || 'dashboard';
    return hash.split('/');
  });

  useEffect(() => {
    const onHashChange = () => {
      const hash = window.location.hash.slice(1) || 'dashboard';
      setRoute(hash.split('/'));
    };
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const navigate = useCallback((path) => {
    window.location.hash = path;
  }, []);

  return { view: route[0], param: route[1], navigate };
}

function App() {
  const { view, param, navigate } = useHashRoute();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleDistrictClick = useCallback((districtName) => {
    navigate(`district/${districtName}`);
  }, [navigate]);

  const renderView = () => {
    if (view === 'district' && param) {
      return <DistrictDetail district={decodeURIComponent(param)} onBack={() => navigate('map')} />;
    }
    switch (view) {
      case 'map':
        return <MapDashboard onDistrictClick={handleDistrictClick} />;
      case 'alerts':
        return <AlertsView onDistrictClick={handleDistrictClick} />;
      case 'shelters':
        return <ShelterPanel />;
      case 'dashboard':
      default:
        return <DashboardStats onDistrictClick={handleDistrictClick} onNavigate={navigate} />;
    }
  };

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <nav className={`sidebar ${sidebarOpen ? 'open' : 'collapsed'}`}>
        <div className="sidebar-brand" onClick={() => navigate('dashboard')}>
          <div className="brand-icon-nav">🌊</div>
          {sidebarOpen && (
            <div className="brand-text-nav">
              <span className="brand-name">FloodPulse</span>
              <span className="brand-sub">Karnataka EWS</span>
            </div>
          )}
        </div>

        <div className="nav-items">
          {Object.entries(VIEWS).map(([key, { label, icon }]) => (
            <button
              key={key}
              className={`nav-item ${view === key ? 'active' : ''}`}
              onClick={() => navigate(key)}
              title={label}
            >
              <span className="nav-icon">{icon}</span>
              {sidebarOpen && <span className="nav-label">{label}</span>}
            </button>
          ))}
        </div>

        <button
          className="sidebar-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          title={sidebarOpen ? 'Collapse' : 'Expand'}
        >
          {sidebarOpen ? '◀' : '▶'}
        </button>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {renderView()}
      </main>
    </div>
  );
}

export default App;
