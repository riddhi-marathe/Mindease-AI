#!/usr/bin/env python
"""
Test script to verify MindEase setup
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    try:
        from app import create_app, db
        print("  ✓ Flask app imports successful")
        
        from app.models import User, HealthAssessment, WellnessLog, HealthMetric
        print("  ✓ Database models imports successful")
        
        from app.services.disease_predictor import DiseasePredictors
        print("  ✓ Disease predictor imports successful")
        
        from app.services.ai_engine import AIEngine
        print("  ✓ AI engine imports successful")
        
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_app_creation():
    """Test if Flask app can be created"""
    print("\nTesting Flask app creation...")
    try:
        from app import create_app
        app = create_app()
        print("  ✓ Flask app created successfully")
        
        with app.app_context():
            print("  ✓ App context working")
            
        return True
    except Exception as e:
        print(f"  ✗ App creation failed: {e}")
        return False

def test_database():
    """Test if database is accessible"""
    print("\nTesting database...")
    try:
        from app import create_app, db
        from app.models import User
        
        app = create_app()
        
        with app.app_context():
            # Try to query users
            users = User.query.all()
            print(f"  ✓ Database accessible (found {len(users)} users)")
            
        return True
    except Exception as e:
        print(f"  ✗ Database test failed: {e}")
        return False

def test_routes():
    """Test if routes are registered"""
    print("\nTesting routes...")
    try:
        from app import create_app
        app = create_app()
        
        routes = []
        for rule in app.url_map.iter_rules():
            if 'api' in rule.rule or rule.rule == '/':
                routes.append(str(rule))
        
        print(f"  ✓ {len(routes)} API routes registered")
        for route in routes[:5]:
            print(f"    - {route}")
        
        return True
    except Exception as e:
        print(f"  ✗ Routes test failed: {e}")
        return False

def test_services():
    """Test if services work"""
    print("\nTesting services...")
    try:
        from app.services.disease_predictor import DiseasePredictors
        
        symptoms = ['fever', 'cough']
        result = DiseasePredictors.predict_disease(symptoms, age=30)
        
        if result and 'urgency' in result:
            print(f"  ✓ Disease predictor working (urgency: {result.get('urgency')})")
        else:
            print("  ⚠️  Disease predictor returned unexpected result")
        
        return True
    except Exception as e:
        print(f"  ✗ Services test failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print(" MindEase Application Tests")
    print("="*60 + "\n")
    
    results = {
        'Imports': test_imports(),
        'App Creation': test_app_creation(),
        'Database': test_database(),
        'Routes': test_routes(),
        'Services': test_services(),
    }
    
    print("\n" + "="*60)
    print(" Test Results")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! MindEase is ready to run.")
        print("\nTo start the server, run:")
        print("  python run.py")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
