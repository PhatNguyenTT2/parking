const parkingLogRouter = require('express').Router()
const ParkingLog = require('../model/parkingLog')

/**
 * GET /api/parking-log
 * Lấy tất cả parking logs với phân trang
 */
parkingLogRouter.get('/', async (request, response, next) => {
  try {
    const { page = 1, limit = 20, eventType, licensePlate, cameraId } = request.query

    const query = {}
    if (eventType) query.eventType = eventType
    if (licensePlate) query.licensePlate = licensePlate.toUpperCase()
    if (cameraId) query.cameraId = cameraId

    const logs = await ParkingLog.find(query)
      .sort({ timestamp: -1 })
      .limit(limit * 1)
      .skip((page - 1) * limit)

    const count = await ParkingLog.countDocuments(query)

    response.json({
      logs,
      totalPages: Math.ceil(count / limit),
      currentPage: parseInt(page),
      total: count
    })
  } catch (error) {
    next(error)
  }
})

/**
 * GET /api/parking-log/vehicle/:licensePlate
 * Lấy tất cả logs của một xe cụ thể
 */
parkingLogRouter.get('/vehicle/:licensePlate', async (request, response, next) => {
  try {
    const { licensePlate } = request.params
    const logs = await ParkingLog.find({
      licensePlate: licensePlate.toUpperCase()
    }).sort({ timestamp: -1 })

    response.json({
      licensePlate: licensePlate.toUpperCase(),
      total: logs.length,
      logs
    })
  } catch (error) {
    next(error)
  }
})

/**
 * GET /api/parking-log/today
 * Lấy logs trong ngày hôm nay
 */
parkingLogRouter.get('/today', async (request, response, next) => {
  try {
    const { eventType } = request.query
    const todayStart = new Date()
    todayStart.setHours(0, 0, 0, 0)
    const todayEnd = new Date()
    todayEnd.setHours(23, 59, 59, 999)

    const query = {
      timestamp: { $gte: todayStart, $lte: todayEnd }
    }
    if (eventType) query.eventType = eventType

    const logs = await ParkingLog.find(query).sort({ timestamp: -1 })

    response.json({
      date: todayStart.toISOString().split('T')[0],
      total: logs.length,
      logs
    })
  } catch (error) {
    next(error)
  }
})

/**
 * GET /api/parking-log/entry/:licensePlate/latest
 * Lấy ảnh vào mới nhất của xe
 */
parkingLogRouter.get('/entry/:licensePlate/latest', async (request, response, next) => {
  try {
    const { licensePlate } = request.params
    const log = await ParkingLog.findOne({
      licensePlate: licensePlate.toUpperCase(),
      eventType: 'entry'
    }).sort({ timestamp: -1 })

    if (!log) {
      return response.status(404).json({
        error: 'Không tìm thấy log vào'
      })
    }

    response.json(log)
  } catch (error) {
    next(error)
  }
})

/**
 * GET /api/parking-log/exit/:licensePlate/latest
 * Lấy ảnh ra mới nhất của xe
 */
parkingLogRouter.get('/exit/:licensePlate/latest', async (request, response, next) => {
  try {
    const { licensePlate } = request.params
    const log = await ParkingLog.findOne({
      licensePlate: licensePlate.toUpperCase(),
      eventType: 'exit'
    }).sort({ timestamp: -1 })

    if (!log) {
      return response.status(404).json({
        error: 'Không tìm thấy log ra'
      })
    }

    response.json(log)
  } catch (error) {
    next(error)
  }
})

/**
 * GET /api/parking-log/statistics/camera
 * Thống kê theo camera
 */
parkingLogRouter.get('/statistics/camera', async (request, response, next) => {
  try {
    const statistics = await ParkingLog.aggregate([
      {
        $group: {
          _id: {
            cameraId: '$cameraId',
            eventType: '$eventType'
          },
          count: { $sum: 1 },
          avgConfidence: { $avg: '$confidence' },
          avgOcrConfidence: { $avg: '$ocrConfidence' }
        }
      },
      {
        $sort: { '_id.cameraId': 1 }
      }
    ])

    response.json({
      statistics
    })
  } catch (error) {
    next(error)
  }
})

/**
 * DELETE /api/parking-log/:id
 * Xóa một log (admin only - cần implement authentication)
 */
parkingLogRouter.delete('/:id', async (request, response, next) => {
  try {
    const { id } = request.params
    const log = await ParkingLog.findByIdAndDelete(id)

    if (!log) {
      return response.status(404).json({
        error: 'Không tìm thấy log'
      })
    }

    response.json({
      message: 'Đã xóa log thành công',
      log
    })
  } catch (error) {
    next(error)
  }
})

module.exports = parkingLogRouter
