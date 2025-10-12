#include <stdio.h>
#include <stdlib.h>
#include "scheduler.h"

void schedule_round_robin(Patient* patients, int count, int time_quantum) {
    int current_time = 0;
    int completed_count = 0;
    float total_waiting_time = 0;
    float total_turnaround_time = 0;

    // A simple array to act as our Ready Queue, storing patient indices
    int* ready_queue = malloc(count * sizeof(int));
    int queue_front = 0;
    int queue_rear = 0;
    int in_queue_count = 0;
    
    // An array to track if a patient has been added to the ready queue
    int* is_in_queue = calloc(count, sizeof(int));

    // Initialize remaining burst time for all patients
    for (int i = 0; i < count; i++) {
        patients[i].remaining_burst_time = patients[i].burst_time;
    }

    printf("\n--- Round Robin Scheduling Results (Time Quantum = %d) ---\n", time_quantum);
    printf("Execution Log:\n");

    while (completed_count < count) {
        // Add newly arrived patients to the ready queue
        for (int i = 0; i < count; i++) {
            if (patients[i].arrival_time <= current_time && patients[i].remaining_burst_time > 0 && !is_in_queue[i]) {
                ready_queue[queue_rear] = i;
                queue_rear = (queue_rear + 1) % count;
                in_queue_count++;
                is_in_queue[i] = 1; // Mark as added
            }
        }

        if (in_queue_count == 0) {
            printf("Time %d: CPU is idle.\n", current_time);
            current_time++;
            continue; // Skip to the next time unit if queue is empty
        }

        // Dequeue a patient
        int current_patient_index = ready_queue[queue_front];
        queue_front = (queue_front + 1) % count;
        in_queue_count--;

        // Execute the patient for the time quantum or its remaining time
        int time_to_run = (patients[current_patient_index].remaining_burst_time < time_quantum)
                          ? patients[current_patient_index].remaining_burst_time
                          : time_quantum;
        
        printf("Time %d: Patient %d runs for %d unit(s).\n", current_time, patients[current_patient_index].patient_id, time_to_run);

        patients[current_patient_index].remaining_burst_time -= time_to_run;
        current_time += time_to_run;

        // Check for new arrivals DURING the execution slice
        for (int i = 0; i < count; i++) {
            if (patients[i].arrival_time <= current_time && patients[i].remaining_burst_time > 0 && !is_in_queue[i]) {
                ready_queue[queue_rear] = i;
                queue_rear = (queue_rear + 1) % count;
                in_queue_count++;
                is_in_queue[i] = 1;
            }
        }

        // If patient is finished
        if (patients[current_patient_index].remaining_burst_time == 0) {
            printf("Time %d: Patient %d finished.\n", current_time, patients[current_patient_index].patient_id);
            completed_count++;
            patients[current_patient_index].completion_time = current_time;
            patients[current_patient_index].turnaround_time = patients[current_patient_index].completion_time - patients[current_patient_index].arrival_time;
            patients[current_patient_index].waiting_time = patients[current_patient_index].turnaround_time - patients[current_patient_index].burst_time;
            total_waiting_time += patients[current_patient_index].waiting_time;
            total_turnaround_time += patients[current_patient_index].turnaround_time;
        } else {
            // If not finished, add back to the end of the queue
            ready_queue[queue_rear] = current_patient_index;
            queue_rear = (queue_rear + 1) % count;
            in_queue_count++;
        }
    }

    // Print final results table
    printf("\n--- Final Metrics ---\n");
    printf("+------------+--------------+------------+-----------------+---------------+-----------------+\n");
    printf("| Patient ID | Arrival Time | Burst Time | Completion Time | Waiting Time  | Turnaround Time |\n");
    printf("+------------+--------------+------------+-----------------+---------------+-----------------+\n");
    for (int i = 0; i < count; i++) {
        printf("| %-10d | %-12d | %-10d | %-15d | %-13d | %-15d |\n",
               patients[i].patient_id, patients[i].arrival_time, patients[i].burst_time,
               patients[i].completion_time, patients[i].waiting_time, patients[i].turnaround_time);
    }
    printf("+------------+--------------+------------+-----------------+---------------+-----------------+\n\n");

    printf("Average Waiting Time: %.2f\n", total_waiting_time / count);
    printf("Average Turnaround Time: %.2f\n", total_turnaround_time / count);
    
    free(ready_queue);
    free(is_in_queue);
}