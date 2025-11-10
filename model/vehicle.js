const mongoose = require('mongoose')

const vehicleSchema = new mongoose.Schema({
  licensePlate: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    uppercase: true
  },
  entryTime: {
    type: Date,
    required: true,
    default: Date.now
  },
  exitTime: {
    type: Date,
    default: null
  },
  status: {
    type: String,
    enum: ['in', 'out'],
    required: true,
    default: 'in'
  },
  entryImagePath: {
    type: String,
    default: null
  },
  exitImagePath: {
    type: String,
    default: null
  },
  duration: {
    type: Number, // Thời gian lưu trú (phút)
    default: null
  }
}, {
  timestamps: true // Tự động tạo createdAt và updatedAt
})

// Index để tăng tốc độ truy vấn
vehicleSchema.index({ licensePlate: 1 })
vehicleSchema.index({ status: 1 })
vehicleSchema.index({ entryTime: -1 })

// Virtual để format thời gian lưu trú
vehicleSchema.virtual('durationFormatted').get(function () {
  if (!this.duration) return null
  const hours = Math.floor(this.duration / 60)
  const minutes = Math.floor(this.duration % 60)
  return `${hours}h ${minutes}m`
})

vehicleSchema.set('toJSON', {
  virtuals: true,
  transform: (document, returnedObject) => {
    returnedObject.id = returnedObject._id.toString()
    delete returnedObject._id
    delete returnedObject.__v
  }
})

module.exports = mongoose.model('Vehicle', vehicleSchema)

