const mongoose = require('mongoose')

const parkingLogSchema = new mongoose.Schema({
  licensePlate: {
    type: String,
    required: true,
    trim: true,
    uppercase: true
  },
  timestamp: {
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
  },
}, {
  timestamps: { createdAt: true, updatedAt: false } // Chỉ cần createdAt
})

// Index để tăng tốc độ truy vấn
parkingLogSchema.index({ licensePlate: 1 })
parkingLogSchema.index({ timestamp: -1 })
parkingLogSchema.index({ cardId: 1 })

// Compound index để truy vấn theo biển số và loại event
parkingLogSchema.index({ licensePlate: 1, cardId: 1, timestamp: -1 })

parkingLogSchema.set('toJSON', {
  transform: (document, returnedObject) => {
    returnedObject.id = returnedObject._id.toString()
    delete returnedObject._id
    delete returnedObject.__v
  }
})

module.exports = mongoose.model('ParkingLog', parkingLogSchema)

