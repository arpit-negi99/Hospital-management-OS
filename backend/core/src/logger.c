#include <stdio.h>
#include <time.h>
#include <string.h> // Required for strlen
#include "logger.h"

static FILE* log_file = NULL;

void log_init(const char* filename) {
    log_file = fopen(filename, "a"); // Append mode
    if (log_file == NULL) {
        perror("Could not open log file");
    }
}

void log_event(const char* message) {
    if (log_file == NULL) {
        printf("Logger not initialized.\n");
        return;
    }

    time_t now = time(NULL);
    // Use the standard ctime() function, which is available on Windows/MinGW
    char* time_str = ctime(&now);
    
    // ctime() adds its own newline character at the end, so we remove it
    time_str[strlen(time_str) - 1] = '\0'; 

    fprintf(log_file, "[%s] %s\n", time_str, message);
    fflush(log_file); // Ensure the log is written immediately
}

void log_close() {
    if (log_file != NULL) {
        fclose(log_file);
        log_file = NULL;
    }
}