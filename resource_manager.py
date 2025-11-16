"""Resource Manager with Fixed Deallocation"""
import threading
from datetime import datetime
from enum import Enum

class ResourceType(Enum):
    BED = "BED"
    OPERATION_ROOM = "OR"
    VENTILATOR = "VENTILATOR"
    MONITOR = "MONITOR"

class Resource:
    def __init__(self, resource_id, resource_type, available=True):
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.available = available
        self.assigned_to = None
        self.assigned_doctor = None
        self.allocation_time = None
        self.notes = ""

class ResourceManager:
    def __init__(self, num_beds=10, num_operation_rooms=3, num_ventilators=5, num_monitors=10):
        self.num_beds = num_beds
        self.num_operation_rooms = num_operation_rooms
        self.num_ventilators = num_ventilators
        self.num_monitors = num_monitors

        # Initialize resources with PROPER ID FORMATTING
        self.beds = {f"BED-{i:03d}": Resource(f"BED-{i:03d}", ResourceType.BED) for i in range(1, num_beds + 1)}
        self.operation_rooms = {f"OR-{i:03d}": Resource(f"OR-{i:03d}", ResourceType.OPERATION_ROOM) for i in range(1, num_operation_rooms + 1)}
        self.ventilators = {f"VENT-{i:03d}": Resource(f"VENT-{i:03d}", ResourceType.VENTILATOR) for i in range(1, num_ventilators + 1)}
        self.monitors = {f"MON-{i:03d}": Resource(f"MON-{i:03d}", ResourceType.MONITOR) for i in range(1, num_monitors + 1)}

        self.bed_lock = threading.RLock()
        self.or_lock = threading.RLock()
        self.vent_lock = threading.RLock()
        self.mon_lock = threading.RLock()

        self.allocation_history = []
        self.event = threading.Event()

    def allocate_bed(self, patient_id, doctor_id, notes=""):
        """Allocate bed with synchronization"""
        with self.bed_lock:
            for bed_id, bed in self.beds.items():
                if bed.available:
                    bed.available = False
                    bed.assigned_to = patient_id
                    bed.assigned_doctor = doctor_id
                    bed.allocation_time = datetime.now()
                    bed.notes = notes

                    self.allocation_history.append({
                        'resource': bed.resource_id,
                        'patient': patient_id,
                        'doctor': doctor_id,
                        'timestamp': bed.allocation_time.isoformat(),
                        'action': 'ALLOCATED'
                    })

                    self.event.set()
                    self.event.clear()

                    return True, f"Bed {bed.resource_id} allocated to {patient_id}", bed.resource_id

            return False, "No beds available", None

    def deallocate_bed(self, bed_id, doctor_id):
        """Deallocate bed - FIXED"""
        with self.bed_lock:
            # FIX: Search for the bed ID correctly
            if bed_id in self.beds:
                bed = self.beds[bed_id]
                if not bed.available:
                    patient_id = bed.assigned_to
                    bed.available = True
                    bed.assigned_to = None
                    bed.assigned_doctor = None

                    self.allocation_history.append({
                        'resource': bed.resource_id,
                        'patient': patient_id,
                        'doctor': doctor_id,
                        'timestamp': datetime.now().isoformat(),
                        'action': 'DEALLOCATED'
                    })

                    self.event.set()
                    self.event.clear()

                    return True, f"Bed {bed.resource_id} deallocated", patient_id
                else:
                    return False, f"Bed {bed_id} is not allocated", None
            else:
                # Return more helpful error message
                return False, f"Bed {bed_id} not found. Available beds: {', '.join(self.beds.keys())}", None

    def allocate_operation_room(self, patient_id, doctor_id, notes=""):
        """Allocate operation room with synchronization"""
        with self.or_lock:
            for or_id, or_room in self.operation_rooms.items():
                if or_room.available:
                    or_room.available = False
                    or_room.assigned_to = patient_id
                    or_room.assigned_doctor = doctor_id
                    or_room.allocation_time = datetime.now()
                    or_room.notes = notes

                    self.allocation_history.append({
                        'resource': or_room.resource_id,
                        'patient': patient_id,
                        'doctor': doctor_id,
                        'timestamp': or_room.allocation_time.isoformat(),
                        'action': 'ALLOCATED'
                    })

                    self.event.set()
                    self.event.clear()

                    return True, f"Operation Room {or_room.resource_id} allocated", or_room.resource_id

            return False, "No operation rooms available", None

    def deallocate_operation_room(self, or_id, doctor_id):
        """Deallocate operation room - FIXED"""
        with self.or_lock:
            if or_id in self.operation_rooms:
                or_room = self.operation_rooms[or_id]
                if not or_room.available:
                    patient_id = or_room.assigned_to
                    or_room.available = True
                    or_room.assigned_to = None
                    or_room.assigned_doctor = None

                    self.allocation_history.append({
                        'resource': or_room.resource_id,
                        'patient': patient_id,
                        'doctor': doctor_id,
                        'timestamp': datetime.now().isoformat(),
                        'action': 'DEALLOCATED'
                    })

                    self.event.set()
                    self.event.clear()

                    return True, f"Operation Room {or_room.resource_id} deallocated", patient_id
                else:
                    return False, f"Operation Room {or_id} is not allocated", None
            else:
                return False, f"Operation Room {or_id} not found", None

    def allocate_ventilator(self, patient_id, doctor_id):
        """Allocate ventilator with synchronization"""
        with self.vent_lock:
            for vent_id, vent in self.ventilators.items():
                if vent.available:
                    vent.available = False
                    vent.assigned_to = patient_id
                    vent.assigned_doctor = doctor_id
                    vent.allocation_time = datetime.now()

                    self.event.set()
                    self.event.clear()

                    return True, f"Ventilator {vent.resource_id} allocated", vent.resource_id

            return False, "No ventilators available", None

    def deallocate_ventilator(self, vent_id, doctor_id):
        """Deallocate ventilator - FIXED"""
        with self.vent_lock:
            if vent_id in self.ventilators:
                vent = self.ventilators[vent_id]
                if not vent.available:
                    patient_id = vent.assigned_to
                    vent.available = True
                    vent.assigned_to = None

                    self.event.set()
                    self.event.clear()

                    return True, f"Ventilator {vent.resource_id} deallocated", patient_id
                else:
                    return False, f"Ventilator {vent_id} is not allocated", None
            else:
                return False, f"Ventilator {vent_id} not found", None

    def allocate_monitor(self, patient_id, doctor_id):
        """Allocate monitor with synchronization"""
        with self.mon_lock:
            for mon_id, mon in self.monitors.items():
                if mon.available:
                    mon.available = False
                    mon.assigned_to = patient_id
                    mon.assigned_doctor = doctor_id
                    mon.allocation_time = datetime.now()

                    self.event.set()
                    self.event.clear()

                    return True, f"Monitor {mon.resource_id} allocated", mon.resource_id

            return False, "No monitors available", None

    def deallocate_monitor(self, mon_id, doctor_id):
        """Deallocate monitor - FIXED"""
        with self.mon_lock:
            if mon_id in self.monitors:
                mon = self.monitors[mon_id]
                if not mon.available:
                    patient_id = mon.assigned_to
                    mon.available = True
                    mon.assigned_to = None

                    self.event.set()
                    self.event.clear()

                    return True, f"Monitor {mon.resource_id} deallocated", patient_id
                else:
                    return False, f"Monitor {mon_id} is not allocated", None
            else:
                return False, f"Monitor {mon_id} not found", None

    def get_status(self):
        """Get all resources status"""
        with self.bed_lock:
            beds_available = sum(1 for b in self.beds.values() if b.available)
            beds_occupied = {b.resource_id: {'patient': b.assigned_to, 'doctor': b.assigned_doctor, 'notes': b.notes} 
                           for b in self.beds.values() if not b.available}

        with self.or_lock:
            or_available = sum(1 for o in self.operation_rooms.values() if o.available)
            or_occupied = {o.resource_id: {'patient': o.assigned_to, 'doctor': o.assigned_doctor, 'notes': o.notes}
                          for o in self.operation_rooms.values() if not o.available}

        with self.vent_lock:
            vent_available = sum(1 for v in self.ventilators.values() if v.available)
            vent_occupied = {v.resource_id: {'patient': v.assigned_to, 'doctor': v.assigned_doctor}
                            for v in self.ventilators.values() if not v.available}

        with self.mon_lock:
            mon_available = sum(1 for m in self.monitors.values() if m.available)
            mon_occupied = {m.resource_id: {'patient': m.assigned_to, 'doctor': m.assigned_doctor}
                           for m in self.monitors.values() if not m.available}

        return {
            'beds': {'total': self.num_beds, 'available': beds_available, 'occupied': beds_occupied},
            'operation_rooms': {'total': self.num_operation_rooms, 'available': or_available, 'occupied': or_occupied},
            'ventilators': {'total': self.num_ventilators, 'available': vent_available, 'occupied': vent_occupied},
            'monitors': {'total': self.num_monitors, 'available': mon_available, 'occupied': mon_occupied},
            'timestamp': datetime.now().isoformat()
        }

    def get_patient_resources(self, patient_id):
        """Get all resources allocated to a patient"""
        resources = {}

        for bed_id, bed in self.beds.items():
            if bed.assigned_to == patient_id:
                resources['bed'] = bed.resource_id

        for or_id, or_room in self.operation_rooms.items():
            if or_room.assigned_to == patient_id:
                resources['operation_room'] = or_room.resource_id

        for vent_id, vent in self.ventilators.items():
            if vent.assigned_to == patient_id:
                resources['ventilator'] = vent.resource_id

        for mon_id, mon in self.monitors.items():
            if mon.assigned_to == patient_id:
                resources['monitor'] = mon.resource_id

        return resources

    def get_available_resources(self):
        """Get list of available resource IDs"""
        return {
            'beds': [bid for bid, b in self.beds.items() if not b.available],
            'operation_rooms': [oid for oid, o in self.operation_rooms.items() if not o.available],
            'ventilators': [vid for vid, v in self.ventilators.items() if not v.available],
            'monitors': [mid for mid, m in self.monitors.items() if not m.available]
        }
