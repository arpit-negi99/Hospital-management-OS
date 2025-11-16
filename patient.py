"""Patient Module"""
class Patient:
    def __init__(self, patient_id, name, respiratory_rate, oxygen_saturation, o2_scale, systolic_bp, heart_rate, temperature, consciousness, on_oxygen):
        self.patient_id = patient_id
        self.name = name
        self.respiratory_rate = respiratory_rate
        self.oxygen_saturation = oxygen_saturation
        self.o2_scale = o2_scale
        self.systolic_bp = systolic_bp
        self.heart_rate = heart_rate
        self.temperature = temperature
        self.consciousness = consciousness
        self.on_oxygen = on_oxygen
        self.priority = None
        self.burst_time = None
        self.arrival_time = None
        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.status = 'WAITING'
