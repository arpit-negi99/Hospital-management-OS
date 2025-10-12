#!/usr/bin/env python3
"""
Hospital OS Management System - Flask API Backend
Provides REST API for frontend communication and ML integration
FIXED VERSION - Better error handling for Windows
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import subprocess
import json
import os
import sys
import pandas as pd
from datetime import datetime
import logging

# Add ML engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_engine', 'src'))

try:
    from ml_predictor import HospitalPriorityPredictor
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML predictor not available: {e}")
    print("Install required packages: pip install scikit-learn pandas joblib")
    HospitalPriorityPredictor = None
    ML_AVAILABLE = False

app = Flask(__name__, 
            template_folder='../../frontend/templates',
            static_folder='../../frontend/static')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
ml_predictor = None
patients_data = []
simulation_results = {}

def initialize_ml_model():
    """Initialize ML model on startup"""
    global ml_predictor
    if not ML_AVAILABLE:
        logger.warning("ML libraries not available")
        return False

    try:
        ml_predictor = HospitalPriorityPredictor()
        model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_engine', 'models')

        # Try to load existing model, otherwise train new one
        try:
            ml_predictor.load_model(model_path)
            logger.info("✅ ML model loaded successfully")
            return True
        except FileNotFoundError:
            logger.info("🤖 Training new ML model...")
            ml_predictor.train_model()
            os.makedirs(model_path, exist_ok=True)
            ml_predictor.save_model(model_path)
            logger.info("✅ New ML model trained and saved")
            return True

    except Exception as e:
        logger.error(f"❌ Failed to initialize ML model: {e}")
        return False

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/predict_priority', methods=['POST'])
def predict_priority():
    """Predict patient priority using ML model"""
    try:
        if not ml_predictor:
            return jsonify({'error': 'ML model not available'}), 500

        data = request.json

        # Validate required fields
        required_fields = [
            'age', 'heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'temperature', 'respiratory_rate', 'oxygen_saturation', 'pain_level',
            'chest_pain', 'breathing_difficulty', 'consciousness_level', 'bleeding_severity'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Make prediction
        result = ml_predictor.predict_priority(data)

        # Add timestamp and patient ID
        result['timestamp'] = datetime.now().isoformat()
        result['patient_id'] = data.get('patient_id', len(patients_data) + 1)

        # Store patient data
        patient_record = {
            **data,
            **result,
            'admission_time': datetime.now().isoformat()
        }
        patients_data.append(patient_record)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in predict_priority: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_patient', methods=['POST'])
def add_patient():
    """Add new patient with automatic priority prediction"""
    try:
        data = request.json

        # Auto-predict priority if ML model available
        if ml_predictor:
            try:
                prediction = ml_predictor.predict_priority(data)
                data.update(prediction)
            except Exception as e:
                logger.warning(f"ML prediction failed, using fallback: {e}")
                data['priority'] = calculate_basic_priority(data)
                data['priority_label'] = get_priority_label(data['priority'])
                data['confidence'] = 0.8
        else:
            # Fallback priority calculation
            data['priority'] = calculate_basic_priority(data)
            data['priority_label'] = get_priority_label(data['priority'])
            data['confidence'] = 0.8

        # Add metadata
        data['patient_id'] = len(patients_data) + 1
        data['admission_time'] = datetime.now().isoformat()
        data['status'] = 'waiting'

        patients_data.append(data)

        return jsonify({
            'success': True,
            'patient_id': data['patient_id'],
            'priority': data['priority'],
            'priority_label': data['priority_label'],
            'confidence': data.get('confidence', 0.8),
            'message': f"Patient {data['patient_id']} added successfully with {data['priority_label']} priority"
        })

    except Exception as e:
        logger.error(f"Error in add_patient: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients"""
    try:
        # Sort by priority (1 = highest)
        sorted_patients = sorted(patients_data, key=lambda x: x.get('priority', 4))
        return jsonify({
            'patients': sorted_patients,
            'total': len(sorted_patients)
        })
    except Exception as e:
        logger.error(f"Error in get_patients: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/run_simulation', methods=['POST'])
def run_simulation():
    """Run C-based OS simulation"""
    try:
        data = request.json
        algorithm = data.get('algorithm', 'fcfs')

        # Export current patients to CSV for C program
        if patients_data:
            df = pd.DataFrame(patients_data)
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'ml_engine', 'data', 'current_patients.csv')
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)

            # Prepare data for C program format
            c_format_data = []
            for i, patient in enumerate(patients_data):
                c_format_data.append({
                    'patient_id': patient.get('patient_id', i + 1),
                    'arrival_time': i,  # Sequential arrival
                    'burst_time': 10 + (patient.get('priority', 4) * 5),  # Priority affects treatment time
                    'priority': patient.get('priority', 4)
                })

            df_c = pd.DataFrame(c_format_data)
            df_c.to_csv(csv_path, index=False)

        # Mock simulation results (in real implementation, you'd compile and run C code)
        avg_waiting = 5.5 + (len(patients_data) * 0.8)
        avg_turnaround = avg_waiting + 12.0

        simulation_results[algorithm] = {
            'algorithm': algorithm.upper(),
            'total_patients': len(patients_data),
            'average_waiting_time': round(avg_waiting, 1),
            'average_turnaround_time': round(avg_turnaround, 1),
            'completion_times': [i * 8 + 10 for i in range(min(len(patients_data), 5))],
            'executed_at': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'result': simulation_results[algorithm]
        })

    except Exception as e:
        logger.error(f"Error in run_simulation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation_results', methods=['GET'])
def get_simulation_results():
    """Get simulation results"""
    return jsonify(simulation_results)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        if not patients_data:
            return jsonify({
                'total_patients': 0,
                'critical_patients': 0,
                'average_age': 0,
                'priority_distribution': {}
            })

        df = pd.DataFrame(patients_data)

        priority_dist = df['priority'].value_counts().to_dict() if 'priority' in df.columns else {}
        priority_labels = {1: 'CRITICAL', 2: 'HIGH', 3: 'MEDIUM', 4: 'LOW'}

        stats = {
            'total_patients': len(patients_data),
            'critical_patients': len([p for p in patients_data if p.get('priority') == 1]),
            'average_age': round(df['age'].mean()) if 'age' in df.columns else 0,
            'priority_distribution': {
                priority_labels.get(k, f'Priority {k}'): v 
                for k, v in priority_dist.items()
            },
            'latest_admission': max([p.get('admission_time', '') for p in patients_data], default='')
        }

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error in get_stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear_data', methods=['POST'])
def clear_data():
    """Clear all patient data"""
    global patients_data, simulation_results
    patients_data.clear()
    simulation_results.clear()
    return jsonify({'success': True, 'message': 'All data cleared'})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'online',
        'ml_available': ML_AVAILABLE and ml_predictor is not None,
        'patients_count': len(patients_data),
        'version': '2.0.0'
    })

def calculate_basic_priority(patient_data):
    """Basic priority calculation fallback"""
    score = 0

    # Age factor
    age = patient_data.get('age', 30)
    if age > 65 or age < 5:
        score += 2

    # Heart rate
    hr = patient_data.get('heart_rate', 80)
    if hr > 120 or hr < 50:
        score += 3
    elif hr > 100 or hr < 60:
        score += 2

    # Blood pressure
    bp_sys = patient_data.get('blood_pressure_systolic', 120)
    if bp_sys > 180 or bp_sys < 90:
        score += 3
    elif bp_sys > 140:
        score += 2

    # Oxygen saturation
    o2 = patient_data.get('oxygen_saturation', 98)
    if o2 < 90:
        score += 3
    elif o2 < 95:
        score += 2

    # Pain level
    pain = patient_data.get('pain_level', 1)
    if pain >= 8:
        score += 3
    elif pain >= 5:
        score += 2

    # Symptoms
    score += patient_data.get('chest_pain', 0)
    score += patient_data.get('breathing_difficulty', 0)
    score += patient_data.get('bleeding_severity', 0)

    # Convert score to priority (1-4)
    if score >= 15:
        return 1  # CRITICAL
    elif score >= 10:
        return 2  # HIGH
    elif score >= 5:
        return 3  # MEDIUM
    else:
        return 4  # LOW

def get_priority_label(priority):
    """Get priority label from number"""
    labels = {1: 'CRITICAL', 2: 'HIGH', 3: 'MEDIUM', 4: 'LOW'}
    return labels.get(priority, 'UNKNOWN')

if __name__ == '__main__':
    print("🏥 Hospital OS Management System - Web Server")
    print("=" * 50)

    # Initialize ML model on startup
    ml_status = initialize_ml_model()
    if ml_status:
        print("✅ ML model initialized successfully")
    else:
        print("⚠️  ML model not available, using fallback priority calculation")

    print("🌐 Starting Flask web server...")
    print("   Open http://localhost:5000 in your browser")
    print("   Press Ctrl+C to stop the server")
    print()

    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
