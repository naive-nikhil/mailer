const mongoose = require('mongoose');

const recipientSchema = new mongoose.Schema({
  campaign: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Campaign',
    required: true
  },
  email: {
    type: String,
    required: true
  },
  name: String,
  company: String,
  customFields: {
    type: Map,
    of: String
  },
  status: {
    type: String,
    enum: ['pending', 'sent', 'failed'],
    default: 'pending'
  },
  sentAt: Date,
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Recipient', recipientSchema);