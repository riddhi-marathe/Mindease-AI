import json
from datetime import date

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import HealthAssessment, HealthMetric, User, WellnessLog
from .services.ai_engine import AIEngine
from .services.disease_predictor import DiseasePredictors

main_bp = Blueprint("main", __name__)


def _current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def _json_payload():
    return request.get_json(silent=True) or {}


def _assessment_payload(assessment):
    results = {}
    if assessment.results:
        try:
            results = json.loads(assessment.results)
        except json.JSONDecodeError:
            results = {}

    return {
        "id": assessment.id,
        "type": assessment.assessment_type,
        "prediction": (
            results.get("possible_conditions", [{}])[0].get("name")
            if results.get("possible_conditions")
            else results.get("summary", "Assessment")
        ),
        "confidence": (
            results.get("possible_conditions", [{}])[0]
            .get("confidence", "N/A")
            .replace("%", "")
            if results.get("possible_conditions")
            else "N/A"
        ),
        "urgency": assessment.urgency_level,
        "created_at": assessment.created_at.isoformat(),
        "results": results,
    }


def _metric_payload(metric):
    return {
        "id": metric.id,
        "metric_type": metric.metric_type,
        "value": metric.value,
        "unit": metric.unit,
        "recorded_at": metric.recorded_at.isoformat(),
    }


def _log_payload(log):
    return {
        "id": log.id,
        "date": log.log_date.isoformat(),
        "mood": log.mood,
        "sleep_hours": log.sleep_hours,
        "exercise_minutes": log.exercise_minutes,
        "water_intake": log.water_intake,
        "energy_level": log.energy_level,
        "stress_level": log.stress_level,
        "notes": log.notes,
        "created_at": log.created_at.isoformat(),
    }


def _save_assessment(user, assessment_type, results, symptoms=None):
    if not user:
        return None

    assessment = HealthAssessment(
        user_id=user.id,
        assessment_type=assessment_type,
        symptoms=json.dumps(symptoms or {}),
        results=json.dumps(results),
        urgency_level=results.get("urgency"),
        severity_score=results.get("severity_score"),
        notes=results.get("recommendation") or results.get("support"),
    )
    db.session.add(assessment)
    db.session.commit()
    return assessment


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/login")
def login_page():
    return render_template("login.html")


@main_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@main_bp.route("/symptom-check")
def symptom_check_page():
    return render_template("symptom_check.html")


@main_bp.route("/wellness-check")
def wellness_check_page():
    return render_template("wellness_check.html")


@main_bp.route("/mental-check")
def mental_check_page():
    return render_template("mental_check.html")


@main_bp.route("/screening")
def screening_page():
    return render_template("screening.html")


@main_bp.route("/tracker")
def tracker_page():
    return render_template("tracker.html")


@main_bp.route("/chat")
def chat_page():
    return render_template("chat.html")


@main_bp.route("/api/user/register", methods=["POST"])
def register():
    data = _json_payload()
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    age = data.get("age")

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        return jsonify({"error": "Username or email already exists"}), 409

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        age=age,
    )
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id

    return (
        jsonify(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "message": "Registration successful",
            }
        ),
        201,
    )


@main_bp.route("/api/user/login", methods=["POST"])
def login():
    data = _json_payload()
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not password or not (username or email):
        return jsonify({"error": "Username/email and password are required"}), 400

    user = None
    if username:
        user = User.query.filter_by(username=username).first()
    if not user and email:
        user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user.id
    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "message": "Login successful",
        }
    )


@main_bp.route("/api/user/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"})


@main_bp.route("/api/user/profile", methods=["GET", "PUT"])
def user_profile():
    user = _current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    if request.method == "PUT":
        data = _json_payload()
        # Update user fields
        if "age" in data:
            user.age = data["age"]
        if "gender" in data:
            user.gender = data["gender"]
        if "medical_history" in data:
            user.medical_history = data["medical_history"]
        
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"})

    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "age": user.age,
            "gender": user.gender,
            "medical_history": user.medical_history,
        }
    )


@main_bp.route("/profile")
def profile_page():
    user = _current_user()
    if not user:
        return redirect(url_for("main.login_page"))
    return render_template("profile.html", user=user)


@main_bp.route("/api/symptoms-list")
def symptoms_list():
    return jsonify(DiseasePredictors.get_symptom_checklist())


@main_bp.route("/api/health/symptom-check", methods=["POST"])
def symptom_check():
    data = _json_payload()
    symptoms = data.get("symptoms") or []
    age_str = data.get("age")
    age = int(age_str) if age_str and str(age_str).isdigit() else None

    if not symptoms:
        return jsonify({"error": "At least one symptom is required"}), 400

    results = DiseasePredictors.predict_disease(symptoms, age=age or 30)
    _save_assessment(
        _current_user(),
        "symptom_check",
        results,
        symptoms={"symptoms": symptoms, "age": age},
    )
    return jsonify(results)


@main_bp.route("/api/health/wellness-check", methods=["POST"])
def wellness_check():
    data = _json_payload()
    symptoms = data.get("symptoms", "")
    health_history = data.get("health_history", "")
    lifestyle = data.get("lifestyle", "")

    ai = AIEngine()
    recommendations = ai.get_wellness_recommendations(
        symptoms, health_history, lifestyle
    )
    results = {
        "recommendations": recommendations,
        "summary": "Wellness check completed",
    }
    _save_assessment(
        _current_user(),
        "wellness",
        results,
        symptoms=data,
    )
    return jsonify(results)


@main_bp.route("/api/health/mental-health-support", methods=["POST"])
def mental_health_support():
    data = _json_payload()
    ai = AIEngine()
    support = ai.get_mental_health_support(
        data.get("mood_description", ""),
        data.get("stressors", ""),
        data.get("coping_methods", ""),
    )
    # Split support into list for frontend
    support_plan = [line.strip() for line in support.split('\n') if line.strip()]
    results = {
        "support_plan": support_plan,
        "full_support": support,
        "summary": "Mental health guidance generated",
    }
    _save_assessment(
        _current_user(),
        "mental_health",
        results,
        symptoms=data,
    )
    return jsonify(results)


@main_bp.route("/api/health/analyze-metrics", methods=["POST"])
def analyze_metrics():
    data = _json_payload()
    ai = AIEngine()
    analysis = ai.analyze_health_metrics(data)
    # Mock structured response for screening
    results = {
        "health_score": 75,
        "risk_factors": ["Sedentary lifestyle", "Poor diet quality"] if data.get("exercise_frequency") == "never" or data.get("diet_quality") == "poor" else [],
        "recommendations": [
            "Increase physical activity to at least 30 minutes daily",
            "Improve diet by including more fruits and vegetables",
            "Ensure 7-9 hours of sleep per night",
            "Schedule regular health check-ups"
        ],
        "preventive_measures": [
            "Maintain healthy weight",
            "Avoid smoking",
            "Limit alcohol consumption",
            "Stay hydrated"
        ],
        "analysis": analysis,
        "summary": "Health screening completed",
    }
    _save_assessment(
        _current_user(),
        "health_screening",
        results,
        symptoms=data,
    )
    return jsonify(results)


@main_bp.route("/api/health/metrics", methods=["GET", "POST"])
def health_metrics():
    user = _current_user()

    if request.method == "POST":
        if not user:
            return jsonify({"error": "Not authenticated"}), 401

        data = _json_payload()
        metric_type = (data.get("metric_type") or "").strip()
        value = data.get("value")
        unit = data.get("unit", "")

        if not metric_type or value in (None, ""):
            return jsonify({"error": "Metric type and value are required"}), 400

        metric = HealthMetric(
            user_id=user.id,
            metric_type=metric_type,
            value=str(value),
            unit=unit,
        )
        db.session.add(metric)
        db.session.commit()
        return jsonify({"message": "Metric added", "metric": _metric_payload(metric)}), 201

    metrics = (
        HealthMetric.query.filter_by(user_id=user.id).order_by(HealthMetric.recorded_at.desc()).all()
        if user
        else []
    )
    return jsonify({"metrics": [_metric_payload(metric) for metric in metrics]})


@main_bp.route("/api/wellness/log", methods=["POST"])
def create_wellness_log():
    user = _current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    data = _json_payload()
    log = WellnessLog(
        user_id=user.id,
        log_date=date.today(),
        mood=data.get("mood"),
        sleep_hours=data.get("sleep_hours"),
        exercise_minutes=data.get("exercise_minutes"),
        water_intake=data.get("water_intake"),
        energy_level=data.get("energy_level"),
        stress_level=data.get("stress_level"),
        notes=data.get("notes"),
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Wellness log saved", "log": _log_payload(log)}), 201


@main_bp.route("/api/wellness/logs")
def wellness_logs():
    user = _current_user()
    logs = (
        WellnessLog.query.filter_by(user_id=user.id).order_by(WellnessLog.created_at.desc()).all()
        if user
        else []
    )
    return jsonify({"logs": [_log_payload(log) for log in logs]})


@main_bp.route("/api/assessments")
def assessments():
    user = _current_user()
    assessments_list = (
        HealthAssessment.query.filter_by(user_id=user.id)
        .order_by(HealthAssessment.created_at.desc())
        .all()
        if user
        else []
    )
    return jsonify(
        {"assessments": [_assessment_payload(assessment) for assessment in assessments_list]}
    )
