from flask import Blueprint, render_template, request, jsonify, session
from app import db
from app.models import User, HealthAssessment, WellnessLog, HealthMetric
from app.services.ai_engine import AIEngine
from app.services.disease_predictor import DiseasePredictors
from datetime import datetime
import json
from functools import wraps

main_bp = Blueprint('main', __name__)

# Initialize services
ai_engine = AIEngine()
disease_predictor = DiseasePredictors()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ==================== Routes ====================

@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@main_bp.route('/login')
def login():
    """Login page"""
    return render_template('login.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')


@main_bp.route('/symptom-check')
@login_required
def symptom_check_page():
    """Symptom check page"""
    return render_template('symptom_check.html')


@main_bp.route('/wellness-check')
@login_required
def wellness_check_page():
    """Wellness check page"""
    return render_template('wellness_check.html')


@main_bp.route('/mental-check')
@login_required
def mental_check_page():
    """Mental health check page"""
    return render_template('mental_check.html')


@main_bp.route('/screening')
@login_required
def screening_page():
    """Health screening page"""
    return render_template('screening.html')


@main_bp.route('/tracker')
@login_required
def tracker_page():
    """Health tracker page"""
    return render_template('tracker.html')


@main_bp.route('/chat')
@login_required
def chat_page():
    """AI chat page"""
    return render_template('chat.html')


@main_bp.route('/api/health/symptom-check', methods=['POST'])
def symptom_check():
    """
    Perform symptom-based disease prediction
    Expected JSON: {
        'symptoms': ['fever', 'cough'],
        'age': 30,
        'medical_history': []
    }
    """
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        age = data.get('age')
        medical_history = data.get('medical_history', [])
        
        if not symptoms:
            return jsonify({'error': 'No symptoms provided'}), 400
        
        # Get prediction
        prediction = disease_predictor.predict_disease(symptoms, age, medical_history)
        
        # Save to database if user is logged in
        if 'user_id' in session:
            assessment = HealthAssessment(
                user_id=session['user_id'],
                assessment_type='symptom_check',
                symptoms=json.dumps(symptoms),
                results=json.dumps(prediction),
                urgency_level=prediction.get('urgency'),
                severity_score=prediction.get('severity_score'),
            )
            db.session.add(assessment)
            db.session.commit()
        
        return jsonify(prediction), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/health/wellness-check', methods=['POST'])
def wellness_check():
    """
    Generate AI-based wellness recommendations
    Expected JSON: {
        'symptoms': 'string',
        'health_history': 'string',
        'lifestyle': 'string'
    }
    """
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', '')
        health_history = data.get('health_history', '')
        lifestyle = data.get('lifestyle', '')
        
        # Get AI recommendations
        recommendations = ai_engine.get_wellness_recommendations(
            symptoms, health_history, lifestyle
        )
        
        # Save to database if user is logged in
        if 'user_id' in session:
            assessment = HealthAssessment(
                user_id=session['user_id'],
                assessment_type='wellness',
                symptoms=json.dumps({
                    'symptoms': symptoms,
                    'health_history': health_history,
                    'lifestyle': lifestyle
                }),
                results=json.dumps({'recommendations': recommendations}),
            )
            db.session.add(assessment)
            db.session.commit()
        
        return jsonify({
            'recommendations': recommendations,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/health/mental-health-support', methods=['POST'])
def mental_health_support():
    """
    Get mental health support and coping strategies
    Expected JSON: {
        'mood': 'string',
        'stressors': 'string',
        'coping_methods': 'string'
    }
    """
    try:
        data = request.get_json()
        mood = data.get('mood', '')
        stressors = data.get('stressors', '')
        coping_methods = data.get('coping_methods', '')
        
        # Get mental health support
        support = ai_engine.get_mental_health_support(mood, stressors, coping_methods)
        
        # Save to database if user is logged in
        if 'user_id' in session:
            assessment = HealthAssessment(
                user_id=session['user_id'],
                assessment_type='mental_health',
                symptoms=json.dumps({
                    'mood': mood,
                    'stressors': stressors,
                    'coping_methods': coping_methods
                }),
                results=json.dumps({'support': support}),
            )
            db.session.add(assessment)
            db.session.commit()
        
        return jsonify({
            'support': support,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/wellness/log', methods=['POST'])
@login_required
def create_wellness_log():
    """
    Create a wellness log entry
    Expected JSON: {
        'mood': 'string',
        'sleep_hours': float,
        'exercise_minutes': int,
        'water_intake': int,
        'energy_level': int (1-10),
        'stress_level': int (1-10),
        'notes': 'string'
    }
    """
    try:
        data = request.get_json()
        
        log = WellnessLog(
            user_id=session['user_id'],
            log_date=datetime.utcnow().date(),
            mood=data.get('mood'),
            sleep_hours=data.get('sleep_hours'),
            exercise_minutes=data.get('exercise_minutes'),
            water_intake=data.get('water_intake'),
            energy_level=data.get('energy_level'),
            stress_level=data.get('stress_level'),
            notes=data.get('notes'),
        )
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'id': log.id,
            'message': 'Wellness log created successfully',
            'log_date': log.log_date.isoformat()
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/wellness/logs', methods=['GET'])
@login_required
def get_wellness_logs():
    """
    Get user's wellness logs
    """
    try:
        logs = WellnessLog.query.filter_by(user_id=session['user_id']).order_by(
            WellnessLog.log_date.desc()
        ).limit(30).all()
        
        return jsonify({
            'logs': [{
                'id': log.id,
                'date': log.log_date.isoformat(),
                'mood': log.mood,
                'sleep_hours': log.sleep_hours,
                'exercise_minutes': log.exercise_minutes,
                'water_intake': log.water_intake,
                'energy_level': log.energy_level,
                'stress_level': log.stress_level,
                'notes': log.notes,
            } for log in logs]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/health/metrics', methods=['POST'])
@login_required
def add_health_metric():
    """
    Add a health metric
    Expected JSON: {
        'metric_type': 'heart_rate|blood_pressure|weight|temperature',
        'value': 'string',
        'unit': 'string'
    }
    """
    try:
        data = request.get_json()
        
        metric = HealthMetric(
            user_id=session['user_id'],
            metric_type=data.get('metric_type'),
            value=data.get('value'),
            unit=data.get('unit'),
        )
        
        db.session.add(metric)
        db.session.commit()
        
        return jsonify({
            'id': metric.id,
            'message': 'Health metric recorded successfully'
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/health/metrics', methods=['GET'])
@login_required
def get_health_metrics():
    """
    Get user's health metrics
    """
    try:
        metrics = HealthMetric.query.filter_by(user_id=session['user_id']).order_by(
            HealthMetric.recorded_at.desc()
        ).limit(50).all()
        
        return jsonify({
            'metrics': [{
                'id': metric.id,
                'metric_type': metric.metric_type,
                'value': metric.value,
                'unit': metric.unit,
                'recorded_at': metric.recorded_at.isoformat(),
            } for metric in metrics]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/assessments', methods=['GET'])
@login_required
def get_assessments():
    """
    Get user's health assessments
    """
    try:
        assessment_type = request.args.get('type')
        
        query = HealthAssessment.query.filter_by(user_id=session['user_id'])
        if assessment_type:
            query = query.filter_by(assessment_type=assessment_type)
        
        assessments = query.order_by(HealthAssessment.created_at.desc()).limit(50).all()
        
        return jsonify({
            'assessments': [{
                'id': assessment.id,
                'type': assessment.assessment_type,
                'urgency_level': assessment.urgency_level,
                'severity_score': assessment.severity_score,
                'created_at': assessment.created_at.isoformat(),
                'results': json.loads(assessment.results) if assessment.results else {},
            } for assessment in assessments]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/user/register', methods=['POST'])
def register_user():
    """
    Register a new user
    Expected JSON: {
        'username': 'string',
        'email': 'string',
        'password': 'string',
        'age': int,
        'gender': 'string'
    }
    """
    try:
        data = request.get_json()
        
        # Check if user exists
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=data.get('password'),  # In production, use proper hashing
            age=data.get('age'),
            gender=data.get('gender'),
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'User registered successfully'
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/user/login', methods=['POST'])
def login_user():
    """
    Login user
    Expected JSON: {
        'username': 'string',
        'password': 'string'
    }
    """
    try:
        data = request.get_json()
        
        user = User.query.filter_by(username=data.get('username')).first()
        
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # In production, use proper password verification
        if user.password_hash != data.get('password'):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        session['user_id'] = user.id
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'Login successful'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/user/logout', methods=['POST'])
def logout_user():
    """
    Logout user
    """
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200


@main_bp.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """
    Get user profile
    """
    try:
        user = User.query.get(session['user_id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'age': user.age,
            'gender': user.gender,
            'created_at': user.created_at.isoformat(),
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/symptoms-list', methods=['GET'])
def get_symptoms_list():
    """
    Get list of symptom categories
    """
    try:
        symptoms = disease_predictor.get_symptom_checklist()
        return jsonify(symptoms), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/health/analyze-metrics', methods=['POST'])
def analyze_health_metrics():
    """
    Analyze health metrics with AI
    Expected JSON: {
        'metrics': {
            'heart_rate': '72 bpm',
            'blood_pressure': '120/80 mmHg',
            'weight': '70 kg'
        }
    }
    """
    try:
        data = request.get_json()
        metrics = data.get('metrics', {})
        
        analysis = ai_engine.analyze_health_metrics(metrics)
        
        return jsonify({
            'analysis': analysis,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
