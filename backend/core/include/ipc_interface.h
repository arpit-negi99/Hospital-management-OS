#ifndef IPC_INTERFACE_H
#define IPC_INTERFACE_H

#include "patient.h"

/**
 * @brief Exports patient data to a CSV file for inter-process communication.
 * @param patients The array of patients.
 * @param count The number of patients.
 * @param filename The name of the output file.
 */
void export_patient_data_for_ml(Patient* patients, int count, const char* filename);

// Imports ML predictions and updates the patient data array
void import_ml_predictions(Patient* patients, int count, const char* filename);

#endif // IPC_INTERFACE_H