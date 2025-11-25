# Hệ Thống Quản Lý Bãi Đỗ Xe Thông Minh

## Tổng Quan
Hệ thống quản lý bãi đỗ xe tự động sử dụng Raspberry Pi, camera OCR và cảm biến RFID để kiểm soát luồng xe ra vào.

## Cấu Trúc Dữ Liệu

### ParkingLog Model
**Mục đích**: Ghi nhận lịch sử xe vào bãi (entry log only)

**Lưu ý**: Model này chỉ lưu thông tin khi xe **vào**, không lưu thông tin xe ra. Khi xe ra, hệ thống sẽ:
- Tìm record theo `cardId`
- So sánh biển số
- Tính thời gian đỗ
- Xóa/đánh dấu record đã xử lý

- **licensePlate**: Biển số xe (bắt buộc, tự động chuyển thành chữ hoa)
- **entryTime**: Thời gian xe vào (bắt buộc, mặc định là thời điểm hiện tại)
- **cardId**: ID thẻ xe/RFID (bắt buộc)
- **image**: Ảnh chụp xe khi vào (tùy chọn)

## Workflow Hệ Thống

### 1. Luồng Xe Vào (Entry Lane)
**Thiết bị**: Raspberry Pi + Camera + RFID Reader

**Quy trình**:
1. Xe đến cổng vào
2. Camera chụp ảnh xe
3. OCR nhận diện biển số xe
4. RFID Reader đọc ID thẻ xe
5. Ghi nhận thời gian vào
6. Lưu dữ liệu vào MongoDB (licensePlate, entryTime, cardId, image)
7. Mở cổng cho xe vào

### 2. Luồng Xe Ra (Exit Lane)
**Thiết bị**: Raspberry Pi + Camera + RFID Reader

**Quy trình**:
1. Xe đến cổng ra
2. RFID Reader đọc ID thẻ xe
3. Camera chụp ảnh xe ra
4. OCR nhận diện biển số xe ra
5. Ghi nhận thời gian ra (tự động khi bắt đầu xử lý)
6. Gửi dữ liệu lên hệ thống: `cardId`, `exitLicensePlate`, `exitImage`, `exitTime`

**Kiểm tra**:
- Tra cứu database theo `cardId`
- So sánh biển số xe vào (từ database) với biển số xe ra (từ OCR)
- **Nếu khớp**: 
  - Tính toán thời gian đỗ (exitTime - entryTime)
  - Hiển thị đối chiếu hình ảnh vào/ra
  - Mở cổng cho xe ra
  - Xóa record trong database
  - Hiển thị thông tin: biển số, thẻ, thời gian vào/ra, thời lượng đỗ
- **Nếu không khớp**: 
  - Cảnh báo biển số không khớp (hiển thị cả 2 biển số)
  - Hiển thị hình ảnh xe ra để kiểm tra
  - Không mở cổng
  - Ghi log sự cố

**Dữ liệu đầu vào (từ Raspberry Pi)**:
- `cardId`: ID thẻ từ RFID Reader (bắt buộc)
- `exitLicensePlate`: Biển số xe từ OCR (bắt buộc)
- `exitImage`: URL hình ảnh xe ra (tùy chọn)
- `exitTime`: Thời gian ra (tự động tạo khi xử lý)

### 3. Tính Toán Thời Gian Đỗ
```
Thời gian đỗ = Thời gian ra - entryTime (từ database)
```

## Công Nghệ Sử dụng

### Backend
- **Node.js + Express**: API server
- **MongoDB + Mongoose**: Database
- **Socket.io**: Real-time communication (nếu cần)

### Frontend
- **React + Vite**: Giao diện quản lý
- **TailwindCSS**: Styling

### Raspberry Pi
- **Python**: Xử lý camera và GPIO
- **OpenCV**: Xử lý hình ảnh
- **OCR**: Nhận diện biển số
- **MFRC522/RC522**: RFID Reader

## Cấu Trúc Thư Mục
```
parking/
├── controller/        # API controllers
├── model/            # MongoDB models
├── frontend/         # React frontend
├── raspberry-pi/     # Python scripts cho Raspberry Pi
│   ├── camera_ocr_service.py  # Xử lý camera và OCR
│   ├── gpio_control.py        # Điều khiển GPIO/cổng
│   └── main.py               # Script chính
└── utils/           # Utilities và middleware
```

## API Endpoints (Dự Kiến)

### Entry
- `POST /api/parking/entry` - Ghi nhận xe vào
  - Body: `{ licensePlate, cardId, image, entryTime }`

### Exit
- **Frontend Service: `processExit(cardId, exitLicensePlate)`**
  - Tìm xe theo `cardId`
  - Validate biển số khớp
  - Xóa record nếu hợp lệ
  - Input bổ sung: `exitImage` (URL), `exitTime` (auto-generated)
  - Response: Thông tin xe vào/ra, thời gian đỗ, trạng thái, hình ảnh đối chiếu

### Query
- `GET /api/parking/logs` - Lấy danh sách log
- `GET /api/parking/current` - Xe đang đỗ
- `GET /api/parking/card/:cardId` - Tra cứu theo thẻ

## Yêu Cầu Cài Đặt

### Backend
```bash
npm install
```

### Frontend
```bash
cd frontend
npm install
```

### Raspberry Pi
```bash
pip install opencv-python pytesseract mfrc522
```

## Chạy Ứng Dụng

### Backend
```bash
npm start
```

### Frontend
```bash
cd frontend
npm run dev
```

### Raspberry Pi
```bash
cd raspberry-pi
python main.py
```

## Lưu Ý Bảo Mật
- Xác thực thẻ RFID trước khi xử lý
- Log tất cả các sự cố (biển số không khớp)
- Backup database định kỳ
- Mã hóa dữ liệu nhạy cảm nếu cần

## Tính Năng Mở Rộng (Future)
- [ ] Tính phí đỗ xe tự động
- [ ] Thông báo qua email/SMS
- [ ] Dashboard analytics
- [ ] API webhook cho hệ thống bên ngoài
- [ ] Multi-language support
