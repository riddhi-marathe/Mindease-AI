from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()

def create_app():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_path = os.path.join(project_root, 'templates')
    static_path = os.path.join(project_root, 'static')

    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=templates_path,
        static_folder=static_path,
        static_url_path='/static'
    )
    
    # Ensure the instance folder exists and use an absolute DB path if needed.
    os.makedirs(app.instance_path, exist_ok=True)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        database_url = f"sqlite:///{os.path.join(app.instance_path, 'mindease.db')}"
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize Extensions
    db.init_app(app)
    CORS(app)
    
    # Register Blueprint
    from .main import main_bp
    app.register_blueprint(main_bp)
    
    # Create Database Tables
    with app.app_context():
        db.create_all()
    
    return app
