import re
from enum import Enum, auto
from model.sim_time import SimTime

class Package(object):

    def __init__(self, package_id: int, sim_time: SimTime, dest_address: str, dest_zip: str,
                 delivery_deadline: int = 0, notes: str = ""):

        self.log = []
        self.status = 0
        self.update_state(PackageStatus.READY_FOR_PICKUP, sim_time)

        # Params
        self.package_id = package_id
        self.dest_address = dest_address
        self.dest_zip = dest_zip
        self.notes = notes

        # Constraints
        self.delivery_deadline = delivery_deadline  # 0 indicates EOD
        self.delayed_until = 0  # 0 indicates no delay
        self.valid_trucks = []  # By default, all trucks are valid
        self.linked_package_ids = []
        self.parse_notes()

    def parse_notes(self):
        """Look through the package's notes for constraints."""
        truck_note = "Can only be on truck"
        if truck_note in self.notes:
            truck_num_index = self.notes.find(truck_note) + len(truck_note) + 1
            truck_num = self.notes[truck_num_index:truck_num_index + 1]
            valid_trucks = truck_num
            print(f"Note: Package {self.package_id} can only go on truck {truck_num}")

        # Linked package notes parsing will fail if it's not the last note
        # If that's problematic, add a delimiter between notes on input and update lpn to look for it
        lpn = "Must be delivered with"  # Linked Package notes
        if lpn in self.notes:
            lpn_index = self.notes.find(lpn) + len(lpn) + 1  # Starting point for any linked package notes
            lps_string = self.notes[lpn_index:]
            self.linked_package_ids = [int(i) for i in re.split(r'\D+', lps_string)]  # r prefix indicates regex string

    def update_state(self, new_status, sim_time):
        self.status = new_status
        self.log.append(PackageLogEntry(new_status, sim_time))

    def __repr__(self):
        return f"Package({self.package_id},{self.destination_location},{self.delivery_deadline},{self.notes})"

    def __str__(self):
        return f"({self.package_id},{self.destination_location},{self.delivery_deadline},{self.notes})"


class PackageStatus(Enum):
    READY_FOR_PICKUP = "Ready for pickup"
    UNDELIVERABLE = "Undeliverable, constrained"
    LOADED_ON_TRUCK = "Loaded on truck"
    DELIVERED = "Delivered"


class PackageLogEntry(object):
    def __init__(self, status: PackageStatus, sim_time: SimTime):
        self.status = status
        self.time = sim_time.get_now()
