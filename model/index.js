// Export tất cả models từ một file duy nhất để dễ import
const Vehicle = require('./vehicle')
const ParkingLog = require('./parkingLog')

module.exports = {
  Vehicle,
  ParkingLog
}

