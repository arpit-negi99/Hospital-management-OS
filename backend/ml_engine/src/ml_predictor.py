#!/usr/bin/env python3
"""
Hospital Priority Prediction ML Engine
Predicts patient priority based on vital signs and symptoms
FIXED VERSION - Handles missing directories properly
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys
import json

class HospitalPriorityPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_columns = [
            'age', 'heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'temperature', 'respiratory_rate', 'oxygen_saturation', 'pain_level',
            'chest_pain', 'breathing_difficulty', 'consciousness_level', 'bleeding_severity'
        ]

    def generate_training_data(self, n_samples=2000):
        """Generate synthetic training data based on medical knowledge"""
        np.random.seed(42)

        data = []

        for _ in range(n_samples):
            # Generate base vital signs
            age = np.random.randint(1, 90)

            # Generate correlated vital signs
            if np.random.random() < 0.2:  # 20% critical cases
                priority = 1  # CRITICAL
                heart_rate = np.random.normal(120, 20)  # Elevated
                bp_sys = np.random.normal(160, 30)      # High
                bp_dia = np.random.normal(100, 20)      # High
                temperature = np.random.normal(39, 1.5)  # Fever
                resp_rate = np.random.randint(25, 40)   # Elevated
                o2_sat = np.random.randint(80, 95)      # Low
                pain_level = np.random.randint(7, 11)   # High pain
                chest_pain = np.random.randint(3, 6)    # High
                breathing_diff = np.random.randint(3, 6) # High
                consciousness = np.random.randint(1, 4)  # Low consciousness
                bleeding = np.random.randint(2, 6)       # Moderate to severe

            elif np.random.random() < 0.5:  # 30% high priority
                priority = 2  # HIGH
                heart_rate = np.random.normal(100, 15)
                bp_sys = np.random.normal(140, 25)
                bp_dia = np.random.normal(90, 15)
                temperature = np.random.normal(38, 1)
                resp_rate = np.random.randint(20, 30)
                o2_sat = np.random.randint(92, 98)
                pain_level = np.random.randint(5, 8)
                chest_pain = np.random.randint(2, 5)
                breathing_diff = np.random.randint(2, 4)
                consciousness = np.random.randint(3, 5)
                bleeding = np.random.randint(1, 4)

            elif np.random.random() < 0.7:  # 20% medium priority
                priority = 3  # MEDIUM
                heart_rate = np.random.normal(80, 10)
                bp_sys = np.random.normal(125, 15)
                bp_dia = np.random.normal(80, 10)
                temperature = np.random.normal(37, 0.5)
                resp_rate = np.random.randint(16, 24)
                o2_sat = np.random.randint(95, 100)
                pain_level = np.random.randint(3, 6)
                chest_pain = np.random.randint(1, 3)
                breathing_diff = np.random.randint(1, 3)
                consciousness = np.random.randint(4, 6)
                bleeding = np.random.randint(0, 2)

            else:  # 30% low priority
                priority = 4  # LOW
                heart_rate = np.random.normal(72, 8)
                bp_sys = np.random.normal(115, 10)
                bp_dia = np.random.normal(75, 8)
                temperature = np.random.normal(36.8, 0.3)
                resp_rate = np.random.randint(14, 20)
                o2_sat = np.random.randint(97, 101)
                pain_level = np.random.randint(1, 4)
                chest_pain = np.random.randint(0, 2)
                breathing_diff = np.random.randint(0, 2)
                consciousness = np.random.randint(5, 6)
                bleeding = np.random.randint(0, 1)

            # Ensure realistic bounds
            heart_rate = max(40, min(200, heart_rate))
            bp_sys = max(80, min(220, bp_sys))
            bp_dia = max(40, min(140, bp_dia))
            temperature = max(35, min(42, temperature))
            o2_sat = max(70, min(100, o2_sat))

            data.append([
                age, heart_rate, bp_sys, bp_dia, temperature, resp_rate,
                o2_sat, pain_level, chest_pain, breathing_diff, consciousness, bleeding, priority
            ])

        columns = self.feature_columns + ['priority']
        return pd.DataFrame(data, columns=columns)

    def train_model(self, df=None):
        """Train the priority prediction model"""
        if df is None:
            df = self.generate_training_data()

        X = df[self.feature_columns]
        y = df['priority']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"Model Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                   target_names=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']))

        return accuracy

    def predict_priority(self, patient_data):
        """Predict priority for a single patient"""
        if isinstance(patient_data, dict):
            # Convert dict to list in correct order
            features = [patient_data[col] for col in self.feature_columns]
        else:
            features = patient_data

        features_scaled = self.scaler.transform([features])
        priority = self.model.predict(features_scaled)[0]
        probability = self.model.predict_proba(features_scaled)[0]

        priority_labels = {1: 'CRITICAL', 2: 'HIGH', 3: 'MEDIUM', 4: 'LOW'}

        return {
            'priority': int(priority),
            'priority_label': priority_labels[priority],
            'confidence': float(max(probability))
        }

    def save_model(self, model_dir='models'):
        """Save trained model and scaler"""
        os.makedirs(model_dir, exist_ok=True)
        joblib.dump(self.model, os.path.join(model_dir, 'priority_model.pkl'))
        joblib.dump(self.scaler, os.path.join(model_dir, 'scaler.pkl'))

        # Save feature columns
        with open(os.path.join(model_dir, 'feature_columns.json'), 'w') as f:
            json.dump(self.feature_columns, f)

        print(f"✅ Model saved to {model_dir}/")

    def load_model(self, model_dir='models'):
        """Load trained model and scaler"""
        self.model = joblib.load(os.path.join(model_dir, 'priority_model.pkl'))
        self.scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))

        with open(os.path.join(model_dir, 'feature_columns.json'), 'r') as f:
            self.feature_columns = json.load(f)

        print(f"✅ Model loaded from {model_dir}/")

def main():
    """Main function for CLI usage"""
    predictor = HospitalPriorityPredictor()

    if len(sys.argv) > 1 and sys.argv[1] == 'train':
        print("🤖 Training new ML model...")
        accuracy = predictor.train_model()
        predictor.save_model()
        print(f"✅ Model trained and saved with accuracy: {accuracy:.4f}")

        # Create data directory if it doesn't exist
        data_dir = '../data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"✅ Created data directory: {data_dir}")

        # Generate and save sample data with absolute path
        print("📊 Generating sample patient data...")
        sample_data = predictor.generate_training_data(100)
        data_file = os.path.join(data_dir, 'sample_patients.csv')
        sample_data.to_csv(data_file, index=False)
        print(f"✅ Sample patient data saved to {data_file}")

        # Also create sample data in current directory for immediate use
        sample_data.to_csv('sample_patients.csv', index=False)
        print("✅ Sample data also saved in current directory")

    elif len(sys.argv) > 1 and sys.argv[1] == 'predict':
        print("🔮 Testing prediction...")
        try:
            predictor.load_model()

            # Example prediction
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

            result = predictor.predict_priority(sample_patient)
            print(f"\n🏥 Prediction Results:")
            print(f"   Priority: {result['priority']} ({result['priority_label']})")
            print(f"   Confidence: {result['confidence']:.1%}")

        except FileNotFoundError:
            print("❌ Model not found. Please train the model first using: python ml_predictor.py train")

    else:
        print("🏥 Hospital Priority Prediction ML Engine")
        print("=" * 40)
        print("Usage:")
        print("  python ml_predictor.py train    - Train and save new model")
        print("  python ml_predictor.py predict  - Test prediction with sample data")
        print()
        print("The ML model uses 12 medical parameters to predict patient priority:")
        print("• Demographics: Age")
        print("• Vital Signs: Heart Rate, Blood Pressure, Temperature, Respiratory Rate, O2 Saturation")
        print("• Assessment: Pain Level, Chest Pain, Breathing Difficulty, Consciousness, Bleeding")
        print()
        print("Output: Priority (1=Critical, 2=High, 3=Medium, 4=Low) with confidence score")

if __name__ == "__main__":
    main()
