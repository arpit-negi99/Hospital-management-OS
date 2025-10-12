#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "scheduler.h"

#define NUM_QUEUES 3
#define Q1_QUANTUM 4
#define Q2_QUANTUM 8

// A simple structure for our queues
typedef struct {
    int* items;
    int front;
    int rear;
    int count;
    int capacity;
} Queue;

// Helper functions for the queue
void init_queue(Queue* q, int capacity) {
    q->items = malloc(capacity * sizeof(int));
    q->front = 0;
    q->rear = -1;
    q->count = 0;
    q->capacity = capacity;
}

void enqueue(Queue* q, int item) {
    q->rear = (q->rear + 1) % q->capacity;
    q->items[q->rear] = item;
    q->count++;
}

int dequeue(Queue* q) {
    int item = q->items[q->front];
    q->front = (q->front + 1) % q->capacity;
    q->count--;
    return item;
}

void schedule_mlfq(Patient* patients, int count) {
    int current_time = 0;
    int completed_count = 0;
    float total_waiting_time = 0;
    float total_turnaround_time = 0;

    Queue queues[NUM_QUEUES];
    for (int i = 0; i < NUM_QUEUES; i++) {
        init_queue(&queues[i], count);
    }

    bool* arrived = calloc(count, sizeof(bool));

    for (int i = 0; i < count; i++) {
        patients[i].remaining_burst_time = patients[i].burst_time;
    }

    printf("\n--- MLFQ Scheduling Results ---\n");
    printf("Execution Log:\n");

    while (completed_count < count) {
        // Add newly arrived patients to the highest priority queue (Q1)
        for (int i = 0; i < count; i++) {
            if (!arrived[i] && patients[i].arrival_time <= current_time) {
                printf("Time %d: Patient %d arrived and entered Q1.\n", current_time, patients[i].patient_id);
                enqueue(&queues[0], i);
                arrived[i] = true;
                patients[i].current_queue = 1;
            }
        }

        int patient_index = -1;
        int current_queue_level = -1;

        // Find a patient to run from the highest priority non-empty queue
        for (int i = 0; i < NUM_QUEUES; i++) {
            if (queues[i].count > 0) {
                patient_index = dequeue(&queues[i]);
                current_queue_level = i;
                break;
            }
        }

        if (patient_index == -1) {
            printf("Time %d: CPU is idle.\n", current_time);
            current_time++;
            continue;
        }

        int quantum = 0;
        if (current_queue_level == 0) quantum = Q1_QUANTUM;
        else if (current_queue_level == 1) quantum = Q2_QUANTUM;
        else quantum = patients[patient_index].remaining_burst_time; // FCFS for Q3

        int time_to_run = (patients[patient_index].remaining_burst_time < quantum)
                          ? patients[patient_index].remaining_burst_time
                          : quantum;
        
        printf("Time %d: Patient %d from Q%d runs for %d unit(s).\n", current_time, patients[patient_index].patient_id, current_queue_level + 1, time_to_run);
        
        current_time += time_to_run;
        patients[patient_index].remaining_burst_time -= time_to_run;

        // Check for new arrivals DURING the execution slice before making a decision on the current process
        for (int i = 0; i < count; i++) {
            if (!arrived[i] && patients[i].arrival_time <= current_time) {
                printf("Time %d: Patient %d arrived and entered Q1.\n", current_time, patients[i].patient_id);
                enqueue(&queues[0], i);
                arrived[i] = true;
                patients[i].current_queue = 1;
            }
        }
        
        if (patients[patient_index].remaining_burst_time == 0) {
            printf("Time %d: Patient %d finished.\n", current_time, patients[patient_index].patient_id);
            completed_count++;
            patients[patient_index].completion_time = current_time;
        } else {
            // Demote if it used the full quantum and is not in the last queue
            if (time_to_run == quantum && current_queue_level < NUM_QUEUES - 1) {
                printf("Time %d: Patient %d demoted to Q%d.\n", current_time, patients[patient_index].patient_id, current_queue_level + 2);
                enqueue(&queues[current_queue_level + 1], patient_index);
                patients[patient_index].current_queue = current_queue_level + 2;
            } else { // Otherwise, add it back to the end of its current queue
                enqueue(&queues[current_queue_level], patient_index);
            }
        }
    }

    printf("\n--- Final Metrics ---\n");
    printf("+------------+--------------+------------+-----------------+---------------+-----------------+\n");
    printf("| Patient ID | Arrival Time | Burst Time | Completion Time | Waiting Time  | Turnaround Time |\n");
    printf("+------------+--------------+------------+-----------------+---------------+-----------------+\n");
    for(int i = 0; i < count; i++) {
        patients[i].turnaround_time = patients[i].completion_time - patients[i].arrival_time;
        patients[i].waiting_time = patients[i].turnaround_time - patients[i].burst_time;
        total_waiting_time += patients[i].waiting_time;
        total_turnaround_time += patients[i].turnaround_time;
        printf("| %-10d | %-12d | %-10d | %-15d | %-13d | %-15d |\n",
               patients[i].patient_id, patients[i].arrival_time, patients[i].burst_time,
               patients[i].completion_time, patients[i].waiting_time, patients[i].turnaround_time);
    }
    printf("+------------+--------------+------------+-----------------+---------------+-----------------+\n\n");
    printf("Average Waiting Time: %.2f\n", total_waiting_time / count);
    printf("Average Turnaround Time: %.2f\n", total_turnaround_time / count);

    for(int i = 0; i < NUM_QUEUES; i++) free(queues[i].items);
    free(arrived);
}