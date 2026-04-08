# MindEase - Quick Reference

## ⚡ Command Cheat Sheet

### Start the Application
```bash
cd mindease-flask
.\venv\Scripts\activate          # Activate venv (Windows)
python run.py                    # Start server at http://localhost:5000
```

### Run Tests
```bash
python test.py                   # Run all tests
```

### Initialize Database
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🌐 Application URLs

| Feature | URL |
|---------|-----|
| Home Page | http://localhost:5000/ |
| Symptom Checker | http://localhost:5000/#symptom-check |
| Wellness Tracker | http://localhost:5000/#wellness |
| Mental Health | http://localhost:5000/#mental-health |

---

## 📋 File Overview

| File/Folder | Purpose | Size |
|-------------|---------|------|
| `run.py` | Application entry point | - |
| `app/main.py` | API routes & handlers | 400+ lines |
| `app/models.py` | Database models | 100+ lines |
| `app/services/ai_engine.py` | AI/Gemini integration | 100+ lines |
| `app/services/disease_predictor.py` | Disease prediction logic | 200+ lines |
| `templates/index.html` | Main UI template | 350+ lines |
| `static/css/style.css` | Custom styles | 300+ lines |
| `static/js/app.js` | Frontend interaction | 600+ lines |
| `requirements.txt` | Python dependencies | 6 packages |
| `.env` | Configuration | - |
| `instance/mindease.db` | SQLite database | Auto-created |

---

## 🔌 API Response Examples

### Symptom Check
```json
{
  "urgency": "moderate",
  "urgency_message": "CONSULT A DOCTOR WITHIN DAYS",
  "possible_conditions": [
    {"name": "flu", "confidence": "80.0%"},
    {"name": "cold", "confidence": "60.0%"}
  ],
  "recommendation": "Schedule a doctor's appointment...",
  "severity_score": 0.8
}
```

### User Registration
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "message": "User registered successfully"
}
```

### Wellness Recommendation
```json
{
  "recommendations": "Based on your information...",
  "timestamp": "2024-04-08T12:30:45.123456"
}
```

---

## 🗂️ Project Structure

```
mindease-flask/
├── app/
│   ├── __init__.py              ← Flask app initialization
│   ├── main.py                  ← All API routes
│   ├── models.py                ← Database models
│   └── services/
│       ├── ai_engine.py         ← Gemini AI
│       └── disease_predictor.py ← Triage logic
├── static/
│   ├── css/style.css            ← Styling
│   └── js/app.js                ← Frontend logic
├── templates/
│   └── index.html               ← UI
├── venv/                        ← Virtual environment
├── instance/
│   └── mindease.db              ← Database
├── .env                         ← Configuration
├── requirements.txt             ← Dependencies
├── run.py                       ← Entry point
├── test.py                      ← Test suite
├── SETUP.md                     ← Detailed setup
├── README.md                    ← Documentation
└── QUICKREF.md                  ← This file
```

---

## ✅ Environment Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created (`venv/`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`instance/mindease.db`)
- [ ] `.env` file configured
- [ ] Gemini API key configured (optional)
- [ ] All tests passed (`python test.py`)

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| Database not found | Run database init command |
| Port 5000 in use | Change `FLASK_PORT` in `.env` |
| Gemini API not working | Check API key in `.env` |
| CORS errors | Already configured with Flask-CORS |

---

## 📊 Database Operations

### Add Sample User
```python
from app import db
from app.models import User

user = User(
    username="test_user",
    email="test@example.com",
    password_hash="password123",
    age=25
)
db.session.add(user)
db.session.commit()
```

### Query Users
```python
from app.models import User

users = User.query.all()
user = User.query.filter_by(username="test_user").first()
```

---

## 🔑 Key Skills Demonstrated

✓ **Flask** - Web framework & routing
✓ **SQLAlchemy** - ORM & database modeling
✓ **APIs** - RESTful design with JSON
✓ **Frontend** - HTML/CSS/JavaScript
✓ **AI Integration** - Google Gemini API
✓ **Authentication** - User registration & login
✓ **HTML Forms** - Data collection & validation
✓ **Error Handling** - Try-catch blocks
✓ **Configuration** - Environment variables
✓ **Testing** - Automated test suite

---

## 🎯 Next Steps

1. **Test the app**
   ```bash
   python run.py
   ```
   Open http://localhost:5000 in your browser

2. **Create sample user** (optional)
   - Click "Login" → "Register"
   - Create account to enable data persistence

3. **Configure Gemini API** (optional but recommended)
   - Get API key from https://makersuite.google.com/app/apikey
   - Update `.env` file
   - Restart server to activate AI features

4. **Explore the code**
   - Read comments in `app/main.py`
   - Review database models in `app/models.py`
   - Check frontend logic in `static/js/app.js`

5. **Customize**
   - Modify styles in `static/css/style.css`
   - Update colors & branding
   - Add new features to the UI

---

## 📞 Quick Links

- **Documentation**: `README.md`
- **Setup Guide**: `SETUP.md`
- **Requirements**: `requirements.txt`
- **Configuration**: `.env`

---

**Note**: This application is for educational purposes. Always consult healthcare professionals for medical advice.

Good luck! 🚀
