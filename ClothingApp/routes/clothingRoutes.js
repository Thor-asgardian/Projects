// routes/clothingRoutes.js
import express from 'express';
import ClothingItem from '../models/ClothingItem.js';
import auth from '../middleware/auth.js';
import upload from '../middleware/upload.js';
import path from 'path';

const router = express.Router();

// Add clothing item
router.post('/', auth, upload.single('image'), async (req, res) => {
  try {
    const item = await ClothingItem.create({
      user: req.user,
      category: req.body.category,
      color: req.body.color,
      season: req.body.season,
      tags: req.body.tags ? req.body.tags.split(',') : [],
      imageUrl: req.file ? `/uploads/${req.file.filename}` : ''
    });
    res.status(201).json(item);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Get all clothing items for user
router.get('/', auth, async (req, res) => {
  try {
    const items = await ClothingItem.find({ user: req.user });
    res.json(items);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

export default router;
