#ifndef LOGGER_H
#define LOGGER_H

// Initializes the logger with a filename
void log_init(const char* filename);

// Logs a formatted message with a timestamp
void log_event(const char* message);

// Closes the log file
void log_close();

#endif // LOGGER_H