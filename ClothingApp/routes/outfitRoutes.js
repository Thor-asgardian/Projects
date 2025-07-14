// routes/outfitRoutes.js
import express from 'express';
import Outfit from '../models/Outfit.js';
import ClothingItem from '../models/ClothingItem.js';
import auth from '../middleware/auth.js';

const router = express.Router();

// Suggest outfit based on rule-based logic
router.get('/suggest', auth, async (req, res) => {
  try {
    const items = await ClothingItem.find({ user: req.user });
    const tops = items.filter(i => i.category.toLowerCase() === 'top');
    const bottoms = items.filter(i => i.category.toLowerCase() === 'bottom');
    const shoes = items.filter(i => i.category.toLowerCase() === 'shoes');

    if (!tops.length || !bottoms.length || !shoes.length) {
      return res.status(400).json({ message: "Not enough clothing items to suggest an outfit." });
    }

    const getRandom = arr => arr[Math.floor(Math.random() * arr.length)];

    const outfitItems = [getRandom(tops), getRandom(bottoms), getRandom(shoes)];

    const outfit = await Outfit.create({
      user: req.user,
      items: outfitItems.map(item => item._id)
    });

    res.json({ outfit, items: outfitItems });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Get all saved outfits
router.get('/', auth, async (req, res) => {
  try {
    const outfits = await Outfit.find({ user: req.user }).populate('items');
    res.json(outfits);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

export default router;
