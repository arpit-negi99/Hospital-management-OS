#ifndef RESOURCES_H
#define RESOURCES_H

#include <stdbool.h>

#define NUM_PATIENTS 5
#define NUM_RESOURCES 3

// --- Global Resource Arrays ---
// Available amount of each resource
extern int available[NUM_RESOURCES];
// Maximum demand of each patient
extern int max_demand[NUM_PATIENTS][NUM_RESOURCES];
// Amount currently allocated to each patient
extern int allocated[NUM_PATIENTS][NUM_RESOURCES];
// Remaining need of each patient
extern int need[NUM_PATIENTS][NUM_RESOURCES];

// --- Function Declarations ---
// Initializes all resource management arrays
void initialize_resources();

// Checks if a resource request leads to a safe state
bool is_safe_state();

// Handles a resource request from a patient
bool request_resources(int patient_id, int request[]);

// Runs a demonstration of the Banker's Algorithm
void run_bankers_demo();

#endif // RESOURCES_H