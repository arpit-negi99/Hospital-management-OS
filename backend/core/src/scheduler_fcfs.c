#include <stdio.h>
#include <stdlib.h>
#include "scheduler.h"

// Comparison function for qsort to sort patients by arrival time
static int compare_by_arrival(const void* a, const void* b) {
    Patient* p1 = (Patient*)a;
    Patient* p2 = (Patient*)b;
    return (p1->arrival_time - p2->arrival_time);
}

void schedule_fcfs(Patient* patients, int count) {
    // Sort patients based on arrival time to simulate the FCFS queue
    qsort(patients, count, sizeof(Patient), compare_by_arrival);

    int current_time = 0;
    float total_waiting_time = 0;
    float total_turnaround_time = 0;

    printf("\n--- FCFS Scheduling Results ---\n");
    printf("+------------+--------------+------------+-----------------+---------------+-----------------+\n");
    printf("| Patient ID | Arrival Time | Burst Time | Completion Time | Waiting Time  | Turnaround Time |\n");
    printf("+------------+--------------+------------+-----------------+---------------+-----------------+\n");

    for (int i = 0; i < count; i++) {
        // If the system is idle, fast-forward time to the next patient's arrival
        if (current_time < patients[i].arrival_time) {
            current_time = patients[i].arrival_time;
        }

        // Calculate metrics for the current patient
        patients[i].completion_time = current_time + patients[i].burst_time;
        patients[i].turnaround_time = patients[i].completion_time - patients[i].arrival_time;
        patients[i].waiting_time = patients[i].turnaround_time - patients[i].burst_time;

        total_waiting_time += patients[i].waiting_time;
        total_turnaround_time += patients[i].turnaround_time;

        // The system time moves to the completion time of the current patient
        current_time = patients[i].completion_time;

        printf("| %-10d | %-12d | %-10d | %-15d | %-13d | %-15d |\n",
               patients[i].patient_id, patients[i].arrival_time, patients[i].burst_time,
               patients[i].completion_time, patients[i].waiting_time, patients[i].turnaround_time);
    }
    printf("+------------+--------------+------------+-----------------+---------------+-----------------+\n\n");

    printf("Average Waiting Time: %.2f\n", total_waiting_time / count);
    printf("Average Turnaround Time: %.2f\n", total_turnaround_time / count);
}