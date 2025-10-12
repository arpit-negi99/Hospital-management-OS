#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

// Include all headers
#include "patient.h"
#include "scheduler.h"
#include "resources.h"
#include "ipc_interface.h"
#include "logger.h"

void print_welcome_banner() {
    printf("\n");
    printf("╔══════════════════════════════════════════════════════════════╗\n");
    printf("║                                                              ║\n");
    printf("║        🏥 Hospital OS Management System Enhanced 🏥         ║\n");
    printf("║                                                              ║\n");
    printf("║  Features:                                                   ║\n");
    printf("║  • ML-based Priority Prediction                              ║\n");
    printf("║  • Multiple Scheduling Algorithms                           ║\n");
    printf("║  • Web-based Frontend Interface                              ║\n");
    printf("║  • Real-time Patient Queue Management                       ║\n");
    printf("║  • Resource Management with Banker's Algorithm              ║\n");
    printf("║                                                              ║\n");
    printf("║  Version 2.0 - Windows Compatible                           ║\n");
    printf("╚══════════════════════════════════════════════════════════════╝\n");
    printf("\n");
}

Patient* create_default_patients(int* count) {
    printf("📝 Creating default patient data...\n");

    Patient* patients = malloc(5 * sizeof(Patient));
    if (!patients) return NULL;

    // Critical case
    patients[0] = create_patient_from_input(1, 70, 150, 190, 110, 39.8, 32, 85, 9, 5, 5, 2, 4);
    patients[0].arrival_time = 0;

    // High priority
    patients[1] = create_patient_from_input(2, 50, 115, 155, 95, 38.2, 26, 91, 8, 4, 3, 3, 2);
    patients[1].arrival_time = 2;

    // Medium priority  
    patients[2] = create_patient_from_input(3, 40, 95, 135, 88, 37.5, 22, 95, 6, 2, 2, 4, 1);
    patients[2].arrival_time = 4;

    // Low priority
    patients[3] = create_patient_from_input(4, 25, 78, 118, 78, 36.9, 18, 97, 4, 1, 1, 5, 0);
    patients[3].arrival_time = 6;

    patients[4] = create_patient_from_input(5, 35, 82, 125, 82, 37.1, 19, 96, 3, 1, 0, 5, 0);
    patients[4].arrival_time = 8;

    *count = 5;
    return patients;
}

void run_interactive_mode() {
    printf("\n=== Interactive Patient Management ===\n");

    char choice;
    Patient patients[100];
    int patient_count = 0;

    while (1) {
        printf("\n--- Options ---\n");
        printf("1. Add new patient manually\n");
        printf("2. Display all patients\n");
        printf("3. Run scheduling simulation\n");
        printf("4. Export data for ML\n");
        printf("5. Load sample data\n");
        printf("6. Web interface info\n");
        printf("q. Quit\n");
        printf("Enter your choice: ");

        scanf(" %c", &choice);

        switch (choice) {
            case '1': {
                if (patient_count >= 100) {
                    printf("Maximum patients reached!\n");
                    break;
                }

                int age, hr, resp_rate, o2_sat, pain, chest_pain, breathing_diff, consciousness, bleeding;
                float bp_sys, bp_dia, temp;

                printf("\n--- Enter Patient Information ---\n");
                printf("Age: ");
                scanf("%d", &age);
                printf("Heart Rate (bpm): ");
                scanf("%d", &hr);
                printf("Blood Pressure Systolic (mmHg): ");
                scanf("%f", &bp_sys);
                printf("Blood Pressure Diastolic (mmHg): ");
                scanf("%f", &bp_dia);
                printf("Temperature (°C): ");
                scanf("%f", &temp);
                printf("Respiratory Rate (/min): ");
                scanf("%d", &resp_rate);
                printf("Oxygen Saturation (%%): ");
                scanf("%d", &o2_sat);
                printf("Pain Level (1-10): ");
                scanf("%d", &pain);
                printf("Chest Pain (0-5): ");
                scanf("%d", &chest_pain);
                printf("Breathing Difficulty (0-5): ");
                scanf("%d", &breathing_diff);
                printf("Consciousness Level (1-5): ");
                scanf("%d", &consciousness);
                printf("Bleeding Severity (0-5): ");
                scanf("%d", &bleeding);

                patients[patient_count] = create_patient_from_input(
                    patient_count + 1, age, hr, bp_sys, bp_dia, temp,
                    resp_rate, o2_sat, pain, chest_pain, breathing_diff, consciousness, bleeding
                );

                patients[patient_count].arrival_time = patient_count;

                printf("\n✅ Patient %d added successfully!\n", patients[patient_count].patient_id);
                print_patient_info(patients[patient_count]);

                patient_count++;
                break;
            }

            case '2': {
                if (patient_count == 0) {
                    printf("No patients in system.\n");
                    break;
                }

                printf("\n=== All Patients ===\n");
                for (int i = 0; i < patient_count; i++) {
                    printf("\n--- Patient %d ---\n", i + 1);
                    print_patient_info(patients[i]);
                }
                break;
            }

            case '3': {
                if (patient_count == 0) {
                    printf("No patients to simulate. Add some patients first.\n");
                    break;
                }

                printf("\nSelect scheduling algorithm:\n");
                printf("1. FCFS\n");
                printf("2. Priority\n");
                printf("3. Round Robin\n");
                printf("4. MLFQ\n");
                printf("Enter choice (1-4): ");

                int alg_choice;
                scanf("%d", &alg_choice);

                // Create copies for simulation
                Patient* sim_patients = malloc(patient_count * sizeof(Patient));
                memcpy(sim_patients, patients, patient_count * sizeof(Patient));

                switch (alg_choice) {
                    case 1:
                        printf("\n🔄 Running FCFS Simulation...\n");
                        schedule_fcfs(sim_patients, patient_count);
                        break;
                    case 2:
                        printf("\n🔄 Running Priority Scheduling Simulation...\n");
                        schedule_priority(sim_patients, patient_count);
                        break;
                    case 3:
                        printf("\n🔄 Running Round Robin Simulation...\n");
                        schedule_round_robin(sim_patients, patient_count, 4);
                        break;
                    case 4:
                        printf("\n🔄 Running MLFQ Simulation...\n");
                        schedule_mlfq(sim_patients, patient_count);
                        break;
                    default:
                        printf("Invalid choice!\n");
                }

                free(sim_patients);
                break;
            }

            case '4': {
                if (patient_count == 0) {
                    printf("No patients to export.\n");
                    break;
                }

                export_patient_for_ml(patients, patient_count, "exported_patients.csv");
                break;
            }

            case '5': {
                printf("\n🔄 Loading sample patient data...\n");

                Patient* sample_patients = create_default_patients(&patient_count);
                if (sample_patients) {
                    memcpy(patients, sample_patients, patient_count * sizeof(Patient));
                    free(sample_patients);
                    printf("✅ Loaded %d sample patients\n", patient_count);
                } else {
                    printf("❌ Failed to create sample patients\n");
                }
                break;
            }

            case '6': {
                printf("\n🌐 Web Interface Information:\n");
                printf("===============================\n");
                printf("To use the web interface:\n");
                printf("1. Navigate to the backend\\api\\ directory\n");
                printf("2. Install Python dependencies (if not done):\n");
                printf("   pip install flask flask-cors pandas scikit-learn joblib\n");
                printf("3. Run the Flask server:\n");
                printf("   python app.py\n");
                printf("4. Open your browser to: http://localhost:5000\n");
                printf("\nThe web interface provides:\n");
                printf("• Interactive patient admission form\n");
                printf("• Real-time ML-based priority prediction\n");
                printf("• Patient queue visualization\n");
                printf("• OS scheduling simulation dashboard\n");
                printf("• Statistical charts and analytics\n");
                break;
            }

            case 'q':
            case 'Q':
                printf("\n👋 Thank you for using Hospital OS Management System!\n");
                return;

            default:
                printf("Invalid choice! Please try again.\n");
        }
    }
}

int main(int argc, char* argv[]) {
    // Print welcome banner
    print_welcome_banner();

    // Initialize logging
    log_init("hospital_system.log");
    log_event("Enhanced Hospital OS Management System starting up");

    // Check command line arguments
    if (argc > 1) {
        if (strcmp(argv[1], "--demo") == 0) {
            printf("🚀 Running demonstration mode...\n\n");

            // Try to load patient data, fallback to default if not found
            int patient_count = 0;
            Patient* patients = NULL;

            // Try different possible data file locations
            const char* data_files[] = {
                "../../ml_engine/data/patients_for_c.csv",
                "../../../backend/ml_engine/data/patients_for_c.csv",
                "patients_for_c.csv",
                "sample_patients.csv",
                NULL
            };

            for (int i = 0; data_files[i] != NULL; i++) {
                patients = load_patients_from_csv(data_files[i], &patient_count);
                if (patients && patient_count > 0) {
                    printf("✅ Loaded %d patients from %s\n", patient_count, data_files[i]);
                    break;
                }
            }

            // If no CSV file found, create default patients
            if (!patients || patient_count == 0) {
                printf("📝 Using default patient data...\n");
                patients = create_default_patients(&patient_count);
            }

            if (patient_count > 0) {
                log_event("Running demonstration with sample patient data");

                // Display patient information
                printf("\n👥 Patient List:\n");
                printf("================\n");
                for (int i = 0; i < patient_count; i++) {
                    printf("Patient %d: %s priority\n", 
                           patients[i].patient_id, patients[i].emergency_level);
                }

                // Run all scheduling algorithms
                printf("\n🔄 Running all scheduling algorithms...\n");

                // FCFS
                Patient* fcfs_patients = malloc(patient_count * sizeof(Patient));
                memcpy(fcfs_patients, patients, patient_count * sizeof(Patient));
                printf("\n--- First Come First Served (FCFS) ---\n");
                schedule_fcfs(fcfs_patients, patient_count);
                free(fcfs_patients);

                // Priority
                Patient* priority_patients = malloc(patient_count * sizeof(Patient));
                memcpy(priority_patients, patients, patient_count * sizeof(Patient));
                printf("\n--- Priority Scheduling ---\n");
                schedule_priority(priority_patients, patient_count);
                free(priority_patients);

                // Round Robin
                Patient* rr_patients = malloc(patient_count * sizeof(Patient));
                memcpy(rr_patients, patients, patient_count * sizeof(Patient));
                printf("\n--- Round Robin (Time Quantum = 4) ---\n");
                schedule_round_robin(rr_patients, patient_count, 4);
                free(rr_patients);

                // MLFQ
                Patient* mlfq_patients = malloc(patient_count * sizeof(Patient));
                memcpy(mlfq_patients, patients, patient_count * sizeof(Patient));
                printf("\n--- Multi-Level Feedback Queue ---\n");
                schedule_mlfq(mlfq_patients, patient_count);
                free(mlfq_patients);

                // Banker's Algorithm demo
                printf("\n--- Resource Management (Banker's Algorithm) ---\n");
                run_bankers_demo();

                // Export for ML
                printf("\n--- Exporting Data for ML Processing ---\n");
                export_patient_for_ml(patients, patient_count, "demo_export.csv");

                free(patients);
            }

        } else if (strcmp(argv[1], "--help") == 0) {
            printf("Hospital OS Management System - Usage:\n");
            printf("======================================\n");
            printf("./hospital_system           - Interactive mode\n");
            printf("./hospital_system --demo    - Run demonstration\n");
            printf("./hospital_system --help    - Show this help\n");
            printf("\nWeb Interface:\n");
            printf("cd backend/api && python app.py\n");
            printf("Then open http://localhost:5000 in your browser\n");

        } else {
            printf("Unknown option: %s\n", argv[1]);
            printf("Use --help for usage information\n");
        }

    } else {
        // Interactive mode
        printf("🖥️  Starting interactive mode...\n");
        printf("(Use --demo for demonstration or --help for more options)\n");
        run_interactive_mode();
    }

    // Cleanup
    log_event("System shutting down");
    log_close();

    printf("\n✅ System shutdown complete\n");
    return 0;
}
