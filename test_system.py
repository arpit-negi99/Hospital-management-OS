#!/usr/bin/env python3
"""
Quick test script to verify ML model installation
"""

import sys
import os

def test_imports():
    print("🧪 Testing Python package imports...")

    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas failed: {e}")
        return False

    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy failed: {e}")
        return False

    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        print("✅ scikit-learn imported successfully")
    except ImportError as e:
        print(f"❌ scikit-learn failed: {e}")
        return False

    try:
        import joblib
        print("✅ joblib imported successfully")
    except ImportError as e:
        print(f"❌ joblib failed: {e}")
        return False

    try:
        import flask
        from flask_cors import CORS
        print("✅ Flask and Flask-CORS imported successfully")
    except ImportError as e:
        print(f"❌ Flask failed: {e}")
        return False

    return True

def test_directories():
    print("\n📁 Testing directory structure...")

    required_dirs = [
        'backend/ml_engine/data',
        'backend/ml_engine/models',
        'backend/ml_engine/src',
        'backend/core/src',
        'backend/core/include',
        'backend/api',
        'frontend/templates',
        'frontend/static/css',
        'frontend/static/js'
    ]

    all_good = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory} - MISSING")
            all_good = False

    return all_good

def test_ml_model():
    print("\n🤖 Testing ML model...")

    try:
        sys.path.append('backend/ml_engine/src')
        from ml_predictor import HospitalPriorityPredictor

        predictor = HospitalPriorityPredictor()
        print("✅ ML predictor class loaded")

        # Test with sample data
        sample_patient = {
            'age': 45,
            'heart_rate': 110,
            'blood_pressure_systolic': 150,
            'blood_pressure_diastolic': 95,
            'temperature': 38.5,
            'respiratory_rate': 22,
            'oxygen_saturation': 94,
            'pain_level': 7,
            'chest_pain': 4,
            'breathing_difficulty': 3,
            'consciousness_level': 4,
            'bleeding_severity': 1
        }

        # Try to load existing model or train new one
        model_dir = 'backend/ml_engine/models'
        try:
            predictor.load_model(model_dir)
            print("✅ Existing ML model loaded")
        except FileNotFoundError:
            print("🔄 Training new ML model...")
            predictor.train_model()
            os.makedirs(model_dir, exist_ok=True)
            predictor.save_model(model_dir)
            print("✅ New ML model trained and saved")

        # Test prediction
        result = predictor.predict_priority(sample_patient)
        print(f"✅ ML prediction successful: {result['priority_label']} (confidence: {result['confidence']:.1%})")

        return True

    except Exception as e:
        print(f"❌ ML model test failed: {e}")
        return False

def main():
    print("🏥 Hospital OS Management System - System Test")
    print("=" * 50)

    imports_ok = test_imports()
    dirs_ok = test_directories()
    ml_ok = test_ml_model()

    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("=" * 50)

    if imports_ok:
        print("✅ Python packages: OK")
    else:
        print("❌ Python packages: FAILED")
        print("   Run: pip install flask flask-cors pandas scikit-learn joblib numpy matplotlib")

    if dirs_ok:
        print("✅ Directory structure: OK")
    else:
        print("❌ Directory structure: INCOMPLETE")
        print("   Run setup.bat to create missing directories")

    if ml_ok:
        print("✅ ML model: OK")
    else:
        print("❌ ML model: FAILED")
        print("   Check Python packages and run setup.bat")

    if imports_ok and dirs_ok and ml_ok:
        print("\n🎉 All tests passed! System ready to use.")
        print("\nNext steps:")
        print("1. Run: python backend/api/app.py")
        print("2. Open: http://localhost:5000")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")

    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
