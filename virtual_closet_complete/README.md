# AI Closet - Your Smart Fashion Assistant

A complete web application that helps users analyze their outfits and manage their virtual closet using AI-powered fashion recommendations.

## Features

- 📷 **Outfit Upload**: Upload photos of your outfits
- 🎯 **AI Analysis**: Get intelligent fashion suggestions based on occasion
- 👗 **Virtual Closet**: Save and manage your favorite outfits
- 💎 **Premium Features**: Advanced analysis and personalized recommendations
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### Option 1: Using the HTML File (Frontend Only)
1. Download the `ai_closet_frontend.html` file
2. Open it in any modern web browser
3. Start uploading and analyzing outfits!

### Option 2: Full Stack Setup

#### Prerequisites
- Node.js (v14 or higher)
- npm (Node Package Manager)

#### Installation

1. **Create Project Directory**
   ```bash
   mkdir ai-closet
   cd ai-closet
   ```

2. **Create Required Files**
   
   Create `server.js` with the backend code provided
   
   Create `package.json` with the dependencies listed
   
   Create a `public` folder and place the HTML file as `index.html`

3. **Install Dependencies**
   ```bash
   npm install
   ```

4. **Create Upload Directory**
   ```bash
   mkdir uploads
   ```

5. **Start the Server**
   ```bash
   npm start
   ```
   
   For development with auto-restart:
   ```bash
   npm run dev
   ```

6. **Access the Application**
   Open your browser and go to `http://localhost:3000`

## File Structure

```
ai-closet/
├── server.js              # Main server file
├── package.json           # Dependencies and scripts
├── database.js           # Database setup (optional)
├── public/
│   └── index.html        # Frontend application
├── uploads/              # Uploaded outfit images
└── README.md            # This file
```

## API Endpoints

### Upload Outfit
```
POST /api/upload-outfit
Content-Type: multipart/form-data
Body: outfit (file)
```

### Analyze Outfit
```
POST /api/analyze-outfit
Content-Type: application/json
Body: { "occasion": "casual", "outfitId": 123 }
```

### Save to Closet
```
POST /api/save-to-closet
Content-Type: application/json
Body: { "outfitId": 123, "occasion": "casual", "userId": "default" }
```

### Get Closet Items
```
GET /api/closet/:userId
```

### Remove from Closet
```
DELETE /api/closet/:outfitId
```

### Premium Subscription
```
POST /api/premium/subscribe
Content-Type: application/json
Body: { "userId": "default", "plan": "monthly" }
```

## Occasion Types

- **Casual**: Everyday, relaxed outfits
- **Formal**: Professional, business meetings
- **Business**: Office wear, corporate events
- **Party**: Social events, celebrations
- **Workout**: Exercise, gym activities
- **Date**: Romantic outings
- **Wedding**: Wedding guest attire

## Premium Features

- Advanced AI outfit analysis
- Personalized recommendations
- Color matching suggestions
- Seasonal wardrobe planning
- Style trend alerts
- Extended closet storage

## Technologies Used

### Frontend
- HTML5
- CSS3 (with modern gradients and animations)
- Vanilla JavaScript
- Responsive design
- File API for image handling

### Backend
- Node.js
- Express.js
- Multer (file uploads)
- Sharp (image processing)
- CORS support

### Optional Database
- SQLite (lightweight)
- MongoDB (scalable option)

## Development

### Adding New Features

1. **New Occasion Types**: Add to `fashionRules` object in `server.js`
2. **Custom Analysis Rules**: Modify the analysis logic in `/api/analyze-outfit`
3. **UI Improvements**: Update the HTML/CSS/JavaScript in `public/index.html`

### Database Integration

To use persistent storage, uncomment and configure the database setup in `database.js`

For SQLite:
```bash
npm install sqlite3
```

For MongoDB:
```bash
npm install mongoose
```

## Deployment

### Local Development
```bash
npm run dev
```

### Production
```bash
npm start
```

### Environment Variables
Create a `.env` file for production:
```env
PORT=3000
NODE_ENV=production
DATABASE_URL=your_database_url
UPLOAD_PATH=./uploads
```

## Browser Support

- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please contact the development team or create an issue in the repository.

---

**Note**: This is a demo application. In production, you should implement proper authentication, input validation, and security measures.