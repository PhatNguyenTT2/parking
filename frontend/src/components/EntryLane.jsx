import { useState, useEffect } from 'react';
import { ArrowDownCircle, Clock, Calendar, Bike, Plus, X } from 'lucide-react';
import parkingLogService from '../../services/parkingLogService';

function EntryLane({ latestEntry, allEntries, onEntryAdded }) {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    licensePlate: '',
    cardId: '',
    image: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedEntry, setSelectedEntry] = useState(null);

  // Tự động cập nhật selectedEntry khi có xe mới vào (latestEntry thay đổi)
  useEffect(() => {
    if (latestEntry) {
      setSelectedEntry(latestEntry);
    }
  }, [latestEntry]); // Depend on the whole object to catch all changes

  const handleEntryClick = async (entry) => {
    try {
      // Set ngay entry từ list để highlight nhanh (optimistic update)
      setSelectedEntry(entry);

      // Fetch chi tiết xe theo ID từ server
      const result = await parkingLogService.getLogById(entry._id || entry.id);
      if (result.success && result.data) {
        // Cập nhật với data mới từ server, giữ nguyên _id để highlight đúng
        setSelectedEntry(result.data);
      }
    } catch (error) {
      console.error('Error fetching entry details:', error);
      // Nếu lỗi thì vẫn giữ entry từ list (đã set ở trên)
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsSubmitting(true);

    try {
      const result = await parkingLogService.createLog({
        licensePlate: formData.licensePlate.toUpperCase(),
        cardId: formData.cardId,
        image: formData.image || null
      });

      if (result.success) {
        // Show success message
        setSuccess(`Xe ${formData.licensePlate.toUpperCase()} đã vào bãi thành công!`);
        // Reset form
        setFormData({ licensePlate: '', cardId: '', image: '' });
        setShowForm(false);
        // Notify parent to refresh data - MUST run to update list
        if (onEntryAdded) {
          await onEntryAdded();
        }
        // Set the newly created entry as selected
        if (result.data) {
          setSelectedEntry(result.data);
        }
        // Auto-hide success message after 3 seconds
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Có lỗi xảy ra khi thêm xe');
      console.error('Error adding entry:', err);
    } finally {
      setIsSubmitting(false);
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

  return (
    <div className="bg-white rounded-xl overflow-hidden flex flex-col shadow-md border border-gray-200 h-full">
      {/* Header */}
      <div className="bg-emerald-500 text-white p-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <ArrowDownCircle size={24} />
          <h2 className="text-xl font-semibold">Làn Vào - Xe Máy</h2>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-white text-emerald-600 px-4 py-2 rounded-lg font-semibold hover:bg-emerald-50 transition-colors flex items-center gap-2"
        >
          {showForm ? <X size={18} /> : <Plus size={18} />}
          {showForm ? 'Đóng' : 'Thêm Xe'}
        </button>
      </div>

      {/* Success Message Toast */}
      {success && (
        <div className="m-4 mb-0 bg-emerald-100 border border-emerald-300 text-emerald-700 px-4 py-3 rounded-lg flex items-center gap-2 animate-pulse">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span className="font-medium">{success}</span>
        </div>
      )}

      {/* Entry Form */}
      {showForm && (
        <div className="m-4 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
          <h3 className="font-semibold mb-3 text-emerald-700">Thêm Xe Vào</h3>
          <form onSubmit={handleSubmit} className="space-y-3">
            {error && (
              <div className="bg-red-100 border border-red-300 text-red-700 px-3 py-2 rounded text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Biển số xe <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.licensePlate}
                onChange={(e) => setFormData({ ...formData, licensePlate: e.target.value })}
                placeholder="VD: 59A1-2345"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>

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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                URL Hình ảnh (tùy chọn)
              </label>
              <input
                type="text"
                value={formData.image}
                onChange={(e) => setFormData({ ...formData, image: e.target.value })}
                placeholder="https://example.com/image.jpg"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-emerald-600 text-white py-2 rounded-lg font-semibold hover:bg-emerald-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Đang thêm...' : 'Thêm Xe Vào'}
            </button>
          </form>
        </div>
      )}

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Image Display - hiển thị ảnh từ database */}
        <div className="m-4 bg-gray-100 rounded-lg overflow-hidden h-64 border border-gray-200 flex-shrink-0">
          {(selectedEntry || latestEntry)?.entryImage ? (
            <img
              src={(selectedEntry || latestEntry).entryImage}
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
        {(selectedEntry || latestEntry) ? (
          <div className="mx-4 mb-4 bg-emerald-50 p-4 rounded-lg border border-emerald-200">
            <h3 className="text-base font-semibold mb-3 text-emerald-700 flex items-center gap-2">
              <Bike size={18} />
              Thông Tin Xe Máy Vào
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                <span className="text-gray-600 text-sm">Biển số:</span>
                <span className="font-bold text-xl text-emerald-600 tracking-wider">
                  {(selectedEntry || latestEntry).licensePlate}
                </span>
              </div>
              <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                <span className="text-gray-600 text-sm">ID Thẻ:</span>
                <span className="font-medium text-gray-800">
                  {(selectedEntry || latestEntry).cardId}
                </span>
              </div>
              <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                <span className="text-gray-600 text-sm">Ngày:</span>
                <span className="font-medium text-gray-800 flex items-center gap-1">
                  <Calendar size={14} />
                  {formatDate((selectedEntry || latestEntry).entryTime)}
                </span>
              </div>
              <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                <span className="text-gray-600 text-sm">Thời gian:</span>
                <span className="font-medium text-gray-800 flex items-center gap-1">
                  <Clock size={14} />
                  {formatTime((selectedEntry || latestEntry).entryTime)}
                </span>
              </div>
              <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                <span className="text-gray-600 text-sm">Trạng thái:</span>
                <span className="text-emerald-600 font-semibold flex items-center gap-1">
                  <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                  Đang đỗ
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="mx-4 mb-4 bg-gray-50 p-4 rounded-lg border border-gray-200">
            <p className="text-center text-gray-400">Chưa có xe máy vào</p>
          </div>
        )}

        {/* All Parking Logs */}
        <div className="mx-4 mb-4">
          <h3 className="font-semibold mb-3 text-gray-700 flex items-center gap-2">
            <Clock size={18} />
            Toàn Bộ Xe Trong Bãi ({allEntries?.length || 0})
          </h3>
          <div className="space-y-2">
            {allEntries && allEntries.length > 0 ? (
              allEntries.map((vehicle, index) => {
                // So sánh _id hoặc id, chuyển về string để đảm bảo khớp chính xác
                const vehicleId = String(vehicle._id || vehicle.id);
                const selectedId = String(selectedEntry?._id || selectedEntry?.id || '');
                const isSelected = vehicleId === selectedId;
                const isLatest = index === 0;

                return (
                  <div
                    key={vehicle._id || vehicle.id || index}
                    onClick={() => handleEntryClick(vehicle)}
                    className={`p-3 rounded-lg flex justify-between items-center transition-colors border cursor-pointer ${isSelected
                      ? 'bg-emerald-100 border-emerald-400 shadow-sm'
                      : 'bg-white border-gray-200 hover:bg-gray-50 hover:border-emerald-300'
                      }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-xl">🏍️</span>
                      <span className={`font-medium ${isSelected ? 'text-emerald-700' : 'text-gray-800'}`}>
                        {vehicle.licensePlate}
                      </span>
                      {isLatest && (
                        <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full">Mới nhất</span>
                      )}
                    </div>
                    <div className="flex items-center gap-1 text-sm text-gray-500">
                      <Clock size={14} />
                      <span>{formatTime(vehicle.entryTime)}</span>
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="text-center text-gray-400 text-sm py-4">Chưa có xe trong bãi</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default EntryLane;
