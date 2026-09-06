import React from 'react';
import MapDashboard from './components/MapDashboard';
import ShelterPanel from './components/ShelterPanel';

function App() {
  return (
    <div className="dashboard-container">
      <MapDashboard />
      <ShelterPanel />
    </div>
  );
}

export default App;
