from app import db
from datetime import datetime


class User(db.Model):
    """User model for storing user account information"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    medical_history = db.Column(db.Text)  # JSON format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    assessments = db.relationship(
        "HealthAssessment", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    wellness_logs = db.relationship(
        "WellnessLog", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.username}>"


class HealthAssessment(db.Model):
    """Model for storing health assessment results"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    assessment_type = db.Column(
        db.String(50), nullable=False
    )  # 'symptom_check', 'wellness', 'mental_health'
    symptoms = db.Column(db.Text)  # JSON format
    results = db.Column(db.Text)  # JSON format with predictions/recommendations
    urgency_level = db.Column(db.String(20))
    severity_score = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<HealthAssessment {self.assessment_type}>"


class WellnessLog(db.Model):
    """Model for storing daily wellness logs"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    log_date = db.Column(db.Date, nullable=False)
    mood = db.Column(db.String(50))
    sleep_hours = db.Column(db.Float)
    exercise_minutes = db.Column(db.Integer)
    water_intake = db.Column(db.Integer)  # in ml
    energy_level = db.Column(db.Integer)  # 1-10 scale
    stress_level = db.Column(db.Integer)  # 1-10 scale
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<WellnessLog {self.log_date}>"


class HealthMetric(db.Model):
    """Model for storing health metrics"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    metric_type = db.Column(
        db.String(50), nullable=False
    )  # 'heart_rate', 'blood_pressure', 'weight', etc
    value = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<HealthMetric {self.metric_type}>"
