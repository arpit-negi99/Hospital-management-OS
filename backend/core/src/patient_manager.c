#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include "patient.h"

#define MAX_LINE_LENGTH 512

// Enhanced patient loading with ML features
Patient* load_patients_from_csv(const char* filename, int* patient_count) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        printf("⚠️  Warning: Could not open %s. Using default data.\n", filename);
        return NULL;
    }

    Patient* patients = NULL;
    char line[MAX_LINE_LENGTH];
    int capacity = 10;
    int count = 0;

    patients = malloc(capacity * sizeof(Patient));
    if (patients == NULL) {
        perror("Initial memory allocation failed");
        fclose(file);
        return NULL;
    }

    // Skip the header line
    if (fgets(line, sizeof(line), file) == NULL) {
        fclose(file);
        free(patients);
        return NULL;
    }

    // Read each patient line with ML features
    while (fgets(line, sizeof(line), file)) {
        if (count >= capacity) {
            capacity *= 2;
            Patient* temp = realloc(patients, capacity * sizeof(Patient));
            if (temp == NULL) {
                perror("Memory reallocation failed");
                free(patients);
                fclose(file);
                return NULL;
            }
            patients = temp;
        }

        // Parse enhanced patient data
        int parsed = sscanf(line, "%d,%d,%d,%d,%d,%d,%f,%f,%f,%d,%d,%d,%d,%d,%d,%d,%f,%19s",
            &patients[count].patient_id,
            &patients[count].arrival_time,
            &patients[count].burst_time,
            &patients[count].priority,
            &patients[count].age,
            &patients[count].heart_rate,
            &patients[count].blood_pressure_systolic,
            &patients[count].blood_pressure_diastolic,
            &patients[count].temperature,
            &patients[count].respiratory_rate,
            &patients[count].oxygen_saturation,
            &patients[count].pain_level,
            &patients[count].chest_pain,
            &patients[count].breathing_difficulty,
            &patients[count].consciousness_level,
            &patients[count].bleeding_severity,
            &patients[count].predicted_priority,
            patients[count].emergency_level);

        if (parsed >= 4) {  // At minimum, we need basic fields
            // Initialize remaining fields if not provided
            if (parsed < 8) {
                patients[count].age = 30 + (rand() % 50);
                patients[count].heart_rate = 70 + (rand() % 30);
                patients[count].blood_pressure_systolic = 120.0 + (rand() % 40);
                patients[count].blood_pressure_diastolic = 80.0 + (rand() % 20);
                patients[count].temperature = 36.5 + ((float)(rand() % 20) / 10.0);
                patients[count].respiratory_rate = 16 + (rand() % 8);
                patients[count].oxygen_saturation = 95 + (rand() % 6);
                patients[count].pain_level = 1 + (rand() % 5);
                patients[count].chest_pain = rand() % 3;
                patients[count].breathing_difficulty = rand() % 3;
                patients[count].consciousness_level = 4 + (rand() % 2);
                patients[count].bleeding_severity = rand() % 2;
                patients[count].predicted_priority = (float)patients[count].priority;
                strcpy(patients[count].emergency_level, "MEDIUM");
            }

            // Initialize system fields
            patients[count].remaining_burst_time = patients[count].burst_time;
            patients[count].current_queue = 0;
            patients[count].completion_time = 0;
            patients[count].waiting_time = 0;
            patients[count].turnaround_time = 0;
            patients[count].admission_time = time(NULL);
            patients[count].treatment_start_time = 0;
            patients[count].treatment_end_time = 0;

            count++;
        }
    }

    fclose(file);
    *patient_count = count;
    return patients;
}

// Create patient from input parameters
Patient create_patient_from_input(int id, int age, int heart_rate, float bp_sys, float bp_dia, 
                                 float temp, int resp_rate, int o2_sat, int pain, 
                                 int chest_pain, int breathing_diff, int consciousness, int bleeding) {
    Patient p;

    p.patient_id = id;
    p.age = age;
    p.heart_rate = heart_rate;
    p.blood_pressure_systolic = bp_sys;
    p.blood_pressure_diastolic = bp_dia;
    p.temperature = temp;
    p.respiratory_rate = resp_rate;
    p.oxygen_saturation = o2_sat;
    p.pain_level = pain;
    p.chest_pain = chest_pain;
    p.breathing_difficulty = breathing_diff;
    p.consciousness_level = consciousness;
    p.bleeding_severity = bleeding;

    // Calculate basic priority based on vital signs
    int priority_score = 0;

    // Heart rate scoring
    if (heart_rate > 120 || heart_rate < 50) priority_score += 3;
    else if (heart_rate > 100 || heart_rate < 60) priority_score += 2;
    else priority_score += 1;

    // Blood pressure scoring
    if (bp_sys > 180 || bp_sys < 90) priority_score += 3;
    else if (bp_sys > 140 || bp_sys < 100) priority_score += 2;
    else priority_score += 1;

    // Oxygen saturation scoring
    if (o2_sat < 90) priority_score += 3;
    else if (o2_sat < 95) priority_score += 2;
    else priority_score += 1;

    // Pain level scoring
    if (pain >= 8) priority_score += 3;
    else if (pain >= 5) priority_score += 2;
    else priority_score += 1;

    // Symptom scoring
    priority_score += chest_pain;
    priority_score += breathing_diff;
    priority_score += (6 - consciousness);
    priority_score += bleeding;

    // Determine priority (1 = highest, 4 = lowest)
    if (priority_score >= 20) {
        p.priority = 1;
        strcpy(p.emergency_level, "CRITICAL");
    } else if (priority_score >= 15) {
        p.priority = 2;
        strcpy(p.emergency_level, "HIGH");
    } else if (priority_score >= 10) {
        p.priority = 3;
        strcpy(p.emergency_level, "MEDIUM");
    } else {
        p.priority = 4;
        strcpy(p.emergency_level, "LOW");
    }

    p.predicted_priority = (float)p.priority;
    p.arrival_time = 0;
    p.burst_time = 10 + (p.priority * 5);  // More severe = longer treatment
    p.remaining_burst_time = p.burst_time;
    p.current_queue = 0;
    p.completion_time = 0;
    p.waiting_time = 0;
    p.turnaround_time = 0;
    p.admission_time = time(NULL);
    p.treatment_start_time = 0;
    p.treatment_end_time = 0;

    return p;
}

// Enhanced patient info display
void print_patient_info(Patient p) {
    printf("\n=== Patient Information ===\n");
    printf("ID: %d\n", p.patient_id);
    printf("Age: %d years\n", p.age);
    printf("Priority: %d (%s)\n", p.priority, p.emergency_level);
    printf("\nVital Signs:\n");
    printf("  Heart Rate: %d bpm\n", p.heart_rate);
    printf("  Blood Pressure: %.1f/%.1f mmHg\n", p.blood_pressure_systolic, p.blood_pressure_diastolic);
    printf("  Temperature: %.1f°C\n", p.temperature);
    printf("  Respiratory Rate: %d /min\n", p.respiratory_rate);
    printf("  Oxygen Saturation: %d%%\n", p.oxygen_saturation);
    printf("  Pain Level: %d/10\n", p.pain_level);
    printf("\nSymptoms:\n");
    printf("  Chest Pain: %d/5\n", p.chest_pain);
    printf("  Breathing Difficulty: %d/5\n", p.breathing_difficulty);
    printf("  Consciousness Level: %d/5\n", p.consciousness_level);
    printf("  Bleeding Severity: %d/5\n", p.bleeding_severity);
    printf("\nScheduling Info:\n");
    printf("  Arrival Time: %d\n", p.arrival_time);
    printf("  Burst Time: %d\n", p.burst_time);
    printf("  Waiting Time: %d\n", p.waiting_time);
    printf("========================\n");
}

// Export patient data for ML processing
void export_patient_for_ml(Patient* patients, int count, const char* filename) {
    FILE* file = fopen(filename, "w");
    if (!file) {
        perror("Error creating ML export file");
        return;
    }

    // Write header
    fprintf(file, "patient_id,age,heart_rate,blood_pressure_systolic,blood_pressure_diastolic,");
    fprintf(file, "temperature,respiratory_rate,oxygen_saturation,pain_level,chest_pain,");
    fprintf(file, "breathing_difficulty,consciousness_level,bleeding_severity,priority,emergency_level\n");

    // Write patient data
    for (int i = 0; i < count; i++) {
        fprintf(file, "%d,%d,%d,%.1f,%.1f,%.1f,%d,%d,%d,%d,%d,%d,%d,%d,%s\n",
            patients[i].patient_id,
            patients[i].age,
            patients[i].heart_rate,
            patients[i].blood_pressure_systolic,
            patients[i].blood_pressure_diastolic,
            patients[i].temperature,
            patients[i].respiratory_rate,
            patients[i].oxygen_saturation,
            patients[i].pain_level,
            patients[i].chest_pain,
            patients[i].breathing_difficulty,
            patients[i].consciousness_level,
            patients[i].bleeding_severity,
            patients[i].priority,
            patients[i].emergency_level);
    }

    fclose(file);
    printf("✅ Patient data exported to %s for ML processing\n", filename);
}
