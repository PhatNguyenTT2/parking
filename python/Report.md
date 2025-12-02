## 3. CƠ SỞ LÝ THUYẾT MONGODB

### 3.1. MongoDB là gì?

MongoDB là một hệ quản trị cơ sở dữ liệu NoSQL (Not Only SQL) mã nguồn mở, sử dụng mô hình document-oriented thay vì mô hình quan hệ truyền thống.

### 3.2. Đặc điểm chính

**Document-Oriented (Hướng tài liệu)**

MongoDB lưu trữ dữ liệu dưới dạng documents (tài liệu) theo định dạng BSON (Binary JSON):

```json
{
   "_id": ObjectId("674468ea1234567890abcdef"),
   "licensePlate": "29A12345",
   "cardId": "1CACE0C634",
   "entryTime": ISODate("2025-12-02T08:30:15.000Z"),
   "exitTime": null,
   "entryImage": "http://localhost:3001/images/entry_123.jpg",
   "exitImage": null
}
```

**Schema-less (Linh hoạt cấu trúc)**

Các documents trong cùng một collection không bắt buộc phải có cùng cấu trúc, cho phép linh hoạt trong quá trình phát triển.

**Scalability (Khả năng mở rộng)**

- Horizontal Scaling: Sharding (phân tán dữ liệu qua nhiều server)
- Vertical Scaling: Tăng RAM/CPU của server

### 3.3. So sánh MongoDB vs SQL

| Đặc điểm | MongoDB (NoSQL) | MySQL/PostgreSQL (SQL) |
|----------|-----------------|------------------------|
| Data Model | Document (JSON-like) | Table (Rows & Columns) |
| Schema | Dynamic (linh hoạt) | Fixed (cố định) |
| Relationships | Embedded / Reference | Foreign Keys |
| Query Language | MongoDB Query Language | SQL |
| Scaling | Horizontal (Sharding) | Vertical (Scale up) |

## 4. THIẾT KẾ DATABASE

### 4.1. Phân tích yêu cầu

Hệ thống cần lưu trữ thông tin về mỗi lần xe vào bãi:

- **Biển số xe (licensePlate):** Định danh xe, tra cứu
- **Mã thẻ RFID (cardId):** Định danh duy nhất, ngăn gian lận
- **Thời gian vào (entryTime):** Tính duration, báo cáo
- **Thời gian ra (exitTime):** Null khi xe đang đỗ
- **Hình ảnh vào (entryImage):** Bằng chứng, tra cứu
- **Hình ảnh ra (exitImage):** Bằng chứng khi xe ra

### 4.2. Thiết kế Schema

**Pydantic Models (Validation)**

```python
from pydantic import BaseModel, Field
from typing import Optional

class ParkingLogCreate(BaseModel):
    cardId: str = Field(..., min_length=1)
    licensePlate: str = Field(..., min_length=1)
    entryImage: Optional[str] = Field(None)

class ParkingLogExit(BaseModel):
    cardId: str = Field(..., min_length=1)
    exitLicensePlate: str = Field(..., min_length=1)
    exitImage: Optional[str] = Field(None)
```

**MongoDB Schema**

```json
{
   "_id": ObjectId,
   "cardId": String (required),
   "licensePlate": String (required, uppercase),
   "entryTime": Date (default: now),
   "exitTime": Date (optional, null = still parking),
   "entryImage": String (optional),
   "exitImage": String (optional)
}
```

**Giải thích các thuộc tính**

**A. licensePlate (Biển số xe)**

- **type:** str - Kiểu dữ liệu chuỗi
- **Field(..., min_length=1):** Bắt buộc phải có
- Tự động uppercase trong controller

Luồng xử lý:

```
Input: "  59a1-2345  "
 → Pydantic validation: "59a1-2345"
 → Controller uppercase: "59A1-2345"
 → Lưu vào DB: "59A1-2345"
```

Lợi ích:
- Chuẩn hóa dữ liệu
- Query chính xác hơn
- Sử dụng index hiệu quả

**B. entryTime & exitTime (Thời gian vào/ra)**

- **type:** Date - Kiểu dữ liệu ngày giờ
- **entryTime:** Tự động set = datetime.now()
- **exitTime:** None = xe đang đỗ

**C. cardId (Mã thẻ RFID)**

- **type:** str - Kiểu dữ liệu chuỗi
- **Field(..., min_length=1):** Bắt buộc phải có
- **Validation:** Kiểm tra duplicate (exitTime = None)

Vai trò:
- UID duy nhất của thẻ RFID
- Key để tìm xe khi ra
- Ngăn chặn 1 thẻ vào 2 lần

**D. entryImage & exitImage (Hình ảnh)**

- **type:** Optional[str] - Lưu URL của ảnh (không bắt buộc)
- **entryImage:** Ảnh xe khi VÀO
- **exitImage:** Ảnh xe khi RA

Format:
```
http://localhost:3001/images/entry_123.jpg
```

### 4.3. Indexes (Tối ưu hóa truy vấn)

**Single Field Indexes**

```javascript
// Index theo biển số xe (tăng dần)
db.parkinglogs.createIndex({ "licensePlate": 1 })

// Index theo thời gian vào (giảm dần - mới nhất trước)
db.parkinglogs.createIndex({ "entryTime": -1 })

// Index theo mã thẻ RFID (tăng dần)
db.parkinglogs.createIndex({ "cardId": 1 })

// Index theo exitTime (query xe đang đỗ)
db.parkinglogs.createIndex({ "exitTime": 1 })
```

Mục đích:

| Index | Query thường dùng | Tốc độ |
|-------|-------------------|--------|
| { licensePlate: 1 } | Tìm xe theo biển số | O(log n) |
| { entryTime: -1 } | Lấy xe vào gần nhất | O(1) |
| { cardId: 1 } | Tìm xe theo thẻ RFID | O(log n) |
| { exitTime: 1 } | Lấy xe đang đỗ (null) | O(log n) |

**Compound Index**

```javascript
// Index kết hợp: cardId + exitTime
db.parkinglogs.createIndex({
   "cardId": 1,
   "exitTime": 1
})
```

Ứng dụng:

```python
# Query sử dụng compound index (rất nhanh)
db.parkinglogs.find({
   "cardId": "CARD001",
   "exitTime": None
})
```

### 4.4. Transform Output

```python
# Convert ObjectId to string
for log in logs:
    log["id"] = str(log.pop("_id"))
```

Trước transform:

```json
{
   "_id": ObjectId("674468ea1234567890abcdef"),
   "licensePlate": "29A12345"
}
```

Sau transform:

```json
{
   "id": "674468ea1234567890abcdef",
   "licensePlate": "29A12345"
}
```

## 5. XÂY DỰNG CHƯƠNG TRÌNH QUẢN LÝ

### 5.1. API Endpoints

#### POST /api/parking/logs (Xe vào)

**Mục đích:** Tạo log mới khi xe vào bãi

**Request:**

```http
POST /api/parking/logs HTTP/1.1
Content-Type: application/json

{
  "licensePlate": "59A1-2345",
  "cardId": "CARD001",
  "entryImage": "http://example.com/entry_123.jpg"
}
```

**Controller Logic:**

1. Validation: Pydantic tự động validate
2. Check duplicate: Kiểm tra cardId đã được sử dụng chưa (exitTime = None)
3. Create log: Tạo document mới
4. Save to DB: Lưu vào MongoDB
5. Return response: Trả về kết quả

**Response (Success - 201 Created):**

```json
{
  "success": true,
  "data": {
    "id": "674468ea1234567890abcdef",
    "licensePlate": "59A1-2345",
    "cardId": "CARD001",
    "entryTime": "2025-12-02T08:30:15.000Z",
    "exitTime": null,
    "entryImage": "http://example.com/entry_123.jpg"
  }
}
```

**Response (Error - 400 Bad Request):**

```json
{
  "detail": "Card CARD001 already has an active entry"
}
```

#### GET /api/parking/logs/current (Xe đang đỗ)

**Mục đích:** Lấy danh sách tất cả xe đang trong bãi (exitTime = null)

**Response:**

```json
{
  "success": true,
  "data": {
    "parkingLogs": [
      {
        "id": "674468ea1234567890abcdef",
        "licensePlate": "59A1-2345",
        "cardId": "CARD001",
        "entryTime": "2025-12-02T08:30:15.000Z",
        "exitTime": null
      }
    ]
  }
}
```

#### PUT /api/parking/logs/exit (Validate xe ra)

**Mục đích:** Validate thông tin xe ra (KHÔNG xóa log - chỉ validate)

**Request:**

```http
PUT /api/parking/logs/exit HTTP/1.1
Content-Type: application/json

{
  "cardId": "CARD001",
  "exitLicensePlate": "59A1-2345",
  "exitImage": "http://example.com/exit_123.jpg"
}
```

**Process:**

1. Find log by cardId (exitTime = null)
2. Validate license plate matches
3. Return vehicle data (không update DB)

**Response (Success):**

```json
{
  "success": true,
  "data": {
    "id": "674468ea1234567890abcdef",
    "licensePlate": "59A1-2345",
    "cardId": "CARD001",
    "entryTime": "2025-12-02T08:30:15.000Z",
    "exitImage": "http://example.com/exit_123.jpg"
  },
  "message": "Exit validation successful - please confirm to delete log"
}
```

**Response (Error - 400 Bad Request):**

```json
{
  "detail": "License plate mismatch. Expected: 59A1-2345, Got: 59A1-2346"
}
```

#### DELETE /api/parking/logs/:id (Xác nhận xe ra)

**Mục đích:** Xóa log khi user xác nhận cho xe ra

**Response:**

```json
{
  "success": true,
  "message": "Log 674468ea1234567890abcdef deleted successfully"
}
```

## 6. KẾT QUẢ ĐẠT ĐƯỢC

### 6.1. Link demo

https://parking-backend-g5m5.onrender.com/docs
