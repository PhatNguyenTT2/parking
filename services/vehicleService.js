const Vehicle = require('../model/vehicle')
const ParkingLog = require('../model/parkingLog')

/**
 * Service để xử lý các nghiệp vụ liên quan đến xe ra/vào
 */
const vehicleService = {
  /**
   * Xử lý khi xe vào
   * @param {string} licensePlate - Biển số xe
   * @param {string} imagePath - Đường dẫn ảnh
   * @param {string} cameraId - ID camera
   * @param {number} confidence - Độ chính xác nhận diện
   * @param {number} ocrConfidence - Độ chính xác OCR
   */
  async handleEntry(licensePlate, imagePath, cameraId, confidence = null, ocrConfidence = null) {
    try {
      // Tìm kiếm xem biển số này đã có trong database chưa
      const existingVehicle = await Vehicle.findOne({ licensePlate })

      if (existingVehicle && existingVehicle.status === 'in') {
        // Cảnh báo: xe đã trong bãi
        return {
          success: false,
          message: 'Xe đã có trong bãi',
          vehicle: existingVehicle
        }
      }

      // Tạo hồ sơ xe mới hoặc cập nhật nếu xe đã ra trước đó
      const vehicle = await Vehicle.findOneAndUpdate(
        { licensePlate },
        {
          licensePlate,
          entryTime: new Date(),
          exitTime: null,
          status: 'in',
          entryImagePath: imagePath,
          exitImagePath: null,
          duration: null
        },
        { upsert: true, new: true }
      )

      // Lưu log vào parkingLogs
      await ParkingLog.create({
        licensePlate,
        eventType: 'entry',
        timestamp: new Date(),
        cameraId,
        imageUrl: imagePath,
        confidence,
        ocrConfidence
      })

      return {
        success: true,
        message: 'Xe vào thành công',
        vehicle
      }
    } catch (error) {
      throw new Error(`Lỗi khi xử lý xe vào: ${error.message}`)
    }
  },

  /**
   * Xử lý khi xe ra
   * @param {string} licensePlate - Biển số xe
   * @param {string} imagePath - Đường dẫn ảnh
   * @param {string} cameraId - ID camera
   * @param {number} confidence - Độ chính xác nhận diện
   * @param {number} ocrConfidence - Độ chính xác OCR
   */
  async handleExit(licensePlate, imagePath, cameraId, confidence = null, ocrConfidence = null) {
    try {
      // Tìm kiếm hồ sơ xe vào
      const vehicle = await Vehicle.findOne({
        licensePlate,
        status: 'in'
      })

      if (!vehicle) {
        // Cảnh báo: không tìm thấy hồ sơ vào
        return {
          allowed: false,
          message: 'Không tìm thấy hồ sơ xe vào',
          vehicle: null
        }
      }

      // Tính thời gian lưu trú (phút)
      const duration = (new Date() - vehicle.entryTime) / 60000

      // Cập nhật thời gian ra và trạng thái
      vehicle.exitTime = new Date()
      vehicle.status = 'out'
      vehicle.duration = duration
      vehicle.exitImagePath = imagePath
      await vehicle.save()

      // Lưu log vào parkingLogs
      await ParkingLog.create({
        licensePlate,
        eventType: 'exit',
        timestamp: new Date(),
        cameraId,
        imageUrl: imagePath,
        confidence,
        ocrConfidence
      })

      return {
        allowed: true,
        message: 'Xe có thể ra',
        vehicle,
        duration
      }
    } catch (error) {
      throw new Error(`Lỗi khi xử lý xe ra: ${error.message}`)
    }
  },

  /**
   * Lấy danh sách xe hiện đang ở trong bãi
   */
  async getCarsInside() {
    try {
      const carsInside = await Vehicle.find({ status: 'in' }).sort({ entryTime: -1 })
      return carsInside
    } catch (error) {
      throw new Error(`Lỗi khi lấy danh sách xe trong bãi: ${error.message}`)
    }
  },

  /**
   * Lấy lịch sử xe trong ngày
   * @param {Date} date - Ngày cần truy vấn (mặc định là hôm nay)
   */
  async getTodayHistory(date = new Date()) {
    try {
      const todayStart = new Date(date.setHours(0, 0, 0, 0))
      const todayEnd = new Date(date.setHours(23, 59, 59, 999))

      const history = await Vehicle.find({
        entryTime: { $gte: todayStart, $lte: todayEnd }
      }).sort({ entryTime: -1 })

      return history
    } catch (error) {
      throw new Error(`Lỗi khi lấy lịch sử xe trong ngày: ${error.message}`)
    }
  },

  /**
   * Tìm xe cụ thể theo biển số
   * @param {string} licensePlate - Biển số xe
   */
  async findVehicle(licensePlate) {
    try {
      const vehicle = await Vehicle.findOne({ licensePlate })
      return vehicle
    } catch (error) {
      throw new Error(`Lỗi khi tìm xe: ${error.message}`)
    }
  },

  /**
   * Lấy lịch sử chi tiết của một xe
   * @param {string} licensePlate - Biển số xe
   */
  async getVehicleHistory(licensePlate) {
    try {
      const logs = await ParkingLog.find({ licensePlate }).sort({ timestamp: -1 })
      return logs
    } catch (error) {
      throw new Error(`Lỗi khi lấy lịch sử xe: ${error.message}`)
    }
  },

  /**
   * Thống kê lưu lượng theo giờ trong ngày
   * @param {Date} date - Ngày cần thống kê (mặc định là hôm nay)
   */
  async getHourlyStatistics(date = new Date()) {
    try {
      const todayStart = new Date(date.setHours(0, 0, 0, 0))
      const todayEnd = new Date(date.setHours(23, 59, 59, 999))

      const statistics = await ParkingLog.aggregate([
        {
          $match: {
            timestamp: { $gte: todayStart, $lte: todayEnd }
          }
        },
        {
          $group: {
            _id: {
              hour: { $hour: '$timestamp' },
              eventType: '$eventType'
            },
            count: { $sum: 1 }
          }
        },
        {
          $sort: { '_id.hour': 1 }
        }
      ])

      return statistics
    } catch (error) {
      throw new Error(`Lỗi khi lấy thống kê theo giờ: ${error.message}`)
    }
  },

  /**
   * Lấy tổng số xe trong bãi hiện tại
   */
  async getTotalCarsInside() {
    try {
      const count = await Vehicle.countDocuments({ status: 'in' })
      return count
    } catch (error) {
      throw new Error(`Lỗi khi đếm số xe trong bãi: ${error.message}`)
    }
  }
}

module.exports = vehicleService

