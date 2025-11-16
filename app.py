#!/usr/bin/env python3
"""Hospital OS - v10 with Fixed Resource Deallocation"""

from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
import traceback
from patient import Patient
from predictor import HealthPredictor
from scheduler import MultiDoctorScheduler
from resource_manager import ResourceManager
from process_sync import ProcessSynchronization

app = Flask(__name__, template_folder='templates', static_folder='static')

scheduler = None
resource_manager = None
predictor = None
sync_manager = None
patient_counter = 0

VALID_RANGES = {
    'heartRate': (40, 200),
    'oxygenSat': (70, 100),
    'tempF': (95, 106),
    'systolicBP': (60, 200),
    'respRate': (8, 40)
}

def get_priority_label(priority_num):
    """Convert priority number to label"""
    priority_map = {0: "CRITICAL", 1: "HIGH", 2: "MEDIUM", 3: "LOW"}
    return priority_map.get(priority_num, "LOW")

def initialize_system():
    """Initialize system"""
    global scheduler, resource_manager, predictor, sync_manager
    print("🏥 Initializing Hospital OS System...")
    try:
        print(" → Loading HealthPredictor...")
        predictor = HealthPredictor()
        predictor.load_models()
        print(" ✓ HealthPredictor loaded")
        print(" → Creating MultiDoctorScheduler...")
        scheduler = MultiDoctorScheduler(num_doctors=3, algorithm='priority')
        print(" ✓ MultiDoctorScheduler created")
        print(" → Creating ResourceManager...")
        resource_manager = ResourceManager(num_beds=10, num_operation_rooms=3, num_ventilators=5, num_monitors=10)
        print(" ✓ ResourceManager created")
        print(" → Creating ProcessSynchronization...")
        sync_manager = ProcessSynchronization(num_doctors=3)
        print(" ✓ ProcessSynchronization created")
        print("✓ System initialized successfully!")
        return True
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        traceback.print_exc()
        return False

def validate_input(data):
    """Validate patient input"""
    errors = []
    try:
        hr = float(data.get('heartRate', 72))
        if hr < VALID_RANGES['heartRate'][0] or hr > VALID_RANGES['heartRate'][1]:
            errors.append(f"Heart Rate must be {VALID_RANGES['heartRate'][0]}-{VALID_RANGES['heartRate'][1]} bpm")
    except (ValueError, TypeError):
        errors.append("Invalid Heart Rate")

    try:
        o2 = float(data.get('oxygenSat', 95))
        if o2 < VALID_RANGES['oxygenSat'][0] or o2 > VALID_RANGES['oxygenSat'][1]:
            errors.append(f"O2 Saturation must be {VALID_RANGES['oxygenSat'][0]}-{VALID_RANGES['oxygenSat'][1]}%")
    except (ValueError, TypeError):
        errors.append("Invalid O2 Saturation")

    try:
        temp = float(data.get('tempF', 98.6))
        if temp < VALID_RANGES['tempF'][0] or temp > VALID_RANGES['tempF'][1]:
            errors.append(f"Temperature must be {VALID_RANGES['tempF'][0]}-{VALID_RANGES['tempF'][1]}°F")
    except (ValueError, TypeError):
        errors.append("Invalid Temperature")

    try:
        bp = float(data.get('systolicBP', 120))
        if bp < VALID_RANGES['systolicBP'][0] or bp > VALID_RANGES['systolicBP'][1]:
            errors.append(f"Systolic BP must be {VALID_RANGES['systolicBP'][0]}-{VALID_RANGES['systolicBP'][1]} mmHg")
    except (ValueError, TypeError):
        errors.append("Invalid Systolic BP")

    try:
        rr = float(data.get('respRate', 18))
        if rr < VALID_RANGES['respRate'][0] or rr > VALID_RANGES['respRate'][1]:
            errors.append(f"Respiratory Rate must be {VALID_RANGES['respRate'][0]}-{VALID_RANGES['respRate'][1]}")
    except (ValueError, TypeError):
        errors.append("Invalid Respiratory Rate")

    return errors

@app.route('/', methods=['GET'])
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/doctor/<int:doctor_num>', methods=['GET'])
def doctor_dashboard(doctor_num):
    try:
        if doctor_num not in [1, 2, 3]:
            return "Invalid doctor", 404
        return render_template('doctor_dashboard.html', doctor_num=doctor_num)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/api/register-patient', methods=['POST'])
def register_patient():
    global patient_counter, scheduler, predictor
    try:
        data = request.json
        errors = validate_input(data)
        if errors:
            return jsonify({'success': False, 'error': ' | '.join(errors)})

        doctor_choice = data.get('doctorChoice')
        if not doctor_choice or doctor_choice not in ['1', '2', '3']:
            return jsonify({'success': False, 'error': 'Select a doctor'})

        doctor_num = int(doctor_choice) - 1
        patient_counter += 1

        patient = Patient(
            patient_id=f"P{patient_counter:03d}",
            name=data['name'],
            respiratory_rate=float(data['respRate']),
            oxygen_saturation=float(data['oxygenSat']),
            o2_scale=int(data.get('o2Scale', 1)),
            systolic_bp=float(data['systolicBP']),
            heart_rate=float(data['heartRate']),
            temperature=float(data['tempF']),
            consciousness=data.get('consciousness', 'A'),
            on_oxygen=0
        )

        priority, burst_time, risk_label = predictor.predict(data)
        patient.priority = priority
        patient.burst_time = burst_time
        patient.arrival_time = datetime.now()

        scheduler.doctors[doctor_num].add_patient(patient)

        return jsonify({
            'success': True,
            'patient': {
                'id': patient.patient_id,
                'name': patient.name,
                'priority': risk_label,
                'priority_num': priority,
                'burst_time': burst_time,
                'assigned_doctor': scheduler.doctors[doctor_num].doctor_id,
                'assigned_doctor_num': doctor_num + 1
            }
        })
    except Exception as e:
        print(f"Register error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    try:
        scheduler.update_all_doctors()
        all_doctors = scheduler.get_all_doctors_status()

        for doctor_status in all_doctors:
            if doctor_status['current_patient']:
                doctor_status['current_patient']['priority_label'] = get_priority_label(doctor_status['current_patient']['priority'])

            for patient in doctor_status['waiting_queue']:
                patient['priority_label'] = get_priority_label(patient['priority'])

        return jsonify({
            'success': True,
            'doctors': all_doctors,
            'overall_stats': scheduler.get_overall_statistics()
        })
    except Exception as e:
        print(f"Schedule error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/demo', methods=['GET'])
def load_demo():
    global patient_counter, scheduler, predictor
    try:
        demo_patients = [
            {'name': 'John Doe', 'heartRate': '145', 'oxygenSat': '82', 'tempF': '101.5', 'systolicBP': '155', 'respRate': '32', 'o2Scale': '2', 'consciousness': 'P', 'doctorChoice': '1'},
            {'name': 'Jane Smith', 'heartRate': '98', 'oxygenSat': '94', 'tempF': '99.2', 'systolicBP': '128', 'respRate': '22', 'o2Scale': '1', 'consciousness': 'A', 'doctorChoice': '2'},
            {'name': 'Bob Johnson', 'heartRate': '72', 'oxygenSat': '98', 'tempF': '98.6', 'systolicBP': '118', 'respRate': '16', 'o2Scale': '0', 'consciousness': 'A', 'doctorChoice': '3'},
            {'name': 'Alice Brown', 'heartRate': '115', 'oxygenSat': '88', 'tempF': '100.8', 'systolicBP': '142', 'respRate': '28', 'o2Scale': '1', 'consciousness': 'V', 'doctorChoice': '1'},
            {'name': 'Charlie Davis', 'heartRate': '155', 'oxygenSat': '78', 'tempF': '102.5', 'systolicBP': '165', 'respRate': '35', 'o2Scale': '2', 'consciousness': 'P', 'doctorChoice': '2'},
            {'name': 'Diana Wilson', 'heartRate': '88', 'oxygenSat': '96', 'tempF': '98.8', 'systolicBP': '122', 'respRate': '18', 'o2Scale': '0', 'consciousness': 'A', 'doctorChoice': '3'}
        ]

        for data in demo_patients:
            patient_counter += 1
            doctor_idx = int(data['doctorChoice']) - 1

            patient = Patient(
                patient_id=f"P{patient_counter:03d}",
                name=data['name'],
                respiratory_rate=float(data['respRate']),
                oxygen_saturation=float(data['oxygenSat']),
                o2_scale=int(data['o2Scale']),
                systolic_bp=float(data['systolicBP']),
                heart_rate=float(data['heartRate']),
                temperature=float(data['tempF']),
                consciousness=data['consciousness'],
                on_oxygen=0
            )

            priority, burst_time, risk_label = predictor.predict(data)
            patient.priority = priority
            patient.burst_time = burst_time
            patient.arrival_time = datetime.now()

            scheduler.doctors[doctor_idx].add_patient(patient)

        return jsonify({'success': True})
    except Exception as e:
        print(f"Demo error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reset', methods=['POST'])
def reset_system():
    global patient_counter
    try:
        patient_counter = 0
        scheduler.reset_all()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resources/status', methods=['GET'])
def get_resources_status():
    """Get all resources status - Synchronized"""
    try:
        if not resource_manager:
            return jsonify({'success': False, 'error': 'Resource manager not initialized'})

        status = resource_manager.get_status()
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resources/allocate-bed', methods=['POST'])
def allocate_bed():
    """Allocate bed to patient"""
    try:
        data = request.json
        patient_id = data.get('patient_id')
        doctor_id = data.get('doctor_id')
        notes = data.get('notes', '')

        success, msg, bed_id = resource_manager.allocate_bed(patient_id, doctor_id, notes)

        return jsonify({
            'success': success,
            'message': msg,
            'bed_id': bed_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resources/deallocate-bed', methods=['POST'])
def deallocate_bed():
    """Deallocate bed - FIXED"""
    try:
        data = request.json
        bed_id = data.get('bed_id')
        doctor_id = data.get('doctor_id')

        if not bed_id:
            return jsonify({'success': False, 'error': 'Bed ID is required'})

        success, msg, patient_id = resource_manager.deallocate_bed(bed_id, doctor_id)

        return jsonify({
            'success': success,
            'message': msg,
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resources/allocate-or', methods=['POST'])
def allocate_operation_room():
    """Allocate operation room"""
    try:
        data = request.json
        patient_id = data.get('patient_id')
        doctor_id = data.get('doctor_id')
        notes = data.get('notes', '')

        success, msg, or_id = resource_manager.allocate_operation_room(patient_id, doctor_id, notes)

        return jsonify({
            'success': success,
            'message': msg,
            'or_id': or_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resources/deallocate-or', methods=['POST'])
def deallocate_operation_room():
    """Deallocate operation room - FIXED"""
    try:
        data = request.json
        or_id = data.get('or_id')
        doctor_id = data.get('doctor_id')

        if not or_id:
            return jsonify({'success': False, 'error': 'Operation Room ID is required'})

        success, msg, patient_id = resource_manager.deallocate_operation_room(or_id, doctor_id)

        return jsonify({
            'success': success,
            'message': msg,
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resources/allocate-ventilator', methods=['POST'])
def allocate_ventilator():
    """Allocate ventilator"""
    try:
        data = request.json
        patient_id = data.get('patient_id')
        doctor_id = data.get('doctor_id')

        success, msg, vent_id = resource_manager.allocate_ventilator(patient_id, doctor_id)

        return jsonify({
            'success': success,
            'message': msg,
            'ventilator_id': vent_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resources/deallocate-ventilator', methods=['POST'])
def deallocate_ventilator():
    """Deallocate ventilator - FIXED"""
    try:
        data = request.json
        vent_id = data.get('ventilator_id')
        doctor_id = data.get('doctor_id')

        if not vent_id:
            return jsonify({'success': False, 'error': 'Ventilator ID is required'})

        success, msg, patient_id = resource_manager.deallocate_ventilator(vent_id, doctor_id)

        return jsonify({
            'success': success,
            'message': msg,
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resources/allocate-monitor', methods=['POST'])
def allocate_monitor():
    """Allocate monitor"""
    try:
        data = request.json
        patient_id = data.get('patient_id')
        doctor_id = data.get('doctor_id')

        success, msg, mon_id = resource_manager.allocate_monitor(patient_id, doctor_id)

        return jsonify({
            'success': success,
            'message': msg,
            'monitor_id': mon_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resources/deallocate-monitor', methods=['POST'])
def deallocate_monitor():
    """Deallocate monitor - FIXED"""
    try:
        data = request.json
        mon_id = data.get('monitor_id')
        doctor_id = data.get('doctor_id')

        if not mon_id:
            return jsonify({'success': False, 'error': 'Monitor ID is required'})

        success, msg, patient_id = resource_manager.deallocate_monitor(mon_id, doctor_id)

        return jsonify({
            'success': success,
            'message': msg,
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/patient/<patient_id>/resources', methods=['GET'])
def get_patient_resources(patient_id):
    """Get all resources allocated to a patient"""
    try:
        resources = resource_manager.get_patient_resources(patient_id)
        return jsonify({'success': True, 'resources': resources})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    print("=" * 70)
    print("🏥 HOSPITAL OS - v10 WITH FIXED RESOURCE DEALLOCATION")
    print("=" * 70)

    if not initialize_system():
        print("ERROR: Failed to initialize")
        exit(1)

    print("Server starting...")
    print(" Main: http://127.0.0.1:5000/")
    print("=" * 70)

    app.run(host='127.0.0.1', port=5000, debug=True)
