import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function ShelterPanel() {
  const [shelters, setShelters] = useState([]);

  useEffect(() => {
    // Fetch real data from our FastAPI backend once it's fully populated
    // For now we mock the API response shape that our /api/shelters endpoint returns
    setShelters([
      { id: 1, name: "Kanteerava Indoor Stadium", capacity: 500, current_occupancy: 450, status: "ACTIVE" },
      { id: 2, name: "Mysuru Town Hall", capacity: 200, current_occupancy: 200, status: "FULL" },
      { id: 3, name: "Hubli Primary School", capacity: 150, current_occupancy: 0, status: "CANDIDATE" }
    ]);
  }, []);

  return (
    <div className="side-panel">
      <h2>Emergency Shelters</h2>
      
      {shelters.map(shelter => {
        const occupancyPct = Math.round((shelter.current_occupancy / shelter.capacity) * 100);
        return (
          <div key={shelter.id} className="shelter-card">
            <div className="shelter-header">
              <span className="shelter-name">{shelter.name}</span>
              <span className={`badge ${shelter.status.toLowerCase()}`}>
                {shelter.status}
              </span>
            </div>
            
            <p>Occupancy: {shelter.current_occupancy} / {shelter.capacity}</p>
            <div className="progress-bar-bg">
              <div 
                className="progress-bar-fill" 
                style={{ 
                  width: `${occupancyPct}%`,
                  background: shelter.status === 'FULL' ? 'var(--alert-red)' : undefined
                }}
              ></div>
            </div>

            {shelter.status === 'CANDIDATE' && (
              <button className="btn">Activate Shelter</button>
            )}
          </div>
        );
      })}
    </div>
  );
}
