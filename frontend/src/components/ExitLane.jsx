import { useState } from 'react';
import { ArrowUpCircle, CheckCircle2, XCircle, Clock, Calendar, Timer, Bike, LogOut } from 'lucide-react';
import parkingLogService from '../../services/parkingLogService';

function ExitLane({ onExitProcessed }) {
  const [formData, setFormData] = useState({
    cardId: '',
    exitLicensePlate: '',
    exitImage: ''
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [exitTime, setExitTime] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirmExit = async () => {
    if (!result?.data?.id) return;

    setIsDeleting(true);
    try {
      await parkingLogService.deleteLog(result.data.id);

      // Show success and clear result
      setResult({
        ...result,
        confirmed: true
      });

      // Notify parent to refresh data
      if (onExitProcessed) onExitProcessed();

      // Auto-clear after 2 seconds
      setTimeout(() => {
        setResult(null);
        setExitTime(null);
      }, 2000);
    } catch (err) {
      setError('Lỗi khi xác nhận xe ra: ' + (err.response?.data?.error?.message || err.message));
    } finally {
      setIsDeleting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setIsProcessing(true);

    // Capture exit time when processing starts
    const currentExitTime = new Date();
    setExitTime(currentExitTime);

    try {
      const exitResult = await parkingLogService.processExit(
        formData.cardId,
        formData.exitLicensePlate.toUpperCase(),
        formData.exitImage || null
      );

      if (exitResult.success) {
        // Add exit image and exit time to result
        setResult({
          success: true,
          data: {
            ...exitResult.data,
            exitImage: formData.exitImage,
            actualExitTime: currentExitTime
          },
          message: exitResult.message
        });
        // Clear form inputs after successful processing
        setFormData({ cardId: '', exitLicensePlate: '', exitImage: '' });
        // DO NOT refresh here - wait for confirmation button
      } else {
        setError(exitResult.error.message);
        setResult({
          success: false,
          data: exitResult.data || null,
          error: exitResult.error,
          exitImage: formData.exitImage,
          exitTime: currentExitTime
        });
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error?.message || 'Có lỗi xảy ra khi xử lý xe ra';
      setError(errorMsg);
      setResult({
        success: false,
        error: { message: errorMsg },
        exitImage: formData.exitImage,
        exitTime: currentExitTime
      });
      console.error('Error processing exit:', err);
    } finally {
      setIsProcessing(false);
    }
  };

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
    <div className="bg-white rounded-xl overflow-hidden flex flex-col shadow-md border border-gray-200 h-full">
      {/* Header */}
      <div className="bg-blue-500 text-white p-4 flex items-center gap-2 flex-shrink-0">
        <ArrowUpCircle size={24} />
        <h2 className="text-xl font-semibold">Làn Ra - Xe Máy</h2>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Exit Form */}
        <div className="m-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold mb-3 text-blue-700 flex items-center gap-2">
            <LogOut size={18} />
            Xử Lý Xe Ra
          </h3>
          <form onSubmit={handleSubmit} className="space-y-3">
            {error && (
              <div className="bg-red-100 border border-red-300 text-red-700 px-3 py-2 rounded text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                ID Thẻ <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.cardId}
                onChange={(e) => setFormData({ ...formData, cardId: e.target.value })}
                placeholder="VD: CARD001"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={isProcessing}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Biển số xe (Nhận diện) <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.exitLicensePlate}
                onChange={(e) => setFormData({ ...formData, exitLicensePlate: e.target.value })}
                placeholder="VD: 59A1-2345"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={isProcessing}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                URL Hình ảnh xe ra (tùy chọn)
              </label>
              <input
                type="text"
                value={formData.exitImage}
                onChange={(e) => setFormData({ ...formData, exitImage: e.target.value })}
                placeholder="https://example.com/exit-image.jpg"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={isProcessing}
              />
            </div>

            {exitTime && (
              <div className="bg-blue-100 p-3 rounded-lg border border-blue-200">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-blue-700 font-medium">Thời gian ra:</span>
                  <span className="text-sm text-blue-900 font-semibold">
                    {formatTime(exitTime)}
                  </span>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={isProcessing}
              className="w-full bg-blue-600 text-white py-2 rouont-semibold hover:bg-blue-700 transinded-lg ftion-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isProcessing ? 'Đang xử lý...' : (
                <>
                  Xử Lý Xe Ra
                </>
              )}
            </button>
          </form>
        </div>

        {/* Exit Result */}
        {result && (
          <div className={`mx-4 mb-4 p-4 rounded-lg border ${result.success
            ? 'bg-emerald-50 border-emerald-200'
            : 'bg-red-50 border-red-200'
            }`}>
            <h3 className={`text-base font-semibold mb-3 flex items-center gap-2 ${result.success ? 'text-emerald-700' : 'text-red-700'
              }`}>
              <Bike size={18} />
              {result.success ? 'Kết Quả Xử Lý' : 'Lỗi Xử Lý'}
            </h3>

            {result.success ? (
              <div className="space-y-2">
                <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                  <span className="text-gray-600 text-sm">Biển số vào:</span>
                  <span className="font-bold text-lg text-blue-600 tracking-wider">
                    {result.data.licensePlate}
                  </span>
                </div>
                <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                  <span className="text-gray-600 text-sm">ID Thẻ:</span>
                  <span className="font-medium text-gray-800">
                    {result.data.cardId}
                  </span>
                </div>
                <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                  <span className="text-gray-600 text-sm">Thời gian vào:</span>
                  <span className="font-medium text-gray-800 flex items-center gap-1">
                    <Clock size={14} />
                    {formatTime(result.data.entryTime)}
                  </span>
                </div>
                <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                  <span className="text-gray-600 text-sm">Thời gian ra:</span>
                  <span className="font-medium text-gray-800 flex items-center gap-1">
                    <Clock size={14} />
                    {formatTime(result.data.actualExitTime || result.data.exitTime)}
                  </span>
                </div>
                <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                  <span className="text-gray-600 text-sm">Thời lượng đỗ:</span>
                  <span className="font-semibold text-blue-600 flex items-center gap-1">
                    <Timer size={14} />
                    {result.data.parkingDuration?.formatted || 'N/A'}
                  </span>
                </div>
                <div className="bg-emerald-100 p-3 rounded-lg border border-emerald-300 text-center">
                  <span className="text-emerald-700 font-semibold flex items-center justify-center gap-2">
                    <CheckCircle2 size={20} />
                    Cho phép xe ra - Biển số khớp
                  </span>
                </div>

                {/* Confirmation Button */}
                {!result.confirmed && (
                  <button
                    onClick={handleConfirmExit}
                    disabled={isDeleting}
                    className="w-full bg-emerald-600 text-white py-3 rounded-lg font-semibold hover:bg-emerald-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {isDeleting ? 'Đang xử lý...' : (
                      <>
                        Xác Nhận Cho Xe Ra
                      </>
                    )}
                  </button>
                )}

                {result.confirmed && (
                  <div className="bg-green-100 p-3 rounded-lg border border-green-300 text-center">
                    <span className="text-green-700 font-semibold flex items-center justify-center gap-2">
                      Đã xác nhận - Xe đã rời bãi
                    </span>
                  </div>
                )}

                {/* Image Comparison - Success Case */}
                {(result.data.entryImage || result.data.exitImage) && (
                  <div className="mt-3 border-t pt-3">
                    <p className="text-xs text-center mb-2 text-gray-600 font-semibold">Đối Chiếu Hình Ảnh</p>
                    <div className="grid grid-cols-2 gap-2">
                      {/* Entry Image */}
                      <div className="bg-gray-50 p-2 rounded-lg border border-gray-200">
                        <p className="text-xs text-center mb-1 text-emerald-600 font-semibold">Ảnh vào (DB)</p>
                        <div className="bg-white rounded h-32 overflow-hidden border border-gray-200">
                          {result.data.entryImage ? (
                            <img
                              src={result.data.entryImage}
                              alt="Entry"
                              className="w-full h-full object-contain"
                            />
                          ) : (
                            <div className="flex items-center justify-center h-full text-gray-400 text-xs">
                              Không có ảnh
                            </div>
                          )}
                        </div>
                        <p className="text-xs text-center mt-1 text-gray-500">
                          {formatTime(result.data.entryTime)}
                        </p>
                      </div>

                      {/* Exit Image */}
                      <div className="bg-gray-50 p-2 rounded-lg border border-gray-200">
                        <p className="text-xs text-center mb-1 text-blue-600 font-semibold">Ảnh ra</p>
                        <div className="bg-white rounded h-32 overflow-hidden border border-gray-200">
                          {result.data.exitImage ? (
                            <img
                              src={result.data.exitImage}
                              alt="Exit"
                              className="w-full h-full object-contain"
                            />
                          ) : (
                            <div className="flex items-center justify-center h-full text-gray-400 text-xs">
                              Không có ảnh
                            </div>
                          )}
                        </div>
                        <p className="text-xs text-center mt-1 text-gray-500">
                          {formatTime(result.data.actualExitTime || result.data.exitTime)}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-2">
                <div className="bg-red-100 p-3 rounded-lg border border-red-300">
                  <p className="text-red-700 font-semibold text-center flex items-center justify-center gap-2">
                    <XCircle size={20} />
                    {result.error?.code === 'LICENSE_PLATE_MISMATCH' ? 'Biển số không khớp!' : 'Không tìm thấy xe!'}
                  </p>
                </div>
                {result.error?.details && (
                  <div className="bg-white p-3 rounded-lg border border-gray-200">
                    <p className="text-sm text-gray-600 mb-2">Chi tiết:</p>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Biển số vào:</span>
                        <span className="font-medium text-emerald-600">{result.error.details.entry}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Biển số ra:</span>
                        <span className="font-medium text-red-600">{result.error.details.exit}</span>
                      </div>
                    </div>
                  </div>
                )}
                <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                  <p className="text-yellow-800 text-sm text-center">
                    Không cho phép xe ra - Vui lòng kiểm tra lại
                  </p>
                </div>

                {/* Force Exit Button for mismatch */}
                {result.error?.code === 'LICENSE_PLATE_MISMATCH' && result.data?.id && !result.confirmed && (
                  <button
                    onClick={handleConfirmExit}
                    disabled={isDeleting}
                    className="w-full bg-orange-600 text-white py-3 rounded-lg font-semibold hover:bg-orange-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {isDeleting ? 'Đang xử lý...' : (
                      <>
                        Buộc Cho Xe Ra (Bỏ qua lỗi)
                      </>
                    )}
                  </button>
                )}

                {result.confirmed && (
                  <div className="bg-green-100 p-3 rounded-lg border border-green-300 text-center">
                    <span className="text-green-700 font-semibold flex items-center justify-center gap-2">
                      <CheckCircle2 size={20} />
                      ✅ Đã xác nhận - Xe đã rời bãi
                    </span>
                  </div>
                )}

                {/* Image Comparison - Error Case */}
                <div className="mt-3 border-t pt-3">
                  <p className="text-xs text-center mb-2 text-gray-600 font-semibold">Đối Chiếu Hình Ảnh</p>
                  <div className="grid grid-cols-2 gap-2">
                    {/* Entry Image - từ database */}
                    <div className="bg-gray-50 p-2 rounded-lg border border-gray-200">
                      <p className="text-xs text-center mb-1 text-emerald-600 font-semibold">Ảnh vào (DB)</p>
                      <div className="bg-white rounded h-32 overflow-hidden border border-gray-200">
                        {result.data?.entryImage ? (
                          <img
                            src={result.data.entryImage}
                            alt="Entry from DB"
                            className="w-full h-full object-contain"
                          />
                        ) : (
                          <div className="flex items-center justify-center h-full text-gray-400 text-xs">
                            Không có ảnh vào
                          </div>
                        )}
                      </div>
                      {result.data?.licensePlate && (
                        <p className="text-xs text-center mt-1 text-gray-500">
                          Biển số: {result.data.licensePlate}
                        </p>
                      )}
                    </div>

                    {/* Exit Image */}
                    <div className="bg-gray-50 p-2 rounded-lg border border-gray-200">
                      <p className="text-xs text-center mb-1 text-red-600 font-semibold">Ảnh ra (Nhận diện)</p>
                      <div className="bg-white rounded h-32 overflow-hidden border border-gray-200">
                        {result.exitImage ? (
                          <img
                            src={result.exitImage}
                            alt="Exit attempt"
                            className="w-full h-full object-contain"
                          />
                        ) : (
                          <div className="flex items-center justify-center h-full text-gray-400 text-xs">
                            Không có ảnh ra
                          </div>
                        )}
                      </div>
                      <p className="text-xs text-center mt-1 text-gray-500">
                        {formatTime(result.exitTime)}
                        {result.error?.details && ` - ${result.error.details.exit}`}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default ExitLane;
