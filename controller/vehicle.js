const vehicleRouter = require('express').Router()
const vehicleService = require('../services/vehicleService')

/**
 * POST /api/vehicle/entry
 * Xử lý khi xe vào bãi
 */
vehicleRouter.post('/entry', async (request, response, next) => {
  try {
    const { licensePlate, imagePath, cameraId, confidence, ocrConfidence } = request.body

    if (!licensePlate || !cameraId) {
      return response.status(400).json({
        error: 'licensePlate và cameraId là bắt buộc'
      })
    }

    const result = await vehicleService.handleEntry(
      licensePlate,
      imagePath,
      cameraId,
      confidence,
      ocrConfidence
    )

    if (!result.success) {
      return response.status(400).json(result)
    }

    response.status(201).json(result)
  } catch (error) {
    next(error)
  }
})

/**
 * POST /api/vehicle/exit
 * Xử lý khi xe ra khỏi bãi
 */
vehicleRouter.post('/exit', async (request, response, next) => {
  try {
    const { licensePlate, imagePath, cameraId, confidence, ocrConfidence } = request.body

    if (!licensePlate || !cameraId) {
      return response.status(400).json({
        error: 'licensePlate và cameraId là bắt buộc'
      })
    }

    const result = await vehicleService.handleExit(
      licensePlate,
      imagePath,
      cameraId,
      confidence,
      ocrConfidence
    )

    if (!result.allowed) {
      return response.status(404).json(result)
    }

    response.json(result)
  } catch (error) {
    next(error)
  }
})

/**
 * GET /api/vehicle/inside
 * Lấy danh sách tất cả xe đang ở trong bãi
 */
vehicleRouter.get('/inside', async (request, response, next) => {
  try {
    const carsInside = await vehicleService.getCarsInsideWithImages()
    response.json({
      total: carsInside.length,
      vehicles: carsInside
    })
  } catch (error) {
    next(error)
  }
})

/**
 * GET /api/vehicle/history/today
 * Lấy lịch sử xe trong ngày
 */
vehicleRouter.get('/history/today', async (request, response, next) => {
  try {
    const { date } = request.query
    const targetDate = date ? new Date(date) : new Date()

    const history = await vehicleService.getTodayHistoryWithImages(targetDate)
    response.json({
      date: targetDate.toISOString().split('T')[0],
      total: history.length,
      vehicles: history
    })
  } catch (error) {
    next(error)
  }
})

/**
 * GET /api/vehicle/:licensePlate
 * Tìm xe cụ thể theo biển số
 */
vehicleRouter.get('/:licensePlate', async (request, response, next) => {
  try {
    const { licensePlate } = request.params
    const vehicle = await vehicleService.getVehicleWithImages(licensePlate.toUpperCase())

    if (!vehicle) {
      return response.status(404).json({
        error: 'Không tìm thấy xe'
      })
    }

    response.json(vehicle)
  } catch (error) {
    next(error)
  }
})

/**
 * GET /api/vehicle/:licensePlate/history
 * Lấy lịch sử chi tiết của một xe
 */
vehicleRouter.get('/:licensePlate/history', async (request, response, next) => {
  try {
    const { licensePlate } = request.params
    const history = await vehicleService.getVehicleHistory(licensePlate.toUpperCase())

    response.json({
      licensePlate: licensePlate.toUpperCase(),
      total: history.length,
      logs: history
    })
  } catch (error) {
    next(error)
  }
})

/**
 * GET /api/vehicle/statistics/hourly
 * Thống kê lưu lượng theo giờ trong ngày
 */
vehicleRouter.get('/statistics/hourly', async (request, response, next) => {
  try {
    const { date } = request.query
    const targetDate = date ? new Date(date) : new Date()

    const statistics = await vehicleService.getHourlyStatistics(targetDate)
    response.json({
      date: targetDate.toISOString().split('T')[0],
      statistics
    })
  } catch (error) {
    next(error)
  }
})

/**
 * GET /api/vehicle/statistics/summary
 * Lấy tổng quan thống kê
 */
vehicleRouter.get('/statistics/summary', async (request, response, next) => {
  try {
    const totalInside = await vehicleService.getTotalCarsInside()
    const todayHistory = await vehicleService.getTodayHistory()

    const entryToday = todayHistory.filter(v => v.status === 'in' || v.exitTime).length
    const exitToday = todayHistory.filter(v => v.status === 'out').length

    response.json({
      currentVehiclesInside: totalInside,
      todayEntry: entryToday,
      todayExit: exitToday,
      todayTotal: todayHistory.length
    })
  } catch (error) {
    next(error)
  }
})

module.exports = vehicleRouter

