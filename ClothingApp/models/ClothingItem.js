// models/ClothingItem.js
import mongoose from 'mongoose';

const clothingItemSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  category: { type: String, required: true }, // e.g., Top, Bottom, Shoes
  color: { type: String },
  season: { type: String }, // e.g., Summer, Winter
  imageUrl: { type: String },
  tags: [String],
}, { timestamps: true });

export default mongoose.model('ClothingItem', clothingItemSchema);
