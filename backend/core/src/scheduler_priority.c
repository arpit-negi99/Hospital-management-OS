#include <stdio.h>
#include <stdlib.h>
#include "scheduler.h"

// Comparison function for qsort to sort by priority (lower number = higher priority)
// If priorities are equal, it uses arrival time as a tie-breaker (FCFS)
static int compare_by_priority(const void* a, const void* b) {
    Patient* p1 = (Patient*)a;
    Patient* p2 = (Patient*)b;

    if (p1->priority < p2->priority) return -1;
    if (p1->priority > p2->priority) return 1;

    // Tie-breaker: if priorities are the same, the one that arrived first goes first
    return (p1->arrival_time - p2->arrival_time);
}

void schedule_priority(Patient* patients, int count) {
    qsort(patients, count, sizeof(Patient), compare_by_priority);

    int current_time = 0;
    float total_waiting_time = 0;
    float total_turnaround_time = 0;

    printf("\n--- Non-Preemptive Priority Scheduling Results ---\n");
    printf("+------------+----------+--------------+------------+-----------------+---------------+-----------------+\n");
    printf("| Patient ID | Priority | Arrival Time | Burst Time | Completion Time | Waiting Time  | Turnaround Time |\n");
    printf("+------------+----------+--------------+------------+-----------------+---------------+-----------------+\n");

    for (int i = 0; i < count; i++) {
        if (current_time < patients[i].arrival_time) {
            current_time = patients[i].arrival_time;
        }

        patients[i].completion_time = current_time + patients[i].burst_time;
        patients[i].turnaround_time = patients[i].completion_time - patients[i].arrival_time;
        patients[i].waiting_time = patients[i].turnaround_time - patients[i].burst_time;

        total_waiting_time += patients[i].waiting_time;
        total_turnaround_time += patients[i].turnaround_time;

        current_time = patients[i].completion_time;

        printf("| %-10d | %-8d | %-12d | %-10d | %-15d | %-13d | %-15d |\n",
               patients[i].patient_id, patients[i].priority, patients[i].arrival_time, patients[i].burst_time,
               patients[i].completion_time, patients[i].waiting_time, patients[i].turnaround_time);
    }
    printf("+------------+----------+--------------+------------+-----------------+---------------+-----------------+\n\n");

    printf("Average Waiting Time: %.2f\n", total_waiting_time / count);
    printf("Average Turnaround Time: %.2f\n", total_turnaround_time / count);
}