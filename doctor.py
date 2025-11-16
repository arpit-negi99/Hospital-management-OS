"""Doctor Module"""
from datetime import datetime

class Doctor:
    def __init__(self, doctor_id, name, specialization="General"):
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization
