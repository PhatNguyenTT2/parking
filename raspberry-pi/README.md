# 🚗 Raspberry Pi - Smart Parking System

Hệ thống điều khiển cổng vào/ra bãi đỗ xe thông minh sử dụng Raspberry Pi, Camera OCR và RFID Reader.

## 📋 Tổng Quan

Dự án này cung cấp giải pháp hoàn chỉnh để tự động hóa việc quản lý xe ra vào bãi đỗ:

- ✅ **Entry Lane**: Quét thẻ RFID → Chụp ảnh xe → Nhận diện biển số → Lưu vào database → Mở cổng
- ✅ **Exit Lane**: Quét thẻ RFID → Tìm thông tin xe → So sánh biển số → Xóa record → Mở cổng
- ✅ **Offline Mode**: Queue requests khi mất kết nối với backend
- ✅ **Visual Feedback**: LED và buzzer để thông báo trạng thái
- ✅ **Simulation Mode**: Chạy được trên máy tính để test (không cần phần cứng)

## 🏗️ Kiến Trúc Hệ Thống

```
raspberry-pi/
├── config/               # Cấu hình
│   ├── settings.py      # Cấu hình chung (API, timeout, v.v.)
│   └── pins.py          # GPIO pin mappings
├── services/            # Business logic
│   ├── rfid_service.py  # Xử lý RFID Reader
│   ├── camera_service.py# Xử lý Camera + OCR
│   ├── api_service.py   # Giao tiếp với Backend API
│   └── gpio_service.py  # Điều khiển GPIO (gate, LED, buzzer)
├── utils/               # Utilities
│   ├── logger.py        # Logging
│   ├── validators.py    # Data validation
│   └── queue_manager.py # Offline request queue
├── entry_lane.py        # Script chính cho cổng VÀO
├── exit_lane.py         # Script chính cho cổng RA
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variables template
```

## 🔧 Phần Cứng Cần Thiết

### Entry Lane / Exit Lane (mỗi cổng)
- 1x Raspberry Pi (3B+, 4, hoặc Zero W)
- 1x Camera Module hoặc USB Camera
- 1x MFRC522 RFID Reader
- 1x Servo Motor (SG90 hoặc tương tự)
- 2x LED (Green + Red)
- 1x Buzzer
- Dây nối, breadboard, nguồn điện

### Kết Nối GPIO

Xem chi tiết trong file `config/pins.py`:

```python
# Entry Lane
ENTRY_GATE_PIN = 17      # Servo motor
ENTRY_GREEN_LED = 27     # LED xanh
ENTRY_RED_LED = 22       # LED đỏ
ENTRY_BUZZER = 23        # Buzzer

# Exit Lane
EXIT_GATE_PIN = 18       # Servo motor
EXIT_GREEN_LED = 24      # LED xanh
EXIT_RED_LED = 25        # LED đỏ
EXIT_BUZZER = 8          # Buzzer

# RFID (SPI)
RFID_RST_PIN = 25
```

## 📦 Cài Đặt

### 1. Chuẩn Bị Raspberry Pi

```bash
# Cập nhật hệ thống
sudo apt update
sudo apt upgrade -y

# Cài đặt Python 3 và pip
sudo apt install python3 python3-pip -y

# Cài đặt Tesseract OCR
sudo apt install tesseract-ocr -y
sudo apt install tesseract-ocr-vie -y  # Vietnamese language pack

# Enable SPI (cho RFID Reader)
sudo raspi-config
# Interface Options -> SPI -> Enable
```

### 2. Clone Repository

```bash
cd ~
git clone <repository-url>
cd parking/raspberry-pi
```

### 3. Cài Đặt Dependencies

```bash
# Tạo virtual environment (khuyến nghị)
python3 -m venv venv
source venv/bin/activate

# Cài đặt packages
pip install -r requirements.txt
```

### 4. Cấu Hình

```bash
# Copy file .env mẫu
cp .env.example .env

# Chỉnh sửa cấu hình
nano .env
```

Cấu hình `.env`:
```bash
# URL của Backend API
BACKEND_URL=http://192.168.1.100:3001/api/parking/logs

# Loại lane: 'entry' hoặc 'exit'
LANE_TYPE=entry

# ID của lane (để phân biệt nếu có nhiều cổng)
LANE_ID=lane_1

# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
```

## 🚀 Chạy Hệ Thống

### Entry Lane (Cổng Vào)

```bash
cd ~/parking/raspberry-pi
python3 entry_lane.py
```

Quy trình:
1. 🔍 Chờ quét thẻ RFID
2. 📸 Chụp ảnh xe
3. 🔤 Nhận diện biển số bằng OCR
4. 📡 Gửi dữ liệu lên backend
5. ✅ Nếu thành công: LED xanh + Beep + Mở cổng (5s)
6. ❌ Nếu thất bại: LED đỏ nhấp nháy + Beep 3 lần

### Exit Lane (Cổng Ra)

```bash
cd ~/parking/raspberry-pi
python3 exit_lane.py
```

Quy trình:
1. 🔍 Chờ quét thẻ RFID
2. 🔎 Tìm thông tin xe trong database (theo cardId)
3. 📸 Chụp ảnh xe ra
4. 🔤 Nhận diện biển số
5. ⚖️ So sánh biển số vào/ra
6. ✅ Nếu khớp: Xóa record + LED xanh + Mở cổng
7. ❌ Nếu không khớp: LED đỏ + Không mở cổng

### Chạy Background (Tự động khởi động)

Tạo systemd service:

```bash
# Tạo service file cho Entry Lane
sudo nano /etc/systemd/system/parking-entry.service
```

Nội dung:
```ini
[Unit]
Description=Parking Entry Lane Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/parking/raspberry-pi
ExecStart=/home/pi/parking/raspberry-pi/venv/bin/python3 entry_lane.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Kích hoạt service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable parking-entry.service
sudo systemctl start parking-entry.service

# Xem log
sudo journalctl -u parking-entry.service -f
```

## 🧪 Testing & Simulation

Hệ thống hỗ trợ **Simulation Mode** để test trên máy tính (không cần phần cứng):

```bash
# Chạy trên Windows/Mac/Linux
python entry_lane.py
```

Simulation Mode tự động kích hoạt khi:
- Không có RFID Reader → Sử dụng card ID giả: `1234567890`
- Không có Camera → Tạo ảnh dummy
- Không có OCR → Trả về biển số giả: `29A12345`
- Không có GPIO → Log thông báo thay vì điều khiển phần cứng

## 📊 Logging

Logs được lưu tại `logs/`:
```
logs/
├── services.rfid_service.log
├── services.camera_service.log
├── services.api_service.log
├── services.gpio_service.log
├── __main__.log
```

Log format:
```
2025-11-25 14:30:45 | INFO     | services.rfid_service | ✅ Card detected: 1234567890
2025-11-25 14:30:47 | INFO     | services.camera_service | ✅ Image captured successfully
2025-11-25 14:30:48 | INFO     | services.camera_service | ✅ Valid license plate detected: 29A12345
2025-11-25 14:30:49 | INFO     | services.api_service | ✅ API request successful: 201
```

## 🔄 Offline Mode

Khi mất kết nối với backend, hệ thống tự động:
1. ✅ Queue requests vào file `data/offline_queue.json`
2. ⏳ Retry định kỳ khi có kết nối
3. 🔄 Xử lý hàng đợi khi khởi động

Cấu hình trong `config/settings.py`:
```python
ENABLE_OFFLINE_QUEUE = True
QUEUE_MAX_SIZE = 100
```

## 🛠️ Troubleshooting

### Lỗi RFID Reader không hoạt động
```bash
# Kiểm tra SPI đã enable
lsmod | grep spi

# Nếu chưa có, enable SPI
sudo raspi-config
# Interface Options -> SPI -> Enable
sudo reboot
```

### Lỗi Camera không detect
```bash
# Test camera
raspistill -o test.jpg

# Nếu dùng USB camera
ls /dev/video*

# Đổi camera ID trong config/pins.py
CAMERA_ID = 0  # Thử 0, 1, 2...
```

### Lỗi OCR không chính xác
```bash
# Cài thêm language pack
sudo apt install tesseract-ocr-vie

# Kiểm tra version
tesseract --version

# Test OCR trực tiếp
tesseract test.jpg output -l vie
```

### Lỗi GPIO Permission Denied
```bash
# Thêm user vào gpio group
sudo usermod -a -G gpio pi

# Hoặc chạy với sudo (không khuyến nghị)
sudo python3 entry_lane.py
```

## 🔧 Customization

### Thay đổi thời gian mở cổng

`config/settings.py`:
```python
GATE_OPEN_DURATION = 5  # seconds (mặc định 5s)
```

### Thay đổi GPIO pins

`config/pins.py`:
```python
ENTRY_GATE_PIN = 17  # Đổi thành pin khác nếu cần
```

### Thay đổi OCR confidence threshold

`config/settings.py`:
```python
OCR_CONFIDENCE_THRESHOLD = 0.6  # 0.0 - 1.0 (mặc định 0.6 = 60%)
```

## 📡 API Backend

Hệ thống giao tiếp với backend qua các endpoint:

### POST /api/parking/logs (Entry)
```json
{
  "licensePlate": "29A12345",
  "cardId": "1234567890",
  "image": "/path/to/image.jpg",
  "entryTime": 1732532400000
}
```

### GET /api/parking/logs?cardId=xxx (Find)
```json
{
  "success": true,
  "data": {
    "parkingLogs": [
      {
        "id": "abc123",
        "licensePlate": "29A12345",
        "cardId": "1234567890",
        "entryTime": 1732532400000
      }
    ]
  }
}
```

### DELETE /api/parking/logs/:id (Exit)
```json
{
  "success": true,
  "data": {
    "message": "Parking log deleted",
    "exitTime": 1732536000000,
    "duration": 3600000
  }
}
```

## 🎯 Tính Năng Nổi Bật

### ✅ Đã Implement
- [x] RFID card reading với retry logic
- [x] Camera capture + OCR license plate recognition
- [x] License plate validation (Vietnamese format)
- [x] API integration với retry và error handling
- [x] Offline mode với request queue
- [x] GPIO control (servo, LED, buzzer)
- [x] Visual/Audio feedback
- [x] Comprehensive logging
- [x] Simulation mode cho testing
- [x] Graceful shutdown

### 🚧 Có Thể Mở Rộng
- [ ] Web dashboard cho monitoring
- [ ] Real-time notifications (WebSocket)
- [ ] Face recognition bổ sung
- [ ] Automatic image cleanup (retention policy)
- [ ] Statistics và analytics
- [ ] Multiple camera support
- [ ] License plate correction UI

## 📝 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

Nếu có vấn đề hoặc câu hỏi, vui lòng tạo Issue trên GitHub.

---

**Happy Parking! 🚗🅿️**
