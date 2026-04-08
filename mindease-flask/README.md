# MindEase - AI Health & Wellness Platform

A Flask-based web application that provides AI-powered health assessments, symptom checking, wellness tracking, and mental health support using Google Gemini AI.

## 🚀 Features

- **AI Symptom Checker**: Predict possible diseases based on symptoms using machine learning triage logic
- **Wellness Assessment**: Get personalized health recommendations powered by Google Gemini AI
- **Mental Health Support**: Receive evidence-based coping strategies and mental health guidance
- **Daily Wellness Logging**: Track mood, sleep, exercise, energy levels, and stress
- **Health Metrics Tracking**: Log health measurements like heart rate, blood pressure, weight
- **User Authentication**: Secure user registration and login
- **Dashboard**: View assessment history and wellness trends

## 📋 Project Structure

```
mindease-flask/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── main.py                  # Routes and API endpoints
│   ├── models.py                # Database models
│   └── services/
│       ├── __init__.py
│       ├── ai_engine.py         # Google Gemini AI integration
│       └── disease_predictor.py # Disease prediction logic
├── static/
│   ├── css/
│   │   └── style.css            # Custom Tailwind styles
│   └── js/
│       └── app.js               # Frontend logic
├── templates/
│   └── index.html               # Main UI template
├── venv/                        # Python virtual environment
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
├── init_db.py                   # Database initialization
├── run.py                       # Application entry point
└── README.md                    # This file
```

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **AI/ML**: Google Generative AI (Gemini)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **APIs**: RESTful with JSON responses
- **CORS**: Enabled for cross-origin requests

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Git (optional)

### Setup Steps

1. **Clone the repository** (or navigate to the project directory)
```bash
cd c:\Users\LENOVO\Desktop\Mindease-AI\mindease-flask
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**

On Windows:
```bash
.\venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables**

Create or edit the `.env` file:
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_change_in_production
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///mindease.db
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

**Important**: Get a free Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

6. **Initialize the database**
```bash
python init_db.py
```

## 🚀 Running the Application

```bash
# Make sure venv is activated
python run.py
```

The application will start at `http://localhost:5000`

### Demo Credentials (if initialized)
- Username: `demo`
- Password: `demo123`

## 📖 API Endpoints

### Health Assessment
- `POST /api/health/symptom-check` - Get disease predictions from symptoms
- `POST /api/health/wellness-check` - Get wellness recommendations
- `POST /api/health/mental-health-support` - Get mental health support
- `POST /api/health/analyze-metrics` - Analyze health metrics with AI

### Wellness Tracking
- `POST /api/wellness/log` - Create a wellness log entry
- `GET /api/wellness/logs` - Retrieve user's wellness logs
- `POST /api/health/metrics` - Add a health metric
- `GET /api/health/metrics` - Get user's health metrics

### User Management
- `POST /api/user/register` - Register a new user
- `POST /api/user/login` - Login user
- `POST /api/user/logout` - Logout user
- `GET /api/user/profile` - Get user profile

### Utilities
- `GET /api/symptoms-list` - Get available symptom categories
- `GET /api/assessments` - Get user's assessments

## 🗄️ Database Models

### User
- Stores user account information
- Relationships: assessments, wellness_logs

### HealthAssessment
- Stores health assessments and predictions
- Types: symptom_check, wellness, mental_health

### WellnessLog
- Daily wellness tracking
- Fields: mood, sleep_hours, exercise_minutes, energy_level, stress_level

### HealthMetric
- Health measurements tracking
- Fields: metric_type, value, unit

## ⚙️ Configuration

### Environment Variables
- `FLASK_ENV` - Development/production environment
- `FLASK_DEBUG` - Enable debug mode
- `SECRET_KEY` - Session security key
- `GEMINI_API_KEY` - Google AI API key (required)
- `DATABASE_URL` - Database connection string
- `FLASK_HOST` - Server host (default: 0.0.0.0)
- `FLASK_PORT` - Server port (default: 5000)

## 📝 Disclaimer

⚠️ **IMPORTANT**: This application is for informational purposes only and should NOT be used as a substitute for professional medical advice. Always consult a qualified healthcare professional for medical diagnosis and treatment.

## 🔐 Security Notes

For production deployment:
1. Change `SECRET_KEY` to a strong random value
2. Set `FLASK_DEBUG=False`
3. Use proper password hashing (bcrypt/werkzeug)
4. Implement HTTPS
5. Use environment variables securely
6. Add input validation and sanitization
7. Implement rate limiting
8. Add CSRF protection

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Support

For issues or questions, please create an issue in the repository or contact the development team.

## 🔗 Useful Links

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Google Generative AI Documentation](https://ai.google.dev/tutorials/python_quickstart)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

---

Built with ❤️ for better health and wellness.
