// models/Outfit.js
import mongoose from 'mongoose';

const outfitSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  items: [{ type: mongoose.Schema.Types.ObjectId, ref: 'ClothingItem' }],
  occasion: { type: String }, // Optional
  weather: { type: String },  // Optional
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model('Outfit', outfitSchema);
