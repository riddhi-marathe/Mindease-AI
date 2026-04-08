# MindEase Setup Guide

## ✅ Installation Complete!

Your MindEase Flask application has been successfully set up! All components are working properly.

### 📊 Test Results
All 5 core tests passed:
- ✓ Flask app and imports
- ✓ Database models  
- ✓ AI engine service
- ✓ Disease predictor service
- ✓ 15+ API routes registered

---

## 🚀 Quick Start

### 1. **Activate Virtual Environment** (if not already active)

```bash
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. **Configure Google Gemini API** (Optional but recommended)

The AI-powered features require a Google Gemini API key:

1. Get your free API key: https://makersuite.google.com/app/apikey
2. Edit the `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### 3. **Start the Server**

```bash
python run.py
```

The server will start at: **http://localhost:5000**

---

## 📁 Project Structure

```
mindease-flask/
├── app/
│   ├── __init__.py                   # Flask app factory
│   ├── main.py                       # All API routes (200+ lines)
│   ├── models.py                     # Database models (4 models)
│   └── services/
│       ├── ai_engine.py              # Google Gemini AI integration
│       └── disease_predictor.py      # Disease triage logic (200+ lines)
│
├── static/
│   ├── css/style.css                 # 300+ lines of custom styles
│   └── js/app.js                     # 600+ lines of frontend logic
│
├── templates/
│   └── index.html                    # Complete UI (350+ lines)
│
├── instance/
│   └── mindease.db                   # SQLite database (created on first run)
│
├── venv/                             # Python virtual environment
├── .env                              # Environment configuration
├── requirements.txt                  # Python dependencies (6 packages)
├── run.py                            # Application entry point
├── init_db.py                        # Database initialization script
├── test.py                           # Test suite (all tests passed ✓)
└── README.md                         # Full documentation
```

---

## 🎯 Features Included

### Backend Features
✓ **Disease Prediction** - Symptom-based triage logic
✓ **AI Wellness** - Google Gemini-powered recommendations  
✓ **Mental Health Support** - Evidence-based guidance
✓ **User Authentication** - Register/Login system
✓ **Health Tracking** - Wellness logs & health metrics
✓ **Database** - SQLAlchemy ORM with 4 models

### Frontend Features
✓ **Responsive UI** - Tailwind CSS design
✓ **Symptom Checker** - Interactive checklist
✓ **Wellness Tracker** - Daily mood & activity logging
✓ **Mental Health Forms** - Mood & stress assessment
✓ **Results Display** - Color-coded health assessments
✓ **Real-time Feedback** - Form validation & alerts

### API Routes (15+ endpoints)
✓ POST `/api/health/symptom-check` - Disease prediction
✓ POST `/api/health/wellness-check` - AI recommendations
✓ POST `/api/health/mental-health-support` - Mental health guidance
✓ POST `/api/wellness/log` - Save daily wellness log
✓ POST `/api/health/metrics` - Log health measurements
✓ GET `/api/wellness/logs` - Retrieve wellness history
✓ GET `/api/health/metrics` - Get health metric history
✓ POST `/api/user/register` - Create new account
✓ POST `/api/user/login` - User authentication
✓ ... and 6 more endpoints

---

## 🔧 Configuration

### .env File Options

```
# Flask Configuration
FLASK_ENV=development              # development or production
FLASK_DEBUG=True                   # Enable debug mode (set False in production)
SECRET_KEY=your_secret_key         # Session security key

# Database
DATABASE_URL=sqlite:///mindease.db # Database connection string

# Google Gemini AI (Optional)
GEMINI_API_KEY=your_api_key        # Get from https://makersuite.google.com/app/apikey

# Server
FLASK_HOST=0.0.0.0                 # Server host
FLASK_PORT=5000                    # Server port
```

---

## 📊 Database Models

### User
```
- id (Integer, PK)
- username (String, Unique)
- email (String, Unique)
- password_hash (String)
- age (Integer)
- gender (String)
- medical_history (Text)
- created_at (DateTime)
```

### HealthAssessment
```
- id (Integer, PK)
- user_id (Integer, FK)
- assessment_type (String) - symptom_check, wellness, mental_health
- symptoms (Text - JSON)
- results (Text - JSON)
- urgency_level (String) - critical, high, moderate, low
- severity_score (Float)
```

### WellnessLog
```
- id (Integer, PK)
- user_id (Integer, FK)
- log_date (Date)
- mood (String)
- sleep_hours (Float)
- exercise_minutes (Integer)
- water_intake (Integer)
- energy_level (Integer, 1-10 scale)
- stress_level (Integer, 1-10 scale)
```

### HealthMetric
```
- id (Integer, PK)
- user_id (Integer, FK)
- metric_type (String)
- value (String)
- unit (String)
- recorded_at (DateTime)
```

---

## 🧪 Running Tests

```bash
python test.py
```

All tests should show ✓ PASS status.

---

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask_cors'"
**Solution**: Reinstall dependencies
```bash
pip install --force-reinstall -r requirements.txt
```

### Issue: Database not found
**Solution**: Create database
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database created!')"
```

### Issue: AI features not working
**Solution**: Configure your Gemini API key in `.env` file. Note: The app will still work without it, showing informative messages instead.

### Issue: "RuntimeError: Working outside of application context"
**Solution**: This usually means the Flask app context isn't set up. Make sure you're using routes through the Flask server, not running code directly.

---

## 📝 Example API Usage

### Check Symptoms
```bash
curl -X POST http://localhost:5000/api/health/symptom-check \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["fever", "cough"],
    "age": 30,
    "medical_history": []
  }'
```

### Register User
```bash
curl -X POST http://localhost:5000/api/user/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password",
    "age": 30,
    "gender": "Male"
  }'
```

### Save Wellness Log
```bash
curl -X POST http://localhost:5000/api/wellness/log \
  -H "Content-Type: application/json" \
  -d '{
    "mood": "good",
    "sleep_hours": 8,
    "exercise_minutes": 30,
    "energy_level": 8,
    "stress_level": 3
  }'
```

---

## 🔒 Security Recommendations

For production deployment:
1. Change `SECRET_KEY` to a strong random value
2. Set `FLASK_DEBUG=False`
3. Use proper password hashing (implement bcrypt)
4. Add HTTPS/SSL certificates
5. Implement CSRF protection
6. Add input validation & sanitization
7. Use rate limiting
8. Set secure session cookies
9. Keep dependencies updated
10. Use environment variables for all secrets

---

## 📚 Technologies Used

- **Python 3.8+**
- **Flask 3.0+**
- **SQLAlchemy 2.0** with Flask-SQLAlchemy
- **Google Generative AI** (Gemini)
- **SQLite** Database
- **Tailwind CSS** 3.0+
- **HTML5 / CSS3 / Vanilla JavaScript**
- **Flask-CORS** for cross-origin requests

---

## 🎓 Learning Resources

- [Flask Official Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Google Generative AI Guide](https://ai.google.dev/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [RESTful API Design](https://restfulapi.net/)

---

## 📞 Support & Contributing

For issues or feature requests:
1. Check the README.md for common issues
2. Review the code comments for implementation details
3. Run the test suite: `python test.py`
4. Check the browser console for frontend errors

---

## ✨ What's Next?

1. **Customize**: Modify styles in `static/css/style.css`
2. **Expand**: Add new routes in `app/main.py`
3. **Enhance**: Improve AI responses in `app/services/ai_engine.py`
4. **Deploy**: Use Gunicorn/uWSGI for production

---

## 📄 License

This project is provided as-is for educational and personal use.

---

## Disclaimer

⚠️ **IMPORTANT**: This application is for informational purposes only. It should NOT be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare professional.

---

**Happy coding! 🚀**
