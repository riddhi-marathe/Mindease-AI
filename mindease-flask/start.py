#!/usr/bin/env python
"""
Quick Start Script for MindEase
This script helps you quickly start and test the MindEase application
"""

import os
import sys
import subprocess

def print_header():
    print("\n" + "="*60)
    print(" MindEase - AI Health & Wellness Platform - Quick Start")
    print("="*60 + "\n")

def check_environment():
    """Check if the environment is set up correctly"""
    print("📋 Checking environment setup...")
    
    # Check if venv exists
    if not os.path.exists('venv'):
        print("  ❌ Virtual environment not found!")
        print("  Please run: python -m venv venv")
        return False
    
    print("  ✓ Virtual environment found")
    
    # Check if requirements are installed
    requirements_file = 'requirements.txt'
    if not os.path.exists(requirements_file):
        print(f"  ❌ {requirements_file} not found!")
        return False
    
    print("  ✓ Requirements file found")
    
    # Check if database exists
    if not os.path.exists('instance/mindease.db'):
        print("  ⚠️  Database not found. Initializing...")
        init_database()
    else:
        print("  ✓ Database found")
    
    return True

def init_database():
    """Initialize the database"""
    print("\n  Initializing database...")
    try:
        from app import create_app, db
        app = create_app()
        app.app_context().push()
        db.create_all()
        print("  ✓ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"  ❌ Database initialization failed: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required settings"""
    print("\n🔐 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("  ⚠️  .env file not found")
        print("  Creating default .env file...")
        with open('.env', 'w') as f:
            f.write("""FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_change_in_production
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///mindease.db
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
""")
        print("  ✓ .env file created. Please update GEMINI_API_KEY")
        print("  📝 Get your free API key from: https://makersuite.google.com/app/apikey")
    else:
        print("  ✓ .env file found")
        
        # Check for API key
        with open('.env', 'r') as f:
            content = f.read()
            if 'your_gemini_api_key_here' in content or 'GEMINI_API_KEY=' not in content:
                print("  ⚠️  GEMINI_API_KEY not configured")
                print("  📝 Please update .env file with your API key")

def start_server():
    """Start the Flask development server"""
    print("\n🚀 Starting MindEase server...")
    print("  Server starting at http://localhost:5000")
    print("  Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, 'run.py'], cwd=os.path.dirname(os.path.abspath(__file__)))
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped gracefully")
        sys.exit(0)

def main():
    print_header()
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed!")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    
    # Check .env configuration
    check_env_file()
    
    # Start server
    print("\n" + "="*60)
    start_server()

if __name__ == '__main__':
    main()
