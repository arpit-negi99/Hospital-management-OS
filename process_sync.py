"""Process Synchronization Module"""
import threading

class ProcessSynchronization:
    def __init__(self, num_doctors=3):
        self.num_doctors = num_doctors
        self.semaphore = threading.Semaphore(num_doctors)
        self.lock = threading.RLock()
        self.sync_event = threading.Event()
