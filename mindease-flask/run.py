#!/usr/bin/env python
"""
MindEase Flask Application Entry Point
"""

import os
import sys
from dotenv import load_dotenv

# Ensure the project root is on sys.path when run from outside the project folder.
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Create shell context for flask shell"""
    return {"db": db}


@app.before_request
def before_request():
    """Before request hook"""
    pass


@app.after_request
def after_request(response):
    """After request hook"""
    response.headers["X-UA-Compatible"] = "IE=edge"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response


@app.context_processor
def inject_globals():
    """Inject global variables to templates"""
    return {
        "app_name": "MindEase",
    }


if __name__ == "__main__":
    # Create database directory if it doesn't exist
    os.makedirs("instance", exist_ok=True)

    # Run the Flask application
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "False").lower() == "true",
    )
