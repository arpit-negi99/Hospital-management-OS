#include <stdio.h>
#include <stdlib.h>
#include "ipc_interface.h"

#define MAX_LINE_LENGTH 256

void export_patient_data_for_ml(Patient* patients, int count, const char* filename) {
    FILE* file = fopen(filename, "w");
    if (file == NULL) {
        perror("Could not open IPC file for writing");
        return;
    }
    // In a real scenario, you'd export features. For now, we export IDs.
    fprintf(file, "patient_id,arrival_time\n");
    for (int i = 0; i < count; i++) {
        fprintf(file, "%d,%d\n", patients[i].patient_id, patients[i].arrival_time);
    }
    fclose(file);
    printf("\n[C] Exported %d patient records to %s for ML analysis.\n", count, filename);
}

// NEW FUNCTION
void import_ml_predictions(Patient* patients, int count, const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        perror("[C] Error: Could not open IPC input file from ML script");
        return;
    }
    
    char line[MAX_LINE_LENGTH];
    // Skip header
    if (fgets(line, sizeof(line), file) == NULL) {
        fclose(file);
        return;
    }

    int patient_id, burst_time, priority;
    while (fgets(line, sizeof(line), file)) {
        sscanf(line, "%d,%d,%d", &patient_id, &burst_time, &priority);
        
        // Find the matching patient and update their data
        for (int i = 0; i < count; i++) {
            if (patients[i].patient_id == patient_id) {
                patients[i].burst_time = burst_time;
                patients[i].priority = priority;
                break;
            }
        }
    }
    fclose(file);
    printf("[C] Imported ML predictions from %s and updated patient data.\n", filename);
}