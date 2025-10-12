/*
#include <stdio.h>
#include <pthread.h>
#include <unistd.h> // For sleep()

#include "synchronization.h"

#define NUM_THREADS 5
#define INCREMENTS_PER_THREAD 1000

// --- Shared Resources ---
long long shared_counter = 0;
pthread_mutex_t counter_mutex;
// ----------------------

// The function each thread will execute without a mutex
void* thread_work_without_mutex(void* arg) {
    for (int i = 0; i < INCREMENTS_PER_THREAD; i++) {
        // RACE CONDITION HAPPENS HERE:
        // A thread might read the value of shared_counter,
        // another thread might also read the SAME value before the first one writes it back,
        // then both will increment and write back the same new value, losing one increment.
        shared_counter++;
    }
    return NULL;
}

// The function each thread will execute WITH a mutex
void* thread_work_with_mutex(void* arg) {
    for (int i = 0; i < INCREMENTS_PER_THREAD; i++) {
        // Lock the mutex before touching the shared resource
        pthread_mutex_lock(&counter_mutex);

        // --- CRITICAL SECTION START ---
        // Only one thread can be in this section at a time.
        shared_counter++;
        // --- CRITICAL SECTION END ---

        // Unlock the mutex after touching the shared resource
        pthread_mutex_unlock(&counter_mutex);
    }
    return NULL;
}

void run_synchronization_demo() {
    pthread_t threads[NUM_THREADS];
    long long expected_value = NUM_THREADS * INCREMENTS_PER_THREAD;

    printf("\n--- Synchronization Demonstration ---\n");

    // --- Part 1: Without a Mutex (Demonstrating the Race Condition) ---
    printf("\n[1] Running with %d threads WITHOUT a mutex...\n", NUM_THREADS);
    shared_counter = 0; // Reset counter

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, thread_work_without_mutex, NULL);
    }
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }
    printf("-> Final counter value: %lld (Expected: %lld)\n", shared_counter, expected_value);
    if (shared_counter != expected_value) {
        printf("-> Notice: The result is incorrect due to the race condition!\n");
    }

    // --- Part 2: With a Mutex (Fixing the Race Condition) ---
    printf("\n[2] Running with %d threads WITH a mutex...\n", NUM_THREADS);
    shared_counter = 0; // Reset counter

    // Initialize the mutex
    pthread_mutex_init(&counter_mutex, NULL);

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, thread_work_with_mutex, NULL);
    }
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    // Destroy the mutex after use
    pthread_mutex_destroy(&counter_mutex);

    printf("-> Final counter value: %lld (Expected: %lld)\n", shared_counter, expected_value);
    if (shared_counter == expected_value) {
        printf("-> Notice: The result is correct because the mutex prevented the race condition!\n");
    }
}
*/

/*
#include <stdio.h>
#include <windows.h>

#include "synchronization.h"

#define NUM_THREADS 5
#define INCREMENTS_PER_THREAD 1000

// --- Shared Resources ---
long long shared_counter = 0;
CRITICAL_SECTION counter_critical_section;
// ----------------------

// The function each thread will execute without a mutex
DWORD WINAPI thread_work_without_mutex(LPVOID arg) {
    for (int i = 0; i < INCREMENTS_PER_THREAD; i++) {
        shared_counter++;
    }
    return 0;
}

// The function each thread will execute WITH a mutex
DWORD WINAPI thread_work_with_mutex(LPVOID arg) {
    for (int i = 0; i < INCREMENTS_PER_THREAD; i++) {
        EnterCriticalSection(&counter_critical_section);
        shared_counter++;
        LeaveCriticalSection(&counter_critical_section);
    }
    return 0;
}

void run_synchronization_demo() {
    HANDLE threads[NUM_THREADS];
    long long expected_value = NUM_THREADS * INCREMENTS_PER_THREAD;

    printf("\n--- Synchronization Demonstration ---\n");

    // --- Part 1: Without a Mutex (Demonstrating the Race Condition) ---
    printf("\n[1] Running with %d threads WITHOUT a mutex...\n", NUM_THREADS);
    shared_counter = 0; // Reset counter

    for (int i = 0; i < NUM_THREADS; i++) {
        threads[i] = CreateThread(NULL, 0, thread_work_without_mutex, NULL, 0, NULL);
    }
    WaitForMultipleObjects(NUM_THREADS, threads, TRUE, INFINITE);
    for (int i = 0; i < NUM_THREADS; i++) {
        CloseHandle(threads[i]);
    }
    printf("-> Final counter value: %lld (Expected: %lld)\n", shared_counter, expected_value);
    if (shared_counter != expected_value) {
        printf("-> Notice: The result is incorrect due to the race condition!\n");
    }

    // --- Part 2: With a Mutex (Fixing the Race Condition) ---
    printf("\n[2] Running with %d threads WITH a mutex...\n", NUM_THREADS);
    shared_counter = 0; // Reset counter

    InitializeCriticalSection(&counter_critical_section);

    for (int i = 0; i < NUM_THREADS; i++) {
        threads[i] = CreateThread(NULL, 0, thread_work_with_mutex, NULL, 0, NULL);
    }
    WaitForMultipleObjects(NUM_THREADS, threads, TRUE, INFINITE);
    for (int i = 0; i < NUM_THREADS; i++) {
        CloseHandle(threads[i]);
    }

    DeleteCriticalSection(&counter_critical_section);

    printf("-> Final counter value: %lld (Expected: %lld)\n", shared_counter, expected_value);
    if (shared_counter == expected_value) {
        printf("-> Notice: The result is correct because the critical section prevented the race condition!\n");
    }
}
*/