/**
 * Script để thêm dữ liệu mẫu vào database
 * Chạy: node seed-data.js
 */

const API_BASE_URL = 'http://localhost:3001/api/vehicle'

// Hàm gửi request
async function sendRequest(endpoint, method = 'GET', data = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  }

  if (data) {
    options.body = JSON.stringify(data)
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options)
    const result = await response.json()
    console.log(`✅ ${method} ${endpoint}:`, result.message || 'Success')
    return result
  } catch (error) {
    console.error(`❌ ${method} ${endpoint}:`, error.message)
    throw error
  }
}

// Hàm delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))

// Main seed function
async function seedData() {
  console.log('🌱 Bắt đầu seed dữ liệu mẫu...\n')

  try {
    // ========================================
    // XE 1: 30A-12345 (ĐÃ RA)
    // ========================================
    console.log('📥 Xe 1: 30A-12345 - Vào và đã ra')
    await sendRequest('/entry', 'POST', {
      licensePlate: '30A-12345',
      cameraId: 'CAM01',
      imagePath: '/images/entry_30A12345.jpg',
      confidence: 0.95,
      ocrConfidence: 0.98
    })

    await delay(3000) // Đợi 3 giây (giả lập thời gian đỗ xe)

    await sendRequest('/exit', 'POST', {
      licensePlate: '30A-12345',
      cameraId: 'CAM02',
      imagePath: '/images/exit_30A12345.jpg',
      confidence: 0.96,
      ocrConfidence: 0.97
    })

    console.log('')

    // ========================================
    // XE 2: 29A-67890 (ĐÃ RA)
    // ========================================
    console.log('📥 Xe 2: 29A-67890 - Vào và đã ra')
    await sendRequest('/entry', 'POST', {
      licensePlate: '29A-67890',
      cameraId: 'CAM01',
      imagePath: '/images/entry_29A67890.jpg',
      confidence: 0.92,
      ocrConfidence: 0.96
    })

    await delay(5000) // Đợi 5 giây

    await sendRequest('/exit', 'POST', {
      licensePlate: '29A-67890',
      cameraId: 'CAM02',
      imagePath: '/images/exit_29A67890.jpg',
      confidence: 0.94,
      ocrConfidence: 0.95
    })

    console.log('')

    // ========================================
    // XE 3: 51B-11111 (ĐANG TRONG BÃI)
    // ========================================
    console.log('📥 Xe 3: 51B-11111 - Chỉ vào, chưa ra')
    await sendRequest('/entry', 'POST', {
      licensePlate: '51B-11111',
      cameraId: 'CAM01',
      imagePath: '/images/entry_51B11111.jpg',
      confidence: 0.98,
      ocrConfidence: 0.99
    })

    console.log('')

    // ========================================
    // KIỂM TRA DỮ LIỆU
    // ========================================
    console.log('📊 Kiểm tra dữ liệu đã seed:')
    console.log('─────────────────────────────────────')

    // Danh sách xe trong bãi
    const insideData = await sendRequest('/inside', 'GET')
    console.log(`\n📌 Xe trong bãi: ${insideData.total} xe`)
    insideData.vehicles.forEach(v => {
      console.log(`   - ${v.licensePlate} (vào lúc ${new Date(v.entryTime).toLocaleTimeString('vi-VN')})`)
    })

    // Lịch sử trong ngày
    const historyData = await sendRequest('/history/today', 'GET')
    console.log(`\n📜 Lịch sử hôm nay: ${historyData.total} lượt`)
    historyData.vehicles.forEach(v => {
      const status = v.status === 'in' ? '🟢 Đang trong bãi' : '🔴 Đã ra'
      console.log(`   - ${v.licensePlate}: ${status}`)
    })

    console.log('\n✅ Seed dữ liệu hoàn thành!')
    console.log('\n💡 Mở trình duyệt và truy cập http://localhost:5173 để xem giao diện')
    console.log('📊 Bạn sẽ thấy:')
    console.log('   - Làn vào: 51B-11111 (xe mới vào gần nhất)')
    console.log('   - Làn ra: 29A-67890 (xe ra gần nhất)')
    console.log('   - Tổng xe trong bãi: 1 xe')
    console.log('   - Tổng lượt hôm nay: 3 xe')

  } catch (error) {
    console.error('\n❌ Seed dữ liệu thất bại:', error.message)
    console.log('\n⚠️  Hãy đảm bảo:')
    console.log('   1. MongoDB đã chạy')
    console.log('   2. Backend đã chạy (npm run dev)')
    console.log('   3. Port 3001 không bị chiếm dụng')
  }
}

// Chạy seed
seedData()
