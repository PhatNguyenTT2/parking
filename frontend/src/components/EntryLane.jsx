import { ArrowDownCircle, Clock, Calendar, Bike } from 'lucide-react';

function EntryLane({ latestEntry, recentEntries }) {
  const formatTime = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('vi-VN');
  };

  return (
    <div className="bg-white rounded-xl overflow-hidden flex flex-col shadow-md border border-gray-200">
      {/* Header */}
      <div className="bg-emerald-500 text-white p-4 flex items-center gap-2">
        <ArrowDownCircle size={24} />
        <h2 className="text-xl font-semibold">Làn Vào - Xe Máy</h2>
      </div>

      {/* Image Display - hiển thị ảnh từ database */}
      <div className="m-4 bg-gray-100 rounded-lg overflow-hidden h-64 border border-gray-200">
        {latestEntry?.entryImagePath ? (
          <img
            src={latestEntry.entryImagePath}
            alt="Entry vehicle"
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <Bike size={48} className="mb-2 opacity-40" />
            <p className="text-sm">Chờ xe máy vào...</p>
          </div>
        )}
      </div>

      {/* Vehicle Info */}
      {latestEntry ? (
        <div className="mx-4 mb-4 bg-emerald-50 p-4 rounded-lg border border-emerald-200">
          <h3 className="text-base font-semibold mb-3 text-emerald-700 flex items-center gap-2">
            <Bike size={18} />
            Thông Tin Xe Máy Vào
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
              <span className="text-gray-600 text-sm">Biển số:</span>
              <span className="font-bold text-xl text-emerald-600 tracking-wider">
                {latestEntry.licensePlate}
              </span>
            </div>
            <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
              <span className="text-gray-600 text-sm">Ngày:</span>
              <span className="font-medium text-gray-800 flex items-center gap-1">
                <Calendar size={14} />
                {formatDate(latestEntry.entryTime)}
              </span>
            </div>
            <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
              <span className="text-gray-600 text-sm">Thời gian:</span>
              <span className="font-medium text-gray-800 flex items-center gap-1">
                <Clock size={14} />
                {formatTime(latestEntry.entryTime)}
              </span>
            </div>
            <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
              <span className="text-gray-600 text-sm">Trạng thái:</span>
              <span className="text-emerald-600 font-semibold flex items-center gap-1">
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                Đã vào
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="mx-4 mb-4 bg-gray-50 p-4 rounded-lg border border-gray-200">
          <p className="text-center text-gray-400">Chưa có xe máy vào</p>
        </div>
      )}

      {/* Recent Entries */}
      <div className="mx-4 mb-4 flex-1 overflow-auto">
        <h3 className="font-semibold mb-3 text-gray-700 flex items-center gap-2">
          <Clock size={18} />
          Lịch Sử Vào Gần Đây
        </h3>
        <div className="space-y-2">
          {recentEntries && recentEntries.length > 0 ? (
            recentEntries.map((vehicle, index) => (
              <div
                key={vehicle._id || index}
                className="bg-white p-3 rounded-lg flex justify-between items-center hover:bg-gray-50 transition-colors border border-gray-200"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xl">🏍️</span>
                  <span className="font-medium text-gray-800">{vehicle.licensePlate}</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-500">
                  <Clock size={14} />
                  <span>{formatTime(vehicle.entryTime)}</span>
                </div>
              </div>
            ))
          ) : (
            <p className="text-center text-gray-400 text-sm py-4">Chưa có lịch sử</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default EntryLane;
