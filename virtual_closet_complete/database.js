// database.js - Database connection setup (Optional)
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// SQLite Database Setup
class Database {
    constructor() {
        this.db = new sqlite3.Database(path.join(__dirname, 'ai_closet.db'), (err) => {
            if (err) {
                console.error('Error opening database:', err.message);
            } else {
                console.log('Connected to SQLite database.');
                this.initTables();
            }
        });
    }

    initTables() {
        // Users table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                premium_status BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Outfits table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS outfits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                filename TEXT NOT NULL,
                original_name TEXT,
                file_path TEXT,
                occasion TEXT,
                analysis_score INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        `);

        // Analysis table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS outfit_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                outfit_id INTEGER,
                occasion TEXT,
                suggestion TEXT,
                reason TEXT,
                premium_suggestion TEXT,
                score INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (outfit_id) REFERENCES outfits (id)
            )
        `);

        // Closet table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS closet_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                outfit_id INTEGER,
                occasion TEXT,
                tags TEXT,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (outfit_id) REFERENCES outfits (id)
            )
        `);

        // Premium subscriptions table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan_type TEXT,
                amount DECIMAL,
                currency TEXT,
                status TEXT DEFAULT 'active',
                start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_date DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        `);
    }

    // User methods
    createUser(username, email, callback) {
        const stmt = this.db.prepare(`
            INSERT INTO users (username, email) 
            VALUES (?, ?)
        `);
        stmt.run([username, email], function(err) {
            callback(err, this ? this.lastID : null);
        });
        stmt.finalize();
    }

    getUserById(id, callback) {
        this.db.get(`
            SELECT * FROM users WHERE id = ?
        `, [id], callback);
    }

    // Outfit methods
    saveOutfit(userId, filename, originalName, filePath, occasion, callback) {
        const stmt = this.db.prepare(`
            INSERT INTO outfits (user_id, filename, original_name, file_path, occasion)
            VALUES (?, ?, ?, ?, ?)
        `);
        stmt.run([userId, filename, originalName, filePath, occasion], function(err) {
            callback(err, this ? this.lastID : null);
        });
        stmt.finalize();
    }

    getOutfitsByUser(userId, callback) {
        this.db.all(`
            SELECT o.*, a.suggestion, a.reason, a.score
            FROM outfits o
            LEFT JOIN outfit_analysis a ON o.id = a.outfit_id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC
        `, [userId], callback);
    }

    // Analysis methods
    saveAnalysis(outfitId, occasion, suggestion, reason, premiumSuggestion, score, callback) {
        const stmt = this.db.prepare(`
            INSERT INTO outfit_analysis (outfit_id, occasion, suggestion, reason, premium_suggestion, score)
            VALUES (?, ?, ?, ?, ?, ?)
        `);
        stmt.run([outfitId, occasion, suggestion, reason, premiumSuggestion, score], function(err) {
            callback(err, this ? this.lastID : null);
        });
        stmt.finalize();
    }

    // Closet methods
    addToCloset(userId, outfitId, occasion, tags, callback) {
        const stmt = this.db.prepare(`
            INSERT INTO closet_items (user_id, outfit_id, occasion, tags)
            VALUES (?, ?, ?, ?)
        `);
        stmt.run([userId, outfitId, occasion, JSON.stringify(tags)], function(err) {
            callback(err, this ? this.lastID : null);
        });
        stmt.finalize();
    }

    getClosetItems(userId, callback) {
        this.db.all(`
            SELECT c.*, o.filename, o.original_name, o.file_path
            FROM closet_items c
            JOIN outfits o ON c.outfit_id = o.id
            WHERE c.user_id = ?
            ORDER BY c.date_added DESC
        `, [userId], callback);
    }

    removeFromCloset(userId, itemId, callback) {
        this.db.run(`
            DELETE FROM closet_items 
            WHERE id = ? AND user_id = ?
        `, [itemId, userId], callback);
    }

    // Premium methods
    createSubscription(userId, planType, amount, currency, callback) {
        const stmt = this.db.prepare(`
            INSERT INTO subscriptions (user_id, plan_type, amount, currency, end_date)
            VALUES (?, ?, ?, ?, datetime('now', '+1 month'))
        `);
        stmt.run([userId, planType, amount, currency], function(err) {
            if (!err) {
                // Update user premium status
                this.db.run(`
                    UPDATE users SET premium_status = 1 WHERE id = ?
                `, [userId]);
            }
            callback(err, this ? this.lastID : null);
        }.bind(this));
        stmt.finalize();
    }

    close() {
        this.db.close((err) => {
            if (err) {
                console.error('Error closing database:', err.message);
            } else {
                console.log('Database connection closed.');
            }
        });
    }
}

// MongoDB Setup (Alternative)
/*
const mongoose = require('mongoose');

// User Schema
const userSchema = new mongoose.Schema({
    username: { type: String, unique: true, required: true },
    email: { type: String, unique: true, required: true },
    premiumStatus: { type: Boolean, default: false },
    createdAt: { type: Date, default: Date.now }
});

// Outfit Schema
const outfitSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    filename: { type: String, required: true },
    originalName: String,
    filePath: String,
    occasion: String,
    analysisScore: Number,
    createdAt: { type: Date, default: Date.now }
});

// Analysis Schema
const analysisSchema = new mongoose.Schema({
    outfitId: { type: mongoose.Schema.Types.ObjectId, ref: 'Outfit', required: true },
    occasion: String,
    suggestion: String,
    reason: String,
    premiumSuggestion: String,
    score: Number,
    createdAt: { type: Date, default: Date.now }
});

// Closet Schema
const closetSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    outfitId: { type: mongoose.Schema.Types.ObjectId, ref: 'Outfit', required: true },
    occasion: String,
    tags: [String],
    dateAdded: { type: Date, default: Date.now }
});

const User = mongoose.model('User', userSchema);
const Outfit = mongoose.model('Outfit', outfitSchema);
const Analysis = mongoose.model('Analysis', analysisSchema);
const Closet = mongoose.model('Closet', closetSchema);

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/ai_closet', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});
*/

module.exports = Database;