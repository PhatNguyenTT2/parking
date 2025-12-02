# TÓM TẮT THIẾT KẾ GIAO DIỆN HỆ THỐNG QUẢN LÝ BÃI GIỮ XE MÁY

## 🎯 Mục Đích
Demo quan sát xe ra/vào bãi giữ xe, mô phỏng bằng **nhập tay** (thay thế cho quét thẻ/camera thực tế)

---

## 🏗️ Cấu Trúc Giao Diện

### 1. Header (Thanh Tiêu Đề)
**Thông tin hiển thị:**
- Số xe đang trong bãi
- Tổng lượt xe hôm nay
- Đồng hồ thời gian thực

---

### 2. Bố Cục Chính: Chia Đôi Màn Hình (Grid 2 Cột)

#### CỘT TRÁI - Làn Vào (EntryLane) - Màu Xanh Lá 🟢
**Chức năng:** Xử lý xe vào bãi

**Các thành phần:**
1. **Form nhập liệu** (ẩn/hiện bằng nút "Thêm Xe"):
   - Biển số xe (bắt buộc)
   - ID Thẻ (bắt buộc)
   - Link ảnh (tùy chọn)

2. **Danh sách xe trong bãi** (scroll được):
   - Hiển thị tất cả xe đang đỗ
   - Click vào xe → xem chi tiết

3. **Panel chi tiết xe được chọn**:
   - Biển số, ID thẻ
   - Thời gian vào, ngày vào
   - Hình ảnh (nếu có)

#### CỘT PHẢI - Làn Ra (ExitLane) - Màu Xanh Dương 🔵
**Chức năng:** Xử lý xe ra bãi

**Các thành phần:**
1. **Form nhập liệu** (luôn hiện):
   - ID Thẻ (bắt buộc)
   - Biển số xe nhận diện (bắt buộc - mô phỏng camera)
   - Link ảnh lúc ra (tùy chọn)

2. **Kết quả xử lý** (sau khi submit):
   - ✅ **Thành công:** Hiển thị thông tin đầy đủ
     - Biển số, ID thẻ
     - Thời gian vào/ra
     - Thời lượng đỗ xe
     - So sánh 2 ảnh (vào/ra)
   - ❌ **Thất bại:** Hiển thị lỗi
     - Biển số không khớp
     - Xe không tồn tại
     - Các lỗi khác

---

## 🔄 Luồng Hoạt Động

### Xe Vào:
1. Nhấn "Thêm Xe" → Form hiện ra
2. Nhập: Biển số + ID Thẻ (+ ảnh nếu có)
3. Submit → Xe được thêm vào danh sách
4. Tự động highlight xe mới nhất vừa thêm

### Xe Ra:
1. Nhập: ID Thẻ + Biển số nhận diện (+ ảnh nếu có)
2. Submit → Hệ thống kiểm tra:
   - ID thẻ có tồn tại?
   - Biển số có khớp?
3. Nếu OK → Hiển thị kết quả + Xóa khỏi danh sách bên trái
4. Nếu lỗi → Hiển thị thông báo lỗi

---

## 📦 Kiến Trúc Code

### Cấu Trúc Thư Mục
```
frontend/
├── services/
│   └── parkingLogService.js    # API Service Layer
│
└── src/
    ├── App.jsx                 # Component chính
    ├── components/
    │   ├── Header.jsx          # Thanh tiêu đề + thống kê
    │   ├── EntryLane.jsx       # Panel làn vào
    │   └── ExitLane.jsx        # Panel làn ra
    └── ...
```

### API Service Layer (`parkingLogService.js`)
```javascript
parkingLogService {
  createLog()      // Thêm xe vào
  processExit()    // Xử lý xe ra
  getAllLogs()     // Lấy danh sách xe
  getCurrentParking() // Lấy xe đang trong bãi
  getLogById()     // Xem chi tiết xe
}
```

### Component Chính (`App.jsx`)
**Responsibilities:**
- Quản lý state: danh sách xe, xe mới nhất
- Fetch data từ backend
- Render Header + 2 Lanes (Entry & Exit)
- Truyền props và callbacks cho các component con

**State Management:**
```javascript
const [allLogs, setAllLogs] = useState([]);      // Danh sách xe trong bãi
const [latestEntry, setLatestEntry] = useState(null); // Xe mới nhất vừa vào
```

### Components

#### Header.jsx
**Props:**
- `totalInside` - Số xe đang trong bãi
- `todayTotal` - Tổng lượt xe hôm nay

**Features:**
- Hiển thị thống kê real-time
- Đồng hồ cập nhật liên tục

#### EntryLane.jsx
**Props:**
- `latestEntry` - Xe mới nhất (để highlight)
- `allEntries` - Danh sách tất cả xe trong bãi
- `onEntryAdded` - Callback khi thêm xe thành công

**Features:**
- Form thêm xe (toggle hiện/ẩn)
- Danh sách xe với scroll
- Panel chi tiết xe được chọn
- Auto-select xe mới nhất
- Toast notification khi thêm thành công

**State:**
```javascript
const [showForm, setShowForm] = useState(false);
const [formData, setFormData] = useState({ licensePlate, cardId, image });
const [selectedEntry, setSelectedEntry] = useState(null);
```

#### ExitLane.jsx
**Props:**
- `onExitProcessed` - Callback khi xử lý xe ra thành công

**Features:**
- Form xử lý xe ra (luôn hiện)
- Kết quả xử lý (thành công/thất bại)
- So sánh ảnh vào/ra
- Tính toán thời lượng đỗ xe
- Validate biển số khớp

**State:**
```javascript
const [formData, setFormData] = useState({ cardId, exitLicensePlate, exitImage });
const [result, setResult] = useState(null);
const [exitTime, setExitTime] = useState(null);
```

---

## 🎨 Đặc Điểm UI/UX

### Design Principles
- **Màu sắc phân biệt:** 
  - 🟢 Xanh lá (Emerald) - Làn Vào
  - 🔵 Xanh dương (Blue) - Làn Ra
  
- **Real-time Updates:** 
  - Tự động refresh khi có xe vào/ra
  - Đồng hồ cập nhật liên tục
  
- **Responsive Layout:** 
  - Grid 2 cột responsive
  - Scroll riêng cho từng panel
  
- **User Feedback:** 
  - Toast notifications (success/error)
  - Highlight xe được chọn
  - Loading states khi processing
  
- **Visual Comparison:** 
  - Ảnh vào/ra đặt cạnh nhau
  - So sánh biển số entry vs exit

### Technology Stack
- **Framework:** React + Vite
- **Styling:** TailwindCSS
- **Icons:** Lucide React
- **HTTP Client:** Axios
- **State Management:** React Hooks (useState, useEffect)

---

## 🔧 Mô Phỏng vs Thực Tế

### Hiện Tại (Demo - Nhập Tay)
| Thao Tác | Mô Phỏng |
|----------|----------|
| Quét thẻ xe | Nhập ID thẻ vào form |
| Camera nhận diện biển số | Nhập biển số vào form |
| Chụp ảnh xe | Nhập link ảnh (optional) |

### Tương Lai (Production - Tự Động)
| Thao Tác | Thực Tế |
|----------|---------|
| Quét thẻ xe | RFID Reader tự động đọc |
| Camera nhận diện biển số | OCR/AI tự động nhận dạng |
| Chụp ảnh xe | Camera tự động chụp + upload |

---

## 📝 Notes

### Validation Rules
- **Biển số:** Required, tự động uppercase
- **ID Thẻ:** Required, unique identifier
- **Ảnh:** Optional, URL format

### Error Handling
- Xe không tồn tại khi xử lý ra
- Biển số không khớp
- Thẻ đã được sử dụng
- Network errors

### Data Flow
1. User Input → Component State
2. Component → API Service
3. API Service → Backend API
4. Backend Response → Component State
5. State Update → UI Re-render

---

**Tác giả:** Hệ thống được thiết kế đơn giản, trực quan, dễ demo và mô phỏng quy trình thực tế quản lý bãi xe!

**Ngày tạo:** December 2, 2025
