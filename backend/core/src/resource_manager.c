#include <stdio.h>
#include "resources.h"

// Definition of global resource arrays
int available[NUM_RESOURCES];
int max_demand[NUM_PATIENTS][NUM_RESOURCES];
int allocated[NUM_PATIENTS][NUM_RESOURCES];
int need[NUM_PATIENTS][NUM_RESOURCES];

void initialize_resources() {
    // Total available resources in the hospital
    // e.g., {10 Ventilators, 5 Beds, 7 Monitors}
    int total_available[NUM_RESOURCES] = {10, 5, 7};
    for(int i = 0; i < NUM_RESOURCES; i++) {
        available[i] = total_available[i];
    }

    // Maximum resource needs for each patient
    int max_matrix[NUM_PATIENTS][NUM_RESOURCES] = {
        {7, 5, 3},
        {3, 2, 2},
        {9, 0, 2},
        {2, 2, 2},
        {4, 3, 3}
    };
    for(int i=0; i < NUM_PATIENTS; i++) {
        for(int j=0; j < NUM_RESOURCES; j++) {
            max_demand[i][j] = max_matrix[i][j];
        }
    }

    // Initially, no resources are allocated
    for (int i = 0; i < NUM_PATIENTS; i++) {
        for (int j = 0; j < NUM_RESOURCES; j++) {
            allocated[i][j] = 0;
        }
    }
    
    // Calculate the initial 'need' matrix (Need = Max - Allocation)
    for (int i = 0; i < NUM_PATIENTS; i++) {
        for (int j = 0; j < NUM_RESOURCES; j++) {
            need[i][j] = max_demand[i][j] - allocated[i][j];
        }
    }
    printf("Resource manager initialized.\n");
}