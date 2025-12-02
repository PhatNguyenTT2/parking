3. CƠ SỞ LÝ THUYẾT MONGODB
3.1. MongoDB là gì?
MongoDB là một hệ quản trị cơ sở dữ liệu NoSQL (Not Only SQL) mã nguồn mở, sử dụng mô hình document-oriented thay vì mô hình quan hệ truyền thống.
3.2. Đặc điểm chính
Document-Oriented (Hướng tài liệu)
MongoDB lưu trữ dữ liệu dưới dạng documents (tài liệu) theo định dạng BSON (Binary JSON):
{
   "_id": ObjectId("674468ea1234567890abcdef"),
   "licensePlate": "29A12345",
   "cardId": "1CACE0C634",
   "entryTime": ISODate("2025-11-25T08:30:15.000Z"),
   "image": "http://localhost:3001/images/entry_123.jpg"
 }
Schema-less (Linh hoạt cấu trúc)
Các documents trong cùng một collection không bắt buộc phải có cùng cấu trúc, cho phép linh hoạt trong quá trình phát triển.
Scalability (Khả năng mở rộng)
•           Horizontal Scaling: Sharding (phân tán dữ liệu qua nhiều server)
•           Vertical Scaling: Tăng RAM/CPU của server
3.3. So sánh MongoDB vs SQL
 
 
 
Đặc điểm
MongoDB (NoSQL)
MySQL/PostgreSQL (SQL)
Data Model
Document (JSON-like)
Table (Rows & Columns)
Schema
Dynamic (linh hoạt)
Fixed (cố định)
Relationships
Embedded / Reference
Foreign Keys
Query Language
MongoDB Query Language
SQL
Scaling
Horizontal (Sharding)
Vertical (Scale up)

 
4. THIẾT KẾ DATABASE
4.1. Phân tích yêu cầu
Hệ thống cần lưu trữ thông tin về mỗi lần xe vào bãi:
•           Biển số xe (licensePlate): Định danh xe, tra cứu
•           Mã thẻ RFID (cardId): Định danh duy nhất, ngăn gian lận
•           Thời gian vào (entryTime): Tính duration, báo cáo
•           Hình ảnh xe (image): Bằng chứng, tra cứu
4.2. Thiết kế Schema
Schema Definition
const parkingLogSchema = new mongoose.Schema({
   licensePlate: {
 	type: String,
 	required: true,
 	trim: true,
 	uppercase: true
   },
   entryTime: {
 	type: Date,
 	required: true,
 	default: Date.now
   },
   cardId: {
 	type: String,
 	required: true,
 	trim: true
   },
   image: {
 	type: String,
 	default: null
   }
 }, {
   timestamps: { createdAt: true, updatedAt: true }
 })
Giải thích các thuộc tính
A. licensePlate (Biển số xe)
•           type: String: Kiểu dữ liệu chuỗi
•           required: true: Bắt buộc phải có
•           trim: true: Xóa khoảng trắng đầu/cuối
•           uppercase: true: Tự động chuyển chữ HOA
Luồng xử lý:
Input: "  29a12345  "
 → trim: "29a12345"
 → uppercase: "29A12345"
 → Lưu vào DB: "29A12345"
Lợi ích: - Chuẩn hóa dữ liệu (không có “29a12345” và “29A12345” khác nhau) - Query chính xác hơn - Sử dụng index hiệu quả
B. entryTime (Thời gian vào)
•           type: Date: Kiểu dữ liệu ngày giờ
•           required: true: Bắt buộc phải có
•           default: Date.now: Mặc định = thời điểm hiện tại
C. cardId (Mã thẻ RFID)
•           type: String: Kiểu dữ liệu chuỗi
•           required: true: Bắt buộc - Không có thẻ = không vào
•           trim: true: Xóa space thừa
Vai trò: - UID duy nhất của thẻ RFID (VD: “1CACE0C634”) - Key để tìm xe khi ra - Ngăn chặn 1 thẻ vào 2 lần
D. image (Hình ảnh xe)
•           type: String: Lưu URL của ảnh
•           default: null: Optional field
Format:
http://192.168.1.100:3001/images/entry_1732524615.jpg
E. timestamps (Audit trail)
{
   timestamps: {
 	createdAt: true,   // Tự động thêm
 	updatedAt: true	// Tự động cập nhật
   }
 }
4.3. Indexes (Tối ưu hóa truy vấn)
Single Field Indexes
// Index theo biển số xe (tăng dần)
 parkingLogSchema.index({ licensePlate: 1 })

 // Index theo thời gian vào (giảm dần - mới nhất trước)
 parkingLogSchema.index({ entryTime: -1 })

 // Index theo mã thẻ RFID (tăng dần)
 parkingLogSchema.index({ cardId: 1 })
Mục đích:
Index
Query thường dùng
Tốc độ
{ licensePlate: 1 }
Tìm xe theo biển số
O(log n)
{ entryTime: -1 }
Lấy xe vào gần nhất
O(1)
{ cardId: 1 }
Tìm xe theo thẻ RFID
O(log n)

Compound Index
// Index kết hợp: licensePlate + cardId + entryTime
 parkingLogSchema.index({
   licensePlate: 1,
   cardId: 1,
   entryTime: -1
 })
Ứng dụng:
// Query sử dụng compound index (rất nhanh)
 db.parkingLogs.find({
   licensePlate: '29A12345',
   cardId: '1CACE0C634'
 }).sort({ entryTime: -1 })
4.4. Transform Output
parkingLogSchema.set('toJSON', {
   transform: (document, returnedObject) => {
 	returnedObject.id = returnedObject._id.toString()
 	delete returnedObject._id
 	delete returnedObject.__v
   }
 })
Trước transform:
{
   "_id": "674468ea1234567890abcdef",
   "licensePlate": "29A12345",
   "__v": 0
 }
Sau transform:
{
   "id": "674468ea1234567890abcdef",
   "licensePlate": "29A12345"
 }
5. XÂY DỰNG CHƯƠNG TRÌNH QUẢN LÝ
5.1. API Endpoints
POST /api/parking/logs (Xe vào)
Mục đích: Tạo log mới khi xe vào bãi
Request:
POST /api/parking/logs HTTP/1.1
 Content-Type: application/json

 {
   "licensePlate": "29A12345",
   "cardId": "1CACE0C634",
   "image": "http://192.168.1.101/images/entry_123.jpg"
 }
Controller Logic:
1.       Validation: Kiểm tra required fields
2.       Check duplicate: Kiểm tra cardId đã được sử dụng chưa
3.       Create log: Tạo document mới
4.       Save to DB: Lưu vào MongoDB
5.       Return response: Trả về kết quả
Response (Success - 201 Created):
{
   "success": true,
   "message": "Parking log created successfully",
   "data": {
 	"id": "674468ea1234567890abcdef",
 	"licensePlate": "29A12345",
 	"cardId": "1CACE0C634",
 	"entryTime": "2025-11-25T08:30:15.000Z"
   }
 }
Response (Error - 409 Conflict):
{
   "success": false,
   "error": {
 	"code": "CARD_IN_USE",
 	"message": "This card is already in use"
   }
 }
GET /api/parking/logs (Danh sách xe đang đỗ)
Mục đích: Lấy danh sách tất cả xe đang trong bãi
Query parameters: - cardId: Tìm theo mã thẻ - licensePlate: Tìm theo biển số - limit: Số lượng kết quả (default: 50) - page: Trang hiện tại (default: 1)
Response:
{
   "success": true,
   "data": {
 	"parkingLogs": [
   	{
     	"id": "674468ea1234567890abcdef",
     	"licensePlate": "29A12345",
     	"cardId": "1CACE0C634",
     	"entryTime": "2025-11-25T08:30:15.000Z"
   	}
 	],
 	"pagination": {
   	"total": 15,
   	"page": 1,
   	"limit": 50,
   	"pages": 1
 	}
   }
 }
DELETE /api/parking/logs/:id (Xe ra)
Mục đích: Xóa log khi xe ra khỏi bãi
Process: 1. Find log by ID 2. Calculate parking duration 3. Delete log 4. Return duration information
Response:
{
   "success": true,
   "data": {
 	"exitTime": "2025-11-25T10:45:30.000Z",
 	"duration": {
   	"hours": 2,
   	"minutes": 15,
   	"formatted": "2h 15m"
 	}
   }
 }
6. KẾT QUẢ ĐẠT ĐƯỢC
6.1. Link demo
Render - Application loading

