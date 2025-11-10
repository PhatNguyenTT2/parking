import { Bike, Activity } from 'lucide-react';

function Header({ totalInside, todayTotal }) {
  const currentTime = new Date().toLocaleString('vi-VN', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center mb-3">
          <div className="flex items-center gap-3">
            <div className="bg-emerald-500 p-2 rounded-lg">
              <Bike size={28} className="text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-800">Hệ Thống Quản Lý Bãi Giữ Xe Máy</h1>
          </div>

          <div className="text-sm text-gray-600">
            {currentTime}
          </div>
        </div>

        <div className="flex gap-4">
          <div className="bg-emerald-50 border border-emerald-200 px-4 py-2 rounded-lg">
            <Activity size={16} className="inline mr-2 text-emerald-600" />
            <span className="font-medium text-gray-700">Xe máy trong bãi: </span>
            <span className="font-bold text-emerald-600">{totalInside}</span>
          </div>
          <div className="bg-blue-50 border border-blue-200 px-4 py-2 rounded-lg">
            <span className="font-medium text-gray-700">Tổng lượt hôm nay: </span>
            <span className="font-bold text-blue-600">{todayTotal}</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
