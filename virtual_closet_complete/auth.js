// auth.js - Authentication middleware and routes
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');

// Configuration
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';
const JWT_EXPIRES_IN = '7d';
const BCRYPT_ROUNDS = 12;

// In-memory user storage (use database in production)
let users = [
    {
        id: 1,
        name: 'Demo User',
        email: 'demo@example.com',
        password: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeHK7YBcqOC7UVe7q', // password123
        premiumStatus: false,
        verified: true,
        createdAt: new Date().toISOString()
    }
];

// Rate limiting
const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // limit each IP to 5 requests per windowMs
    message: { error: 'Too many authentication attempts, please try again later.' }
});

const signupLimiter = rateLimit({
    windowMs: 60 * 60 * 1000, // 1 hour
    max: 3, // limit each IP to 3 signup requests per hour
    message: { error: 'Too many signup attempts, please try again later.' }
});

// Middleware to verify JWT token
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid or expired token' });
        }
        req.user = user;
        next();
    });
};

// Middleware to check if user is premium
const requirePremium = (req, res, next) => {
    if (!req.user.premiumStatus) {
        return res.status(403).json({ 
            error: 'Premium subscription required',
            premiumRequired: true 
        });
    }
    next();
};

// Helper functions
const generateToken = (user) => {
    const payload = {
        id: user.id,
        email: user.email,
        premiumStatus: user.premiumStatus
    };
    return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
};

const hashPassword = async (password) => {
    return await bcrypt.hash(password, BCRYPT_ROUNDS);
};

const verifyPassword = async (password, hashedPassword) => {
    return await bcrypt.compare(password, hashedPassword);
};

const findUserByEmail = (email) => {
    return users.find(user => user.email.toLowerCase() === email.toLowerCase());
};

const findUserById = (id) => {
    return users.find(user => user.id === id);
};

// Validation functions
const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

const validatePasswordFormat = (password) => {
    return password.length >= 6;
};

const sanitizeUser = (user) => {
    const { password, ...sanitizedUser } = user;
    return sanitizedUser;
};

// Authentication routes
const setupAuthRoutes = (app) => {
    
    // Login route
    app.post('/api/auth/login', authLimiter, async (req, res) => {
        try {
            const { email, password, rememberMe } = req.body;

            // Validation
            if (!email || !password) {
                return res.status(400).json({ error: 'Email and password are required' });
            }

            if (!validateEmail(email)) {
                return res.status(400).json({ error: 'Invalid email format' });
            }

            // Find user
            const user = findUserByEmail(email);
            if (!user) {
                return res.status(401).json({ error: 'Invalid email or password' });
            }

            // Check password
            const validPassword = await verifyPassword(password, user.password);
            if (!validPassword) {
                return res.status(401).json({ error: 'Invalid email or password' });
            }

            // Generate token
            const token = generateToken(user);
            
            // Update last login
            user.lastLogin = new Date().toISOString();

            res.json({
                success: true,
                message: 'Login successful',
                token,
                user: sanitizeUser(user),
                expiresIn: rememberMe ? '30d' : '7d'
            });

        } catch (error) {
            console.error('Login error:', error);
            res.status(500).json({ error: 'Login failed' });
        }
    });

    // Signup route
    app.post('/api/auth/signup', signupLimiter, async (req, res) => {
        try {
            const { name, email, password, confirmPassword, newsletter } = req.body;

            // Validation
            if (!name || !email || !password || !confirmPassword) {
                return res.status(400).json({ error: 'All fields are required' });
            }

            if (!validateEmail(email)) {
                return res.status(400).json({ error: 'Invalid email format' });
            }

            if (!validatePasswordFormat(password)) {
                return res.status(400).json({ error: 'Password must be at least 6 characters long' });
            }

            if (password !== confirmPassword) {
                return res.status(400).json({ error: 'Passwords do not match' });
            }

            // Check if user already exists
            if (findUserByEmail(email)) {
                return res.status(409).json({ error: 'Email already registered' });
            }

            // Hash password
            const hashedPassword = await hashPassword(password);

            // Create new user
            const newUser = {
                id: Date.now(),
                name: name.trim(),
                email: email.toLowerCase().trim(),
                password: hashedPassword,
                premiumStatus: false,
                verified: false,
                newsletter: newsletter || false,
                createdAt: new Date().toISOString(),
                lastLogin: null
            };

            users.push(newUser);

            // Generate token
            const token = generateToken(newUser);

            res.status(201).json({
                success: true,
                message: 'Account created successfully',
                token,
                user: sanitizeUser(newUser)
            });

        } catch (error) {
            console.error('Signup error:', error);
            res.status(500).json({ error: 'Account creation failed' });
        }
    });

    // Logout route
    app.post('/api/auth/logout', authenticateToken, (req, res) => {
        // In a real app, you might want to blacklist the token
        res.json({
            success: true,
            message: 'Logged out successfully'
        });
    });

    // Get current user profile
    app.get('/api/auth/profile', authenticateToken, (req, res) => {
        const user = findUserById(req.user.id);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        res.json({
            success: true,
            user: sanitizeUser(user)
        });
    });

    // Update user profile
    app.put('/api/auth/profile', authenticateToken, async (req, res) => {
        try {
            const { name, email, currentPassword, newPassword } = req.body;
            const user = findUserById(req.user.id);

            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }

            // Update name
            if (name && name.trim()) {
                user.name = name.trim();
            }

            // Update email
            if (email && email !== user.email) {
                if (!validateEmail(email)) {
                    return res.status(400).json({ error: 'Invalid email format' });
                }
                
                if (findUserByEmail(email)) {
                    return res.status(409).json({ error: 'Email already in use' });
                }
                
                user.email = email.toLowerCase().trim();
            }

            // Update password
            if (newPassword) {
                if (!currentPassword) {
                    return res.status(400).json({ error: 'Current password required' });
                }

                const validCurrentPassword = await verifyPassword(currentPassword, user.password);
                if (!validCurrentPassword) {
                    return res.status(401).json({ error: 'Current password is incorrect' });
                }

                if (!validatePasswordFormat(newPassword)) {
                    return res.status(400).json({ error: 'New password must be at least 6 characters long' });
                }

                user.password = await hashPassword(newPassword);
            }

            user.updatedAt = new Date().toISOString();

            res.json({
                success: true,
                message: 'Profile updated successfully',
                user: sanitizeUser(user)
            });

        } catch (error) {
            console.error('Profile update error:', error);
            res.status(500).json({ error: 'Profile update failed' });
        }
    });

    // Delete account
    app.delete('/api/auth/account', authenticateToken, async (req, res) => {
        try {
            const { password } = req.body;
            const user = findUserById(req.user.id);

            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }

            // Verify password
            if (password) {
                const validPassword = await verifyPassword(password, user.password);
                if (!validPassword) {
                    return res.status(401).json({ error: 'Password is incorrect' });
                }
            }

            // Remove user from array (in production, mark as deleted instead)
            const userIndex = users.findIndex(u => u.id === req.user.id);
            if (userIndex > -1) {
                users.splice(userIndex, 1);
            }

            res.json({
                success: true,
                message: 'Account deleted successfully'
            });

        } catch (error) {
            console.error('Account deletion error:', error);
            res.status(500).json({ error: 'Account deletion failed' });
        }
    });

    // Forgot password
    app.post('/api/auth/forgot-password', authLimiter, async (req, res) => {
        try {
            const { email } = req.body;

            if (!email || !validateEmail(email)) {
                return res.status(400).json({ error: 'Valid email address required' });
            }

            const user = findUserByEmail(email);
            
            // Always return success for security (don't reveal if email exists)
            res.json({
                success: true,
                message: 'If this email is registered, you will receive reset instructions'
            });

            // In production, send actual email here
            if (user) {
                console.log(`Password reset requested for: ${email}`);
                // Generate reset token and send email
            }

        } catch (error) {
            console.error('Forgot password error:', error);
            res.status(500).json({ error: 'Request failed' });
        }
    });

    // Reset password
    app.post('/api/auth/reset-password', authLimiter, async (req, res) => {
        try {
            const { token, newPassword } = req.body;

            if (!token || !newPassword) {
                return res.status(400).json({ error: 'Token and new password are required' });
            }

            if (!validatePasswordFormat(newPassword)) {
                return res.status(400).json({ error: 'Password must be at least 6 characters long' });
            }

            // In production, verify reset token here
            // For demo, accept any token
            const hashedPassword = await hashPassword(newPassword);

            res.json({
                success: true,
                message: 'Password reset successfully'
            });

        } catch (error) {
            console.error('Password reset error:', error);
            res.status(500).json({ error: 'Password reset failed' });
        }
    });

    // Verify email
    app.post('/api/auth/verify-email', authenticateToken, (req, res) => {
        const user = findUserById(req.user.id);
        
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        user.verified = true;
        user.verifiedAt = new Date().toISOString();

        res.json({
            success: true,
            message: 'Email verified successfully',
            user: sanitizeUser(user)
        });
    });

    // Social login (Google/Facebook)
    app.post('/api/auth/social-login', async (req, res) => {
        try {
            const { provider, providerId, email, name, avatar } = req.body;

            if (!provider || !providerId || !email) {
                return res.status(400).json({ error: 'Invalid social login data' });
            }

            // Check if user exists
            let user = findUserByEmail(email);

            if (!user) {
                // Create new user
                user = {
                    id: Date.now(),
                    name: name || 'User',
                    email: email.toLowerCase().trim(),
                    password: null, // No password for social login
                    premiumStatus: false,
                    verified: true,
                    provider: provider,
                    providerId: providerId,
                    avatar: avatar,
                    createdAt: new Date().toISOString(),
                    lastLogin: new Date().toISOString()
                };

                users.push(user);
            } else {
                // Update existing user
                user.lastLogin = new Date().toISOString();
                if (!user.provider) {
                    user.provider = provider;
                    user.providerId = providerId;
                }
                if (avatar && !user.avatar) {
                    user.avatar = avatar;
                }
            }

            const token = generateToken(user);

            res.json({
                success: true,
                message: 'Social login successful',
                token,
                user: sanitizeUser(user)
            });

        } catch (error) {
            console.error('Social login error:', error);
            res.status(500).json({ error: 'Social login failed' });
        }
    });

    // Admin routes (for testing)
    app.get('/api/auth/users', (req, res) => {
        // In production, add proper admin authentication
        const sanitizedUsers = users.map(user => sanitizeUser(user));
        res.json({
            success: true,
            users: sanitizedUsers,
            count: users.length
        });
    });
};

// Export everything
module.exports = {
    setupAuthRoutes,
    authenticateToken,
    requirePremium,
    authLimiter,
    signupLimiter,
    findUserByEmail,
    findUserById,
    sanitizeUser,
    generateToken,
    hashPassword,
    verifyPassword
};