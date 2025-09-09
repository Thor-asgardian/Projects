require('dotenv').config();
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const multer = require('multer');

const app = express();
const PORT = process.env.PORT || 3000;
const USERS_FILE = path.join(__dirname, 'users.json');
const HISTORY_FILE = path.join(__dirname, 'history.json');

// ===== Middleware =====
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// ===== Helper Functions =====
function loadUsers() {
    if (!fs.existsSync(USERS_FILE)) return [];
    try {
        return JSON.parse(fs.readFileSync(USERS_FILE, 'utf-8'));
    } catch (err) {
        console.error('Error reading users.json:', err);
        return [];
    }
}

function saveUsers(users) {
    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
}

function loadHistory() {
    if (!fs.existsSync(HISTORY_FILE)) return [];
    try {
        return JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf-8'));
    } catch (err) {
        console.error('Error reading history.json:', err);
        return [];
    }
}

function saveHistory(history) {
    fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2));
}

function generateToken(user) {
    return jwt.sign(
        { id: user.id, email: user.email },
        process.env.JWT_SECRET,
        { expiresIn: '1h' }
    );
}

// ===== Authentication Middleware =====
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'Access denied' });

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: 'Invalid token' });
        req.user = user;
        next();
    });
}

// ===== Multer Setup =====
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, uploadDir),
    filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname)
});

const upload = multer({
    storage,
    limits: { fileSize: 5 * 1024 * 1024 }, // 5MB
    fileFilter: (req, file, cb) => {
        const allowed = /jpeg|jpg|png|gif|webp/;
        const ext = allowed.test(path.extname(file.originalname).toLowerCase());
        const mime = allowed.test(file.mimetype);
        if (ext && mime) cb(null, true);
        else cb(new Error('Only image files allowed (jpeg, jpg, png, gif, webp)'));
    }
});

// ===== Routes =====

// Landing page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Dashboard
app.get('/dashboard.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

// Signup
app.post('/api/signup', async (req, res) => {
    const { email, password } = req.body;
    if (!email || !password) return res.status(400).json({ error: 'Email & password required' });

    const users = loadUsers();
    if (users.find(u => u.email === email)) return res.status(400).json({ error: 'User exists' });

    const passwordHash = await bcrypt.hash(password, 10);
    const newUser = { id: Date.now().toString(), email, passwordHash };
    users.push(newUser);
    saveUsers(users);

    const token = generateToken(newUser);
    res.json({ message: 'Signup successful', token });
});

// Login
app.post('/api/login', async (req, res) => {
    const { email, password } = req.body;
    const users = loadUsers();
    const user = users.find(u => u.email === email);
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });

    const valid = await bcrypt.compare(password, user.passwordHash);
    if (!valid) return res.status(401).json({ error: 'Invalid credentials' });

    const token = generateToken(user);
    res.json({ message: 'Login successful', token });
});

// Profile
app.get('/api/profile', authenticateToken, (req, res) => {
    res.json({ user: req.user });
});

// Upload Image
app.post('/upload', (req, res) => {
    upload.single('image')(req, res, (err) => {
        if (err) return res.status(400).json({ error: err.message });
        if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

        const imageUrl = `/uploads/${req.file.filename}`;
        const history = loadHistory();
        history.push({
            type: 'upload',
            imageUrl,
            filename: req.file.filename,
            originalName: req.file.originalname,
            timestamp: new Date().toISOString()
        });
        saveHistory(history);

        res.json({ success: true, imageUrl });
    });
});

// Analyze Outfit
app.post('/analyze', (req, res) => {
    upload.single('image')(req, res, (err) => {
        if (err) return res.status(400).json({ success: false, error: err.message });
        if (!req.file) return res.status(400).json({ success: false, error: 'No file uploaded' });

        const imageUrl = `/uploads/${req.file.filename}`;
        const occasion = req.body.occasion || 'casual';
        const weather = req.body.weather || 'mild';

        const suggestions = {
            general_suggestion: "Your outfit combination works well!",
            reason: "Colors complement each other nicely.",
            premium_suggestion: "Add a stylish watch or bracelet.",
            additional_suggestions: ["Pair with white sneakers", "Add a denim jacket"],
            weather_tips: ["Perfect for current weather"],
            rating: "good",
            confidence: 85,
            occasion,
            weather
        };

        const history = loadHistory();
        history.push({ type: 'analyze', imageUrl, analysis: suggestions, timestamp: new Date().toISOString() });
        saveHistory(history);

        res.json({ success: true, imageUrl, analysis: suggestions });
    });
});

// History
app.get('/api/history', (req, res) => {
    const history = loadHistory()
        .filter(h => h.type === 'analyze')
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    res.json({ success: true, history });
});

// Serve uploads
app.use('/uploads', express.static(uploadDir));

// SPA fallback
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    if (!process.env.JWT_SECRET) console.warn('⚠️ JWT_SECRET is not set!');
});
