#ifndef PATIENT_H
#define PATIENT_H

#include <time.h>

// Enhanced patient structure with ML features
typedef struct {
    int patient_id;
    int arrival_time;
    int burst_time;
    int priority;

    // ML-driven health parameters
    int age;
    int heart_rate;
    float blood_pressure_systolic;
    float blood_pressure_diastolic;
    float temperature;
    int respiratory_rate;
    int oxygen_saturation;
    int pain_level;  // 1-10 scale

    // Symptom severity (1-5 scale)
    int chest_pain;
    int breathing_difficulty;
    int consciousness_level;
    int bleeding_severity;

    // System fields
    int remaining_burst_time;
    int current_queue;
    int completion_time;
    int waiting_time;
    int turnaround_time;

    // ML prediction
    float predicted_priority;
    char emergency_level[20];  // "CRITICAL", "HIGH", "MEDIUM", "LOW"

    // Timestamps
    time_t admission_time;
    time_t treatment_start_time;
    time_t treatment_end_time;
} Patient;

// Function declarations
Patient* load_patients_from_csv(const char* filename, int* patient_count);
void print_patient_info(Patient p);
Patient create_patient_from_input(int id, int age, int heart_rate, float bp_sys, float bp_dia, 
                                 float temp, int resp_rate, int o2_sat, int pain, 
                                 int chest_pain, int breathing_diff, int consciousness, int bleeding);
void export_patient_for_ml(Patient* patients, int count, const char* filename);

#endif // PATIENT_H