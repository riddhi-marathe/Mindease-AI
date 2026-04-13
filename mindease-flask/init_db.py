#!/usr/bin/env python
"""
Database initialization script for MindEase
Run this script to initialize the database with sample data
"""

import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, HealthAssessment, WellnessLog, HealthMetric


def init_database():
    """Initialize database with tables"""
    print("Initializing database...")

    app = create_app()

    with app.app_context():
        # Drop all tables (only for development)
        # db.drop_all()

        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully")

        # Add sample user (optional)
        try:
            sample_user = User.query.filter_by(username="demo").first()
            if not sample_user:
                sample_user = User(
                    username="demo",
                    email="demo@mindease.ai",
                    password_hash=generate_password_hash("demo123"),
                    age=30,
                    gender="Male",
                )
                db.session.add(sample_user)
                db.session.commit()
                print("✓ Sample user created (username: demo, password: demo123)")
            else:
                print("✓ Sample user already exists")
        except Exception as e:
            print(f"! Note: Could not create sample user: {e}")
            db.session.rollback()

        print("\n✓ Database initialization complete!")
        print(
            "\nDatabase location:",
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), "instance", "mindease.db")
            ),
        )


if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)
