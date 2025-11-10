import { ArrowUpCircle, CheckCircle2, XCircle, Clock, Calendar, Timer, Bike } from 'lucide-react';

function ExitLane({ latestExit }) {
  const canExit = latestExit?.status === 'out';

  // Debug: Log dữ liệu để kiểm tra
  console.log('ExitLane - latestExit:', latestExit);
  console.log('ExitLane - entryImagePath:', latestExit?.entryImagePath);
  console.log('ExitLane - exitImagePath:', latestExit?.exitImagePath);

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

  const calculateDuration = (entry, exit) => {
    if (!entry || !exit) return 'N/A';
    const duration = Math.round((new Date(exit) - new Date(entry)) / 60000); // minutes
    const hours = Math.floor(duration / 60);
    const minutes = duration % 60;

    if (hours > 0) {
      return `${hours} giờ ${minutes} phút`;
    }
    return `${minutes} phút`;
  };

  return (
    <div className="bg-white rounded-xl overflow-hidden flex flex-col shadow-md border border-gray-200">
      {/* Header */}
      <div className="bg-blue-500 text-white p-4 flex items-center gap-2">
        <ArrowUpCircle size={24} />
        <h2 className="text-xl font-semibold">Làn Ra - Xe Máy</h2>
      </div>

      {/* Exit Info */}
      {latestExit ? (
        <div className={`mx-4 mb-4 p-4 rounded-lg border ${canExit
          ? 'bg-emerald-50 border-emerald-200'
          : 'bg-red-50 border-red-200'
          }`}>
          <h3 className={`text-base font-semibold mb-3 flex items-center gap-2 ${canExit ? 'text-emerald-700' : 'text-red-700'
            }`}>
            <Bike size={18} />
            Thông Tin Xe Máy Ra
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
              <span className="text-gray-600 text-sm">Biển số:</span>
              <span className="font-bold text-xl text-blue-600 tracking-wider">
                {latestExit.licensePlate}
              </span>
            </div>
            <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
              <span className="text-gray-600 text-sm">Ngày vào:</span>
              <span className="font-medium text-gray-800 flex items-center gap-1">
                <Calendar size={14} />
                {formatDate(latestExit.entryTime)}
              </span>
            </div>
            <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
              <span className="text-gray-600 text-sm">Thời gian vào:</span>
              <span className="font-medium text-gray-800 flex items-center gap-1">
                <Clock size={14} />
                {formatTime(latestExit.entryTime)}
              </span>
            </div>
            {latestExit.exitTime && (
              <>
                <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                  <span className="text-gray-600 text-sm">Thời gian ra:</span>
                  <span className="font-medium text-gray-800 flex items-center gap-1">
                    <Clock size={14} />
                    {formatTime(latestExit.exitTime)}
                  </span>
                </div>
                <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                  <span className="text-gray-600 text-sm">Thời lượng:</span>
                  <span className="font-semibold text-blue-600 flex items-center gap-1">
                    <Timer size={14} />
                    {calculateDuration(latestExit.entryTime, latestExit.exitTime)}
                  </span>
                </div>
              </>
            )}
            <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
              <span className="text-gray-600 text-sm">Trạng thái:</span>
              {canExit ? (
                <span className="text-emerald-600 font-semibold flex items-center gap-1">
                  <CheckCircle2 size={18} />
                  Cho ra
                </span>
              ) : (
                <span className="text-red-600 font-semibold flex items-center gap-1">
                  <XCircle size={18} />
                  Không cho ra
                </span>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="mx-4 mb-4 bg-gray-50 p-4 rounded-lg border border-gray-200">
          <p className="text-center text-gray-400">Chưa có xe máy ra</p>
        </div>
      )}

      {/* Image Comparison */}
      {latestExit && (
        <div className="mx-4 mb-4 flex-1">
          <h3 className="font-semibold mb-3 text-gray-700 flex items-center gap-2">
            <CheckCircle2 size={18} />
            Đối Chiếu Hình Ảnh
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {/* Entry Image */}
            <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
              <p className="text-xs text-center mb-2 text-emerald-600 font-semibold">Ảnh vào</p>
              <div className="bg-white rounded h-36 overflow-hidden border border-gray-200">
                {latestExit.entryImagePath ? (
                  <img
                    src={latestExit.entryImagePath}
                    alt="Entry"
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-400 text-xs">
                    Không có ảnh
                  </div>
                )}
              </div>
              <p className="text-xs text-center mt-2 text-gray-500">
                {formatTime(latestExit.entryTime)}
              </p>
            </div>

            {/* Exit Image */}
            <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
              <p className="text-xs text-center mb-2 text-blue-600 font-semibold">Ảnh ra</p>
              <div className="bg-white rounded h-36 overflow-hidden border border-gray-200">
                {latestExit.exitImagePath ? (
                  <img
                    src={latestExit.exitImagePath}
                    alt="Exit"
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-400 text-xs">
                    Không có ảnh
                  </div>
                )}
              </div>
              <p className="text-xs text-center mt-2 text-gray-500">
                {formatTime(latestExit.exitTime)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ExitLane;
