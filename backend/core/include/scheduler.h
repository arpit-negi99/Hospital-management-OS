#ifndef SCHEDULER_H
#define SCHEDULER_H

#include "patient.h"

/**
 * @brief Schedules patients using the First-Come, First-Served (FCFS) algorithm.
 *
 * @param patients An array of Patient structs.
 * @param count The number of patients in the array.
 */
void schedule_fcfs(Patient* patients, int count);

// We will add the declarations for other schedulers here as we implement them.
void schedule_priority(Patient* patients, int count);
void schedule_round_robin(Patient* patients, int count, int time_quantum);
void schedule_mlfq(Patient* patients, int count);

#endif // SCHEDULER_H