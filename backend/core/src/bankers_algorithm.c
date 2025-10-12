#include <stdio.h>
#include "resources.h"

// Safety Algorithm
bool is_safe_state() {
    int work[NUM_RESOURCES];
    for (int i = 0; i < NUM_RESOURCES; i++) {
        work[i] = available[i];
    }

    bool finish[NUM_PATIENTS] = {0};
    int safe_sequence[NUM_PATIENTS];
    int count = 0;

    while (count < NUM_PATIENTS) {
        bool found = false;
        for (int p = 0; p < NUM_PATIENTS; p++) {
            if (!finish[p]) {
                int j;
                for (j = 0; j < NUM_RESOURCES; j++) {
                    if (need[p][j] > work[j])
                        break;
                }
                if (j == NUM_RESOURCES) {
                    for (int k = 0; k < NUM_RESOURCES; k++) {
                        work[k] += allocated[p][k];
                    }
                    safe_sequence[count++] = p;
                    finish[p] = true;
                    found = true;
                }
            }
        }
        if (!found) {
            printf("System is in an unsafe state!\n");
            return false;
        }
    }

    printf("System is in a safe state. Safe sequence: ");
    for (int i = 0; i < NUM_PATIENTS; i++) {
        printf("P%d ", safe_sequence[i]);
    }
    printf("\n");
    return true;
}

// Resource-Request Algorithm
bool request_resources(int patient_id, int request[]) {
    printf("Patient P%d requests resources: {%d, %d, %d}\n", patient_id, request[0], request[1], request[2]);

    for (int i = 0; i < NUM_RESOURCES; i++) {
        if (request[i] > need[patient_id][i]) {
            printf("Error: Patient has exceeded its maximum claim.\n");
            return false;
        }
        if (request[i] > available[i]) {
            // This line has been fixed to include patient_id
            printf("Patient P%d must wait. Resources not available.\n", patient_id);
            return false;
        }
    }

    // Tentatively allocate resources
    for (int i = 0; i < NUM_RESOURCES; i++) {
        available[i] -= request[i];
        allocated[patient_id][i] += request[i];
        need[patient_id][i] -= request[i];
    }

    // Check for safety
    if (is_safe_state()) {
        printf("Request granted. Resources allocated to P%d.\n", patient_id);
        return true;
    } else {
        // Roll back if unsafe
        printf("Request denied as it leads to an unsafe state. Rolling back.\n");
        for (int i = 0; i < NUM_RESOURCES; i++) {
            available[i] += request[i];
            allocated[patient_id][i] -= request[i];
            need[patient_id][i] += request[i];
        }
        return false;
    }
}

void run_bankers_demo() {
    printf("\n--- Banker's Algorithm Demonstration ---\n");
    initialize_resources();
    is_safe_state();

    int request1[] = {1, 0, 2};
    request_resources(1, request1);

    int request2[] = {3, 0, 2};
    request_resources(0, request2);
    
    int request3[] = {0, 2, 0};
    request_resources(1, request3);
}