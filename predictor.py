"""Health Predictor Module - ML-based Priority Prediction"""
import joblib
import os

class HealthPredictor:
    def __init__(self):
        self.risk_model = None
        self.label_encoder = None
        self.models_loaded = False
        self.priority_mapping = {0: "CRITICAL", 1: "HIGH", 2: "MEDIUM", 3: "LOW"}

    def load_models(self):
        try:
            if os.path.exists("risk_model.joblib"):
                self.risk_model = joblib.load("risk_model.joblib")
                self.label_encoder = joblib.load("label_encoder.joblib")
                self.models_loaded = True
                return True
        except:
            pass
        return False

    def predict(self, patient_data):
        """Predict priority and burst time"""
        score = 0
        try:
            o2_sat = float(patient_data.get('oxygenSat', 95))
            if o2_sat < 85: score += 10
            elif o2_sat < 95: score += 5
            else: score += 2

            hr = float(patient_data.get('heartRate', 75))
            if hr > 130: score += 7
            elif hr > 110: score += 4
            else: score += 1

            temp = float(patient_data.get('temperature', patient_data.get('tempF', 98.6)))
            if temp > 100: score += 5
            elif temp > 99: score += 3
            else: score += 1

            bp = float(patient_data.get('systolicBP', 120))
            if bp > 150 or bp < 90: score += 5

            rr = float(patient_data.get('respRate', 18))
            if rr > 30: score += 5
            elif rr > 24: score += 3
        except (ValueError, TypeError):
            score = 1

        if score >= 20:
            priority, risk_label, burst_time = 0, "CRITICAL", 20
        elif score >= 10:
            priority, risk_label, burst_time = 1, "HIGH", 15
        elif score >= 5:
            priority, risk_label, burst_time = 2, "MEDIUM", 10
        else:
            priority, risk_label, burst_time = 3, "LOW", 5

        return priority, burst_time, risk_label
