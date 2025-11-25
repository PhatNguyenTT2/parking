import { useState, useEffect } from 'react';
import './App.css';
import parkingLogService from '../services/parkingLogService';
import Header from './components/Header';
import EntryLane from './components/EntryLane';
import ExitLane from './components/ExitLane';

function App() {
  const [currentParking, setCurrentParking] = useState([]);
  const [todayLogs, setTodayLogs] = useState([]);
  const [latestEntry, setLatestEntry] = useState(null);

  // Fetch data
  const fetchData = async () => {
    try {
      // Get current parking (vehicles in parking lot)
      const currentData = await parkingLogService.getCurrentParking();

      // Get today's logs
      const todayData = await parkingLogService.getTodayLogs();

      console.log('App - currentData:', currentData);
      console.log('App - todayData:', todayData);

      const currentLogs = currentData.data?.parkingLogs || [];
      const todayLogsData = todayData.data?.parkingLogs || [];

      setCurrentParking(currentLogs);
      setTodayLogs(todayLogsData);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  // Auto-update latestEntry when todayLogs changes
  useEffect(() => {
    if (todayLogs.length > 0) {
      setLatestEntry(todayLogs[0]);
    } else {
      setLatestEntry(null);
    }
  }, [todayLogs]);

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header
        totalInside={currentParking.length}
        todayTotal={todayLogs.length}
      />

      <div className="flex-1 overflow-auto">
        <div className="grid grid-cols-2 gap-6 p-6 min-h-full">
          <EntryLane
            latestEntry={latestEntry}
            recentEntries={todayLogs.slice(0, 5)}
            onEntryAdded={fetchData}
          />

          <ExitLane
            onExitProcessed={fetchData}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
