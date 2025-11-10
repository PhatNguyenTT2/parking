Bước số 5 trong kế hoạch thực hiện dự án của nhóm SoCiety được xác định là "Thiết kế database (MongoDB), xây dựng chương trình quản lý xe ra/vào" với thời hạn 2 tuần. Dưới đây là phân tích chi tiết về các khía cạnh khác nhau của bước này.

Mục Tiêu Và Kết Quả Mong Muốn
Kết quả chính của bước 5 là đạt được "Lưu trữ - truy xuất dữ liệu biển số, thời gian ổn định". Điều này có nghĩa hệ thống MongoDB phải hoạt động một cách tin cậy và hiệu quả để lưu trữ và quản lý thông tin về các xe vào và xe ra.​

Data Input (Dữ Liệu Đầu Vào)
Dữ liệu đầu vào cho bước 5 bao gồm:

Từ bước 4 (Tích hợp OCR):

Biển số xe được nhận diện và trích xuất thành ký tự từ hệ thống YOLOv5 + OCR đã kiểm thử thành công

Thông tin biển số phải ở dạng chuỗi ký tự (text) chính xác

Thông tin bổ sung:

Thời gian khi xe vào/ra (timestamp)

Loại xe (xác định từ biển số hoặc input thủ công)

Camera ID hoặc điểm vào/ra (để phân biệt xe vào hay xe ra)

Hình ảnh gốc của biển số (tùy chọn, để audit/verify sau)

Data Output (Dữ Liệu Đầu Ra)
Dữ liệu đầu ra mà MongoDB cần tạo ra gồm:

Hồ sơ xe ra/vào:

Biển số xe

Thời gian vào

Thời gian ra

Trạng thái (đang ở trong bãi / đã ra)

Khoảng thời gian lưu trú

Báo cáo và truy vấn:

Danh sách xe hiện đang ở trong bãi

Lịch sử xe ra/vào trong ngày

Thống kê lưu lượng theo giờ

Xác thực xe (kiểm tra biển số khi ra có khớp với khi vào không)

Cấu Trúc MongoDB
Để đáp ứng nhu cầu này, bạn nên thiết kế một hoặc nhiều collection như sau:

Collection 1: vehicles (Hồ sơ xe)

javascript
{
  _id: ObjectId,
  licensePlate: "String",        // Biển số (unique)
  entryTime: ISODate,           // Thời gian vào
  exitTime: ISODate,            // Thời gian ra (null nếu chưa ra)
  status: "in" | "out",         // Trạng thái hiện tại
  entryImagePath: "String",     // Đường dẫn ảnh vào
  exitImagePath: "String",      // Đường dẫn ảnh ra
  duration: Number,             // Thời gian lưu trú (phút)
  createdAt: ISODate,
  updatedAt: ISODate
}
Collection 2: parkingLogs (Lịch sử chi tiết)

javascript
{
  _id: ObjectId,
  licensePlate: "String",
  eventType: "entry" | "exit",
  timestamp: ISODate,
  cameraId: "String",
  imageUrl: "String",
  confidence: Number,           // Độ chính xác nhận diện (0-1)
  ocrConfidence: Number,        // Độ chính xác OCR
  createdAt: ISODate
}
Cách Sử Dụng MongoDB
1. Khi xe vào (Entry):

javascript
// Tìm kiếm xem biển số này đã có trong database chưa
const existingVehicle = await collection.findOne({ licensePlate: plateNumber });

if (existingVehicle && existingVehicle.status === "in") {
  // Cảnh báo: xe đã trong bãi
} else {
  // Tạo hồ sơ xe mới hoặc cập nhật
  await collection.insertOne({
    licensePlate: plateNumber,
    entryTime: new Date(),
    exitTime: null,
    status: "in",
    entryImagePath: imagePath
  });
}
2. Khi xe ra (Exit):

javascript
// Tìm kiếm hồ sơ xe vào
const vehicle = await collection.findOne({ 
  licensePlate: plateNumber, 
  status: "in" 
});

if (vehicle) {
  // Cập nhật thời gian ra và trạng thái
  const duration = (new Date() - vehicle.entryTime) / 60000; // phút
  
  await collection.updateOne(
    { _id: vehicle._id },
    {
      $set: {
        exitTime: new Date(),
        status: "out",
        duration: duration,
        exitImagePath: imagePath
      }
    }
  );
  
  // Cho phép mở barrier
  return { allowed: true, message: "Vehicle can exit" };
} else {
  // Cảnh báo: không tìm thấy hồ sơ vào
  return { allowed: false, message: "No entry record found" };
}
3. Truy vấn thông tin:

javascript
// Xe hiện đang ở trong bãi
const carsInside = await collection.find({ status: "in" }).toArray();

// Lịch sử xe trong ngày
const todayStart = new Date().setHours(0, 0, 0, 0);
const history = await collection.find({ 
  entryTime: { $gte: new Date(todayStart) } 
}).toArray();

// Tìm xe cụ thể
const vehicleInfo = await collection.findOne({ licensePlate: "ABC12345" });
Tích Hợp Với Các Bước Khác
Liên kết với bước 4 (OCR): MongoDB nhận biển số đã xác thực từ YOLOv5 + OCR, đảm bảo dữ liệu đầu vào chính xác trước khi lưu.

Chuẩn bị cho bước 6 (SoC integration): Hệ thống MongoDB được xây dựng độc lập, có thể truy cập từ Raspberry Pi 4 thông qua:

Remote MongoDB Atlas (cloud-based) - dễ truy cập từ bất kỳ nơi nào

Local MongoDB trên Raspberry Pi - tối ưu hóa độ trễ nhưng cần cài đặt phần mềm

Các Kỹ Năng Và Công Cụ Cần Thiết
MongoDB fundamentals: Insert, Find, Update, Delete (CRUD operations)

Node.js/Express API: Xây dựng API endpoints để quản lý dữ liệu

Mongoose ODM (optional): Giúp định nghĩa schema một cách rõ ràng

Indexing: Tạo index cho licensePlate để tăng tốc độ truy vấn

Authentication: Nếu dùng MongoDB Atlas, cần thiết lập user/password

Thách Thức Tiềm Ẩn
Conflict resolution: Xử lý trường hợp biển số bị nhận diện sai

Duplicate handling: Nếu cùng một xe vào 2 lần trong ngày

Timestamp synchronization: Đảm bảo thời gian server và các thiết bị đều chính xác

Connection stability: Đảm bảo kết nối MongoDB ổn định khi tích hợp lên Raspberry Pi

Bước 5 này là nền tảng dữ liệu quan trọng cho toàn bộ hệ thống, vì vậy cần đảm bảo thiết kế schema tốt, các index hiệu quả, và xử lý lỗi toàn diện.

