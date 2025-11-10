// API service để gọi các endpoint của backend
const API_BASE_URL = 'http://localhost:3001/api/vehicle'
const BACKEND_URL = 'http://localhost:3001'

/**
 * Helper function để tạo URL đầy đủ cho hình ảnh
 */
const getImageUrl = (imagePath) => {
  if (!imagePath) return null
  // Nếu imagePath đã là URL đầy đủ thì return luôn
  if (imagePath.startsWith('http')) return imagePath
  // Nếu là đường dẫn tương đối, thêm BACKEND_URL
  return `${BACKEND_URL}${imagePath}`
}

/**
 * Helper function để xử lý vehicle data và thêm URL đầy đủ cho hình ảnh
 */
const processVehicleData = (vehicle) => {
  if (!vehicle) return null
  return {
    ...vehicle,
    entryImagePath: getImageUrl(vehicle.entryImagePath),
    exitImagePath: getImageUrl(vehicle.exitImagePath)
  }
}

/**
 * Lấy danh sách xe đang trong bãi
 */
export const getCarsInside = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/inside`)
    if (!response.ok) {
      throw new Error('Failed to fetch cars inside')
    }
    const data = await response.json()
    // Xử lý URL hình ảnh cho tất cả vehicles
    return {
      ...data,
      vehicles: (data.vehicles || []).map(processVehicleData)
    }
  } catch (error) {
    console.error('Error fetching cars inside:', error)
    throw error
  }
}

/**
 * Lấy lịch sử xe trong ngày
 */
export const getTodayHistory = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/history/today`)
    if (!response.ok) {
      throw new Error('Failed to fetch today history')
    }
    const data = await response.json()
    // Xử lý URL hình ảnh cho tất cả vehicles
    return {
      ...data,
      vehicles: (data.vehicles || []).map(processVehicleData)
    }
  } catch (error) {
    console.error('Error fetching today history:', error)
    throw error
  }
}

/**
 * Lấy thông tin chi tiết của một xe
 */
export const getVehicleByLicensePlate = async (licensePlate) => {
  try {
    const response = await fetch(`${API_BASE_URL}/${licensePlate}`)
    if (!response.ok) {
      throw new Error('Failed to fetch vehicle')
    }
    const vehicle = await response.json()
    return processVehicleData(vehicle)
  } catch (error) {
    console.error('Error fetching vehicle:', error)
    throw error
  }
}

/**
 * Thêm xe vào (dành cho test)
 */
export const addEntryVehicle = async (data) => {
  try {
    const response = await fetch(`${API_BASE_URL}/entry`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to add entry vehicle')
    }
    const result = await response.json()
    return {
      ...result,
      vehicle: processVehicleData(result.vehicle)
    }
  } catch (error) {
    console.error('Error adding entry vehicle:', error)
    throw error
  }
}

/**
 * Thêm xe ra (dành cho test)
 */
export const addExitVehicle = async (data) => {
  try {
    const response = await fetch(`${API_BASE_URL}/exit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || errorData.message || 'Failed to add exit vehicle')
    }
    const result = await response.json()
    return {
      ...result,
      vehicle: processVehicleData(result.vehicle)
    }
  } catch (error) {
    console.error('Error adding exit vehicle:', error)
    throw error
  }
}

