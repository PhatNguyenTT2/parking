import { useState, useEffect } from 'react';
import './App.css';
import { getCarsInside, getTodayHistory } from '../services/vehicleApi';
import Header from './components/Header';
import EntryLane from './components/EntryLane';
import ExitLane from './components/ExitLane';

function App() {
  const [carsInside, setCarsInside] = useState([]);
  const [todayHistory, setTodayHistory] = useState([]);
  const [latestEntry, setLatestEntry] = useState(null);
  const [latestExit, setLatestExit] = useState(null);

  // Fetch data mỗi 3 giây
  useEffect(() => {
    const fetchData = async () => {
      try {
        const insideData = await getCarsInside();
        const historyData = await getTodayHistory();

        console.log('App - insideData:', insideData);
        console.log('App - historyData:', historyData);

        setCarsInside(insideData.vehicles || []);
        setTodayHistory(historyData.vehicles || []);

        // Lấy xe vào gần nhất
        const recentEntries = (historyData.vehicles || []).filter(v => v.status === 'in');
        if (recentEntries.length > 0) {
          setLatestEntry(recentEntries[0]);
        }

        // Lấy xe ra gần nhất
        const recentExits = (historyData.vehicles || []).filter(v => v.status === 'out');
        if (recentExits.length > 0) {
          setLatestExit(recentExits[0]);
          console.log('App - Latest exit vehicle:', recentExits[0]);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        totalInside={carsInside.length}
        todayTotal={todayHistory.length}
      />

      <div className="grid grid-cols-2 gap-6 p-6 h-[calc(100vh-100px)]">
        <EntryLane
          latestEntry={latestEntry}
          recentEntries={(todayHistory || []).filter(v => v.status === 'in').slice(0, 5)}
        />

        <ExitLane
          latestExit={latestExit}
        />
      </div>
    </div>
  );
}

export default App;
