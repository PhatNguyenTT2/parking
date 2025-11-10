const mongoose = require('mongoose')

const parkingLogSchema = new mongoose.Schema({
  licensePlate: {
    type: String,
    required: true,
    trim: true,
    uppercase: true
  },
  eventType: {
    type: String,
    enum: ['entry', 'exit'],
    required: true
  },
  timestamp: {
    type: Date,
    required: true,
    default: Date.now
  },
  cameraId: {
    type: String,
    required: true,
    trim: true
  },
  imageUrl: {
    type: String,
    default: null
  },
  confidence: {
    type: Number, // Độ chính xác nhận diện (0-1)
    min: 0,
    max: 1,
    default: null
  },
  ocrConfidence: {
    type: Number, // Độ chính xác OCR (0-1)
    min: 0,
    max: 1,
    default: null
  }
}, {
  timestamps: { createdAt: true, updatedAt: false } // Chỉ cần createdAt
})

// Index để tăng tốc độ truy vấn
parkingLogSchema.index({ licensePlate: 1 })
parkingLogSchema.index({ eventType: 1 })
parkingLogSchema.index({ timestamp: -1 })
parkingLogSchema.index({ cameraId: 1 })

// Compound index để truy vấn theo biển số và loại event
parkingLogSchema.index({ licensePlate: 1, eventType: 1, timestamp: -1 })

parkingLogSchema.set('toJSON', {
  transform: (document, returnedObject) => {
    returnedObject.id = returnedObject._id.toString()
    delete returnedObject._id
    delete returnedObject.__v
  }
})

module.exports = mongoose.model('ParkingLog', parkingLogSchema)

