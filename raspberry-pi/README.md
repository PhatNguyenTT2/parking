# Hướng dẫn triển khai lên Raspberry Pi 4

## Yêu cầu phần cứng

### 1. Raspberry Pi 4
- **Model**: Raspberry Pi 4 Model B
- **RAM**: 4GB hoặc 8GB (khuyến nghị)
- **Storage**: Thẻ SD 64GB hoặc SSD USB 3.0
- **OS**: Raspberry Pi OS 64-bit (Debian Bullseye)

### 2. Camera
- **Option 1**: Raspberry Pi Camera Module v2 (8MP)
- **Option 2**: USB Webcam (HD 720p trở lên)
- **Số lượng**: 2 camera (1 cho vào, 1 cho ra)

### 3. Relay Module
- **Loại**: 2-Channel 5V Relay Module
- **Mục đích**: Điều khiển barrier (cổng) vào/ra

### 4. LED và nút nhấn
- **LED xanh**: Báo cho phép vào
- **LED đỏ**: Báo từ chối
- **Nút nhấn**: Trigger thủ công (optional)

### 5. Barrier (Cổng)
- **Loại**: Servo motor barrier hoặc motor DC 12V
- **Nguồn**: Adapter 12V 2A

## Sơ đồ kết nối

```
Raspberry Pi 4
├── GPIO 17 → Relay CH1 → Barrier Entry
├── GPIO 27 → Relay CH2 → Barrier Exit
├── GPIO 22 → LED Green (220Ω resistor)
├── GPIO 23 → LED Red (220Ω resistor)
├── Camera 1 → CSI Port → Entry Camera
└── Camera 2 → USB Port → Exit Camera
```

## Cài đặt môi trường

### 1. Update system
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 2. Cài Node.js
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node --version  # Verify v18+
```

### 3. Cài MongoDB
**Option A: MongoDB Local (nặng hơn)**
```bash
# Raspberry Pi OS không hỗ trợ MongoDB chính thức
# Khuyến nghị dùng MongoDB Atlas (cloud)
```

**Option B: MongoDB Atlas (khuyến nghị)**
- Tạo free cluster tại https://cloud.mongodb.com
- Lấy connection string
- Update file `.env`

### 4. Cài Python dependencies
```bash
sudo apt install -y python3-pip python3-opencv tesseract-ocr
pip3 install opencv-python pytesseract pillow requests RPi.GPIO
```

### 5. Cài YOLOv5 (optional, nếu muốn detect biển số)
```bash
pip3 install torch torchvision
git clone https://github.com/ultralytics/yolov5
cd yolov5
pip3 install -r requirements.txt
```

## Deploy Backend

### 1. Copy project vào Raspberry Pi
```bash
# Từ máy PC
scp -r parking pi@raspberrypi.local:/home/pi/

# Hoặc clone từ Git
ssh pi@raspberrypi.local
cd /home/pi
git clone <your-repo-url> parking
cd parking
```

### 2. Cài dependencies và build
```bash
# Backend
npm install

# Frontend
cd frontend
npm install
npm run build
cd ..
```

### 3. Tạo file .env
```bash
nano .env
```

Nội dung:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/parking
PORT=3001
NODE_ENV=production
```

### 4. Tạo systemd service
```bash
sudo nano /etc/systemd/system/parking-backend.service
```

Nội dung:
```ini
[Unit]
Description=Parking Management Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/parking
ExecStart=/usr/bin/node /home/pi/parking/index.js
Restart=on-failure
Environment=NODE_ENV=production
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable và start service
sudo systemctl daemon-reload
sudo systemctl enable parking-backend
sudo systemctl start parking-backend
sudo systemctl status parking-backend

# Xem logs
sudo journalctl -u parking-backend -f
```

## Deploy Camera và GPIO Service

### 1. Copy scripts
```bash
cp raspberry-pi/*.py /home/pi/parking/
cd /home/pi/parking
```

### 2. Test GPIO
```bash
sudo python3 gpio_control.py
# Sẽ test mở/đóng barrier và LED
```

### 3. Test Camera
```bash
python3 camera_ocr_service.py
# Sẽ chụp ảnh và detect biển số mỗi 10 giây
```

### 4. Tạo systemd service cho camera
```bash
sudo nano /etc/systemd/system/parking-camera.service
```

Nội dung:
```ini
[Unit]
Description=Parking Camera OCR Service
After=parking-backend.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/parking
ExecStart=/usr/bin/python3 /home/pi/parking/camera_ocr_service.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable parking-camera
sudo systemctl start parking-camera
sudo systemctl status parking-camera
```

## Truy cập giao diện

### 1. Từ cùng mạng local
```
http://raspberrypi.local:3001
```

### 2. Từ ngoài mạng (cần port forwarding)
- Port forward router: 3001 → Raspberry Pi IP
- Hoặc dùng ngrok: `ngrok http 3001`

## Tối ưu hóa hiệu suất

### 1. Overclock Raspberry Pi (cẩn thận!)
```bash
sudo nano /boot/config.txt
```
Thêm:
```
over_voltage=6
arm_freq=2000
gpu_freq=750
```

### 2. Tăng swap memory
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### 3. Disable desktop (chạy headless)
```bash
sudo raspi-config
# System Options → Boot → Console
```

### 4. Sử dụng SSD thay vì SD card
- Boot từ USB SSD nhanh hơn nhiều
- Tuổi thọ cao hơn

## Monitoring và Debugging

### 1. Xem logs realtime
```bash
# Backend
sudo journalctl -u parking-backend -f

# Camera service
sudo journalctl -u parking-camera -f

# System logs
tail -f /var/log/syslog
```

### 2. Kiểm tra CPU/RAM usage
```bash
htop
```

### 3. Test API
```bash
# Từ Raspberry Pi
curl http://localhost:3001/api/vehicle/inside

# Từ máy khác
curl http://raspberrypi.local:3001/api/vehicle/inside
```

## Troubleshooting

### Lỗi: Camera not found
```bash
# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable

# Reboot
sudo reboot
```

### Lỗi: GPIO permission denied
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi
```

### Lỗi: MongoDB connection timeout
- Kiểm tra internet connection
- Whitelist IP của Raspberry Pi trong MongoDB Atlas
- Check firewall

### Lỗi: Node.js out of memory
```bash
# Tăng heap size
export NODE_OPTIONS="--max-old-space-size=2048"
```

## Bảo trì

### 1. Auto backup database
```bash
# Crontab backup MongoDB hàng ngày
crontab -e
```
Thêm:
```
0 2 * * * mongodump --uri="mongodb+srv://..." --out=/home/pi/backups/$(date +\%Y\%m\%d)
```

### 2. Auto cleanup images cũ
```bash
# Xóa ảnh > 30 ngày
find /home/pi/parking/public/images -type f -mtime +30 -delete
```

### 3. Update system định kỳ
```bash
sudo apt update && sudo apt upgrade -y
```

## Chi phí ước tính

| Thành phần | Giá tiền (VNĐ) |
|------------|----------------|
| Raspberry Pi 4 (4GB) | 1,500,000 |
| Camera Module x2 | 600,000 |
| Relay Module | 50,000 |
| LED + Resistor + Wires | 100,000 |
| Barrier Motor x2 | 2,000,000 |
| Nguồn + Box | 300,000 |
| **Tổng** | **~4,550,000** |

## Kết luận

Hệ thống hoàn toàn có thể chạy trên Raspberry Pi 4 với hiệu suất tốt. Key points:

✅ Node.js backend nhẹ, chạy mượt  
✅ React frontend đã build static  
✅ MongoDB Atlas (cloud) giảm tải cho RPi  
✅ GPIO control barriers đơn giản  
✅ Camera + OCR real-time khả thi  

**Khuyến nghị**: Dùng RPi 4 4GB + SSD + MongoDB Atlas
