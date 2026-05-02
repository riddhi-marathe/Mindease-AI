import json
from collections import Counter
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import HealthAssessment, HealthMetric, User, WellnessLog
from .services.ai_engine import AIEngine
from .services.disease_predictor import DiseasePredictors

main_bp = Blueprint("main", __name__)

ASSESSMENT_TITLES = {
    "symptom_check": "Symptom check",
    "wellness": "Wellness check",
    "mental_health": "Mental health support",
    "health_screening": "Health screening",
}

ASSESSMENT_ICONS = {
    "symptom_check": "stethoscope",
    "wellness": "heart",
    "mental_health": "brain",
    "health_screening": "clipboard-list",
}

METRIC_LABELS = {
    "heart_rate": "Heart rate",
    "blood_pressure": "Blood pressure",
    "weight": "Weight",
    "temperature": "Temperature",
    "blood_sugar": "Blood sugar",
}


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


def _average(values, precision=1):
    numeric_values = [value for value in values if isinstance(value, (int, float))]
    if not numeric_values:
        return None
    return round(sum(numeric_values) / len(numeric_values), precision)


def _relative_date(value):
    if not value:
        return ""

    target_date = value.date() if isinstance(value, datetime) else value
    delta_days = (date.today() - target_date).days

    if delta_days <= 0:
        return "Today"
    if delta_days == 1:
        return "Yesterday"
    if delta_days < 7:
        return f"{delta_days} days ago"
    return target_date.strftime("%b %d, %Y")


def _format_mood_label(raw_mood):
    if not raw_mood:
        return None
    return str(raw_mood).replace("_", " ").strip().title()


def _check_in_streak(logs):
    log_dates = {log.log_date for log in logs if log.log_date}
    streak = 0
    current_day = date.today()

    while current_day in log_dates:
        streak += 1
        current_day -= timedelta(days=1)

    return streak


def _weekly_energy_series(logs):
    latest_by_day = {}
    for log in logs:
        if not log.log_date:
            continue
        existing = latest_by_day.get(log.log_date)
        if not existing or log.created_at > existing.created_at:
            latest_by_day[log.log_date] = log

    series = []
    for offset in range(6, -1, -1):
        day = date.today() - timedelta(days=offset)
        log = latest_by_day.get(day)
        energy_value = log.energy_level if log and log.energy_level is not None else 0
        series.append(
            {
                "label": day.strftime("%a"),
                "value": energy_value,
                "height": max(16, energy_value * 10) if energy_value else 12,
                "has_entry": bool(log),
                "mood": _format_mood_label(log.mood) if log else "No check-in",
            }
        )

    return series


def _build_activity_feed(assessments, logs, metrics):
    items = []

    for assessment in assessments[:5]:
        assessment_name = ASSESSMENT_TITLES.get(
            assessment.assessment_type, "Health assessment"
        )
        detail = "Saved to your history"
        if assessment.urgency_level:
            detail = f"Urgency: {assessment.urgency_level.replace('_', ' ').title()}"

        items.append(
            {
                "kind": "assessment",
                "icon": ASSESSMENT_ICONS.get(assessment.assessment_type, "file-text"),
                "title": f"{assessment_name} completed",
                "detail": detail,
                "time_label": _relative_date(assessment.created_at),
                "sort_key": assessment.created_at,
            }
        )

    for log in logs[:5]:
        detail_parts = []
        if log.sleep_hours is not None:
            detail_parts.append(f"{log.sleep_hours:g}h sleep")
        if log.energy_level is not None:
            detail_parts.append(f"energy {log.energy_level}/10")
        if log.stress_level is not None:
            detail_parts.append(f"stress {log.stress_level}/10")

        items.append(
            {
                "kind": "log",
                "icon": "smile",
                "title": "Daily wellness log added",
                "detail": " | ".join(detail_parts) or "Check-in captured for today",
                "time_label": _relative_date(log.log_date),
                "sort_key": log.created_at,
            }
        )

    for metric in metrics[:5]:
        metric_name = METRIC_LABELS.get(
            metric.metric_type, metric.metric_type.replace("_", " ").title()
        )
        metric_value = f"{metric.value} {metric.unit}".strip()
        items.append(
            {
                "kind": "metric",
                "icon": "activity",
                "title": f"{metric_name} recorded",
                "detail": metric_value,
                "time_label": _relative_date(metric.recorded_at),
                "sort_key": metric.recorded_at,
            }
        )

    ordered_items = sorted(items, key=lambda item: item["sort_key"], reverse=True)
    return ordered_items[:6]


def _build_focus_items(assessments, logs, metrics, avg_sleep, avg_stress, weekly_checkins):
    focus_items = []

    if not logs:
        focus_items.append("Complete a wellness check to start building your trend history.")
    else:
        if avg_stress is not None and avg_stress >= 7:
            focus_items.append(
                "Stress has been elevated lately. A short grounding exercise could help today."
            )
        if avg_sleep is not None and avg_sleep < 7:
            focus_items.append(
                "Your sleep average is below the recommended range. Aim for a calmer wind-down tonight."
            )
        if weekly_checkins < 3:
            focus_items.append(
                "Add a few more check-ins this week to unlock stronger dashboard insights."
            )

    if not assessments:
        focus_items.append(
            "Run a screening, wellness check, or symptom check to build your assessment history."
        )

    if not metrics:
        focus_items.append(
            "Track at least one health metric so your dashboard can show more health context."
        )

    if not focus_items:
        focus_items.append(
            "Your routine looks steady. Keep logging consistently so trends stay meaningful."
        )

    return focus_items[:3]


def _get_critical_assessments(assessments):
    """Extract critical and high-urgency assessments"""
    critical = []
    for assessment in assessments:
        urgency = assessment.urgency_level or "routine"
        if urgency.lower() in ["critical", "emergency", "high"]:
            critical.append(assessment)
    return critical


def _get_hospital_recommendations():
    """Get a list of recommended nearby hospitals
    Returns sample hospitals - in production, would use user location and real API
    """
    return [
        {
            "name": "Emergency Care Center",
            "address": "123 Medical Plaza, Healthcare District",
            "distance": "0.8 km",
            "phone": "(555) 123-4567",
            "rating": 4.8,
            "services": ["Emergency", "Mental Health Crisis", "24/7 Support"],
            "lat": 40.7128,
            "lng": -74.0060,
        },
        {
            "name": "Wellness Crisis Unit",
            "address": "456 Health Ave, Downtown",
            "distance": "1.2 km", 
            "phone": "(555) 234-5678",
            "rating": 4.6,
            "services": ["Mental Health", "Crisis Intervention", "Counseling"],
            "lat": 40.7138,
            "lng": -74.0050,
        },
        {
            "name": "Community Mental Health Hospital",
            "address": "789 Care Road, Central",
            "distance": "1.5 km",
            "phone": "(555) 345-6789",
            "rating": 4.7,
            "services": ["Psychiatric Care", "Emergency Services", "Support Groups"],
            "lat": 40.7118,
            "lng": -74.0070,
        },
    ]


def _build_dashboard_context(user):
    guest_series = _weekly_energy_series([])
    if not user:
        return {
            "is_guest": True,
            "display_name": "there",
            "summary": {
                "assessments": 0,
                "weekly_checkins": 0,
                "streak": 0,
                "metrics": 0,
                "avg_sleep": None,
                "avg_energy": None,
                "avg_stress": None,
                "wellness_score": None,
            },
            "activity_feed": [],
            "weekly_energy": guest_series,
            "dominant_mood": None,
            "latest_assessment": None,
            "trend_message": "Sign in to see your saved history, trend snapshots, and personalized follow-up suggestions.",
            "sleep_message": "Track sleep and daily check-ins to reveal energy patterns over time.",
            "stress_message": "Use the wellness tools to capture stress and mood signals in one place.",
            "focus_items": [
                "Sign in or create an account to save your dashboard history.",
                "Start with a wellness check if you want a quick self-reflection.",
                "Use symptom check or screening tools anytime you need more context.",
            ],
            "highlights": ["Guest preview mode", "History unlocks after login"],
        }

    assessments = (
        HealthAssessment.query.filter_by(user_id=user.id)
        .order_by(HealthAssessment.created_at.desc())
        .all()
    )
    logs = (
        WellnessLog.query.filter_by(user_id=user.id)
        .order_by(WellnessLog.created_at.desc())
        .all()
    )
    metrics = (
        HealthMetric.query.filter_by(user_id=user.id)
        .order_by(HealthMetric.recorded_at.desc())
        .all()
    )

    # Check for critical assessments
    critical_assessments = _get_critical_assessments(assessments)
    has_critical_issue = len(critical_assessments) > 0

    weekly_cutoff = date.today() - timedelta(days=6)
    weekly_logs = [log for log in logs if log.log_date and log.log_date >= weekly_cutoff]

    avg_sleep = _average([log.sleep_hours for log in logs if log.sleep_hours is not None])
    avg_energy = _average(
        [log.energy_level for log in logs if log.energy_level is not None]
    )
    avg_stress = _average(
        [log.stress_level for log in logs if log.stress_level is not None]
    )

    score_parts = []
    if avg_energy is not None:
        score_parts.append(avg_energy * 10)
    if avg_stress is not None:
        score_parts.append((11 - avg_stress) * 10)
    if avg_sleep is not None:
        score_parts.append(min(avg_sleep / 8, 1) * 100)
    wellness_score = round(sum(score_parts) / len(score_parts)) if score_parts else None

    mood_counter = Counter(
        _format_mood_label(log.mood) for log in logs if _format_mood_label(log.mood)
    )
    dominant_mood = mood_counter.most_common(1)[0][0] if mood_counter else None

    latest_assessment = None
    if assessments:
        latest = assessments[0]
        payload = _assessment_payload(latest)
        latest_assessment = {
            "title": ASSESSMENT_TITLES.get(latest.assessment_type, "Assessment"),
            "result": payload["prediction"],
            "urgency": (payload["urgency"] or "routine").replace("_", " ").title(),
            "created_label": _relative_date(latest.created_at),
        }

    weekly_checkins = len(weekly_logs)
    highlights = []
    if weekly_checkins:
        checkin_label = "check-in" if weekly_checkins == 1 else "check-ins"
        highlights.append(f"{weekly_checkins} {checkin_label} in the last 7 days")
    if dominant_mood:
        highlights.append(f"Most common mood: {dominant_mood}")
    if assessments:
        highlights.append(f"{len(assessments)} saved assessments")
    if not highlights:
        highlights.append("No saved activity yet")

    return {
        "is_guest": False,
        "display_name": user.username,
        "summary": {
            "assessments": len(assessments),
            "weekly_checkins": weekly_checkins,
            "streak": _check_in_streak(logs),
            "metrics": len(metrics),
            "avg_sleep": avg_sleep,
            "avg_energy": avg_energy,
            "avg_stress": avg_stress,
            "wellness_score": wellness_score,
        },
        "activity_feed": _build_activity_feed(assessments, logs, metrics),
        "weekly_energy": _weekly_energy_series(weekly_logs),
        "dominant_mood": dominant_mood,
        "latest_assessment": latest_assessment,
        "trend_message": (
            f"Your energy average is {avg_energy}/10 this week."
            if avg_energy is not None
            else "Add a few daily logs to uncover your weekly energy trend."
        ),
        "sleep_message": (
            f"You are averaging {avg_sleep} hours of sleep."
            if avg_sleep is not None
            else "Start logging sleep to see whether rest is shaping your mood and energy."
        ),
        "stress_message": (
            f"Stress is averaging {avg_stress}/10."
            if avg_stress is not None
            else "Stress insights appear after a few wellness logs."
        ),
        "focus_items": _build_focus_items(
            assessments, logs, metrics, avg_sleep, avg_stress, weekly_checkins
        ),
        "highlights": highlights,
        "has_critical_issue": has_critical_issue,
        "critical_assessments": [
            {
                "title": ASSESSMENT_TITLES.get(a.assessment_type, "Assessment"),
                "urgency": (a.urgency_level or "routine").replace("_", " ").title(),
                "severity_score": a.severity_score or 0,
                "created_label": _relative_date(a.created_at),
            }
            for a in critical_assessments[:3]
        ],
        "hospital_recommendations": _get_hospital_recommendations(),
    }


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/login")
def login_page():
    return render_template("login.html")


@main_bp.route("/dashboard")
def dashboard():
    user = _current_user()
    return render_template(
        "dashboard.html",
        dashboard=_build_dashboard_context(user),
        user=user,
    )


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
        if user else []
    )
    return jsonify(
        {"assessments": [_assessment_payload(assessment) for assessment in assessments_list]}
    )
