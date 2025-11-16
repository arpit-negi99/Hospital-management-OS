"""Scheduler Module with Priority Support"""
import copy
from datetime import datetime

class Doctor:
    def __init__(self, doctor_id, name, specialization="General"):
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization
        self.patients_queue = []
        self.current_patient = None
        self.patient_start_time = None
        self.completed_patients = []
        self.total_patients_treated = 0

    def add_patient(self, patient):
        patient.assigned_doctor = self.doctor_id
        patient.arrival_time = datetime.now()
        self.patients_queue.append(patient)
        self._sort_queue()

    def _sort_queue(self):
        self.patients_queue.sort(key=lambda p: (p.priority if isinstance(p.priority, int) else 999, p.arrival_time.timestamp() if isinstance(p.arrival_time, datetime) else 0))

    def get_priority_label(self, priority_num):
        priority_map = {0: "CRITICAL", 1: "HIGH", 2: "MEDIUM", 3: "LOW"}
        return priority_map.get(priority_num, "LOW")

    def get_current_patient_info(self):
        if self.current_patient is None:
            return None
        elapsed = (datetime.now() - self.patient_start_time).total_seconds()
        total_time = self.current_patient.burst_time * 60
        remaining = max(0, total_time - elapsed)
        return {'patient': self.current_patient, 'elapsed_seconds': elapsed, 'total_seconds': total_time, 'remaining_seconds': remaining, 'is_complete': remaining <= 0}

    def update_treatment(self):
        if self.current_patient is not None:
            info = self.get_current_patient_info()
            if info['is_complete']:
                self.current_patient.start_time = self.patient_start_time
                self.current_patient.completion_time = datetime.now()
                self.current_patient.status = 'COMPLETED'
                arrival_timestamp = self.current_patient.arrival_time.timestamp()
                start_timestamp = self.patient_start_time.timestamp()
                self.current_patient.waiting_time = max(0, start_timestamp - arrival_timestamp)
                self.completed_patients.append(copy.copy(self.current_patient))
                self.total_patients_treated += 1
                self.current_patient = None
                self.patient_start_time = None

        if self.current_patient is None and len(self.patients_queue) > 0:
            self._sort_queue()
            self.current_patient = self.patients_queue.pop(0)
            self.current_patient.status = 'IN_TREATMENT'
            self.patient_start_time = datetime.now()

    def get_status(self):
        self.update_treatment()
        current_info = None
        if self.current_patient is not None:
            info = self.get_current_patient_info()
            current_info = {'id': self.current_patient.patient_id, 'name': self.current_patient.name, 'priority': self.current_patient.priority, 'priority_label': self.get_priority_label(self.current_patient.priority), 'burst_time': self.current_patient.burst_time, 'remaining_seconds': int(info['remaining_seconds']), 'remaining_minutes': round(info['remaining_seconds'] / 60, 1)}

        waiting_queue = []
        cumulative_wait = 0
        if self.current_patient is not None:
            info = self.get_current_patient_info()
            cumulative_wait = info['remaining_seconds']

        for idx, patient in enumerate(self.patients_queue):
            wait_time_seconds = cumulative_wait
            waiting_queue.append({'id': patient.patient_id, 'name': patient.name, 'priority': patient.priority, 'priority_label': self.get_priority_label(patient.priority), 'burst_time': patient.burst_time, 'queue_position': idx + 1, 'wait_time_seconds': int(wait_time_seconds), 'wait_time_minutes': round(wait_time_seconds / 60, 1)})
            cumulative_wait += patient.burst_time * 60

        return {'doctor_id': self.doctor_id, 'doctor_name': self.name, 'specialization': self.specialization, 'current_patient': current_info, 'waiting_queue': waiting_queue, 'queue_size': len(self.patients_queue), 'total_treated': self.total_patients_treated, 'is_available': self.current_patient is None}

class MultiDoctorScheduler:
    def __init__(self, num_doctors=3, algorithm='priority'):
        self.num_doctors = num_doctors
        self.algorithm = algorithm
        self.doctors = []
        for i in range(num_doctors):
            doctor_id = f"DOC{i+1:02d}"
            doctor_names = ["Dr. Sarah Johnson", "Dr. Michael Chen", "Dr. Emily Rodriguez"]
            specializations = ["Emergency Medicine", "Internal Medicine", "Surgery"]
            doc = Doctor(doctor_id, doctor_names[i], specializations[i])
            self.doctors.append(doc)

    def update_all_doctors(self):
        for doctor in self.doctors:
            doctor.update_treatment()

    def get_all_doctors_status(self):
        return [doctor.get_status() for doctor in self.doctors]

    def get_overall_statistics(self):
        total_in_system = sum(len(doc.patients_queue) + (1 if doc.current_patient else 0) for doc in self.doctors)
        total_waiting = sum(len(doc.patients_queue) for doc in self.doctors)
        total_treating = sum(1 for doc in self.doctors if doc.current_patient)
        total_completed = sum(len(doc.completed_patients) for doc in self.doctors)
        return {'total_in_system': total_in_system, 'total_waiting': total_waiting, 'total_treating': total_treating, 'total_completed': total_completed}

    def reset_all(self):
        for doctor in self.doctors:
            doctor.patients_queue = []
            doctor.current_patient = None
            doctor.completed_patients = []
            doctor.total_patients_treated = 0
