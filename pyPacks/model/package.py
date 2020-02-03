import re
from enum import Enum, auto
from typing import List
from model.sim_time import SimTime, parse_time
from model.location import Location


# TODO: Add in "priority" concept for packages with delivery deadlines.
class Package(object):

    def __init__(self, package_id: int, sim_time: SimTime, dest_location: Location, city: str,
                 delivery_deadline: int = 0, mass_kg: float = 0, notes: str = ""):

        self.log = []
        self.status = PackageStatus.INITIALIZED
        self.my_sim_time_tracker = sim_time
        self.update_status(PackageStatus.INITIALIZED)

        # Params
        self.package_id: int = int(package_id)
        self.dest_location: Location = dest_location
        self.city = city
        self.notes: str = notes
        self.mass_kg = mass_kg

        # Constraints
        self.delivery_deadline: float = parse_time(delivery_deadline)  # 1700 indicates EOD
        self.delayed_until: float = 0  # 0 indicates no delay
        self.valid_truck_ids: List[int] = []  # By default, all trucks are valid
        self.linked_package_ids = []
        self.parse_notes()

    def parse_notes(self):
        """Look through the package's notes for constraints."""
        truck_note = "Can only be on truck"
        if truck_note in self.notes:
            truck_num_index = self.notes.find(truck_note) + len(truck_note) + 1
            truck_num = self.notes[truck_num_index:truck_num_index + 1]
            valid_trucks = [truck_num]  # Only supports one truck
            print(f"Note: Package {self.package_id} can only go on truck {truck_num}")

        # Linked package notes parsing will fail if it's not the last note
        # If that's problematic, add a delimiter between notes on input and update lpn to look for it
        lpn = "Must be delivered with"  # Linked Package notes
        if lpn in self.notes:
            # Find the linked package list
            lpn_index = self.notes.find(lpn) + len(lpn) + 1  # Starting point for any linked package notes
            lps_string = self.notes[lpn_index:]
            self.linked_package_ids = [int(i) for i in re.split(r'\D+', lps_string)]  # r prefix indicates regex string
            print(f"Note: Package {self.package_id} must be delivered with {self.linked_package_ids}")

        # Delayed until...
        delayed_note = "Delayed on flight---will not arrive to depot until"
        if delayed_note in self.notes:
            self.update_status(PackageStatus.DELAYED)
            dn_index = self.notes.find(delayed_note) + len(delayed_note) + 1
            delay_time_string = self.notes[dn_index:]
            self.delayed_until = parse_time(delay_time_string)
        elif self.notes == "Wrong address listed":
            self.delayed_until = 1020  # From task docs
            self.update_status(PackageStatus.DELAYED)
        else:
            self.update_status(PackageStatus.READY_FOR_PICKUP)

    def get_rem_time(self) -> float:
        """Retrieves the remaining time until delivery in hours."""
        rem = self.delivery_deadline - self.my_sim_time_tracker.get_now()
        rem_hours = rem / 100
        return rem_hours

    def update_status(self, new_status):
        # Prevent transitions from DELAYED to LOADED_ON_TRUCK
        if self.status == PackageStatus.DELAYED and new_status == PackageStatus.LOADED_ON_TRUCK:
            raise StatusTransitionError(PackageStatus.DELAYED, PackageStatus.LOADED_ON_TRUCK)

        self.status = new_status
        self.log.append(PackageLogEntry(new_status, self.my_sim_time_tracker))

    def verbose_str(self):
        from model.package_group import PackageGroup
        from model.truck import Truck

        dest = self.dest_location
        address_string = ", ".join([dest.address, self.city, dest.zip])

        status_header_len = max(len("Status"), PackageStatus.get_longest_len())
        enhanced_status = self.status.value
        if self.status == PackageStatus.DELAYED:
            enhanced_status = f"Delayed: {self.delayed_until:.0f}"
        elif self.status == PackageStatus.DELIVERED:
            dlv_time = self.log[-1].time
            if dlv_time > self.delivery_deadline:
                enhanced_status = f"LATE DELIV @ {dlv_time:.1f}"
            else:
                enhanced_status = f"Delivered @ {dlv_time:.1f}"
        elif self.status == PackageStatus.LOADED_ON_TRUCK:
            my_pg = PackageGroup.get_owning_package_group(self.package_id)
            my_truck = Truck.get_truck_loaded_on(my_pg)
            enhanced_status = f"Loaded on truck {my_truck.truck_num}"
        status_string = "{:{sw}}".format(enhanced_status, sw=status_header_len)

        deadline_string = "EOD" if self.delivery_deadline == 0 else f"{self.delivery_deadline:.0f}"
        return f"ID: {self.package_id:2}\t{status_string}\t" \
               f"{address_string:<45}\tDeadline:{deadline_string:4}\tKG: {self.mass_kg}\t Notes: {self.notes}"

    def __repr__(self):
        return f"Package(ID {self.package_id},{self.dest_location.name})"

    def __str__(self):
        return f"Package(ID {self.package_id},{self.dest_location.name},{self.delivery_deadline},{self.notes})"


class InvalidOperationFromStatusError(Exception):
    """An operation was attempted that isn't valid with this status."""

    def __init__(self, message):
        self.message = message


class StatusTransitionError(Exception):
    """An invalid status change was attempted."""

    def __init__(self, previous_status, next_status):
        self.previous = previous_status
        self.next = next_status
        self.message = f"Can't move from {previous_status} to {next_status}!"


class PackageStatus(Enum):
    INITIALIZED = "Package created"
    READY_FOR_PICKUP = "Ready for pickup"
    DELAYED = "Delayed"
    LOADED_ON_TRUCK = "Loaded on truck"
    DELIVERED = "Delivered"
    RETURN_TO_HUB = "Must return to hub"

    @classmethod
    def get_longest_len(cls):
        return max([len(x.value) for x in PackageStatus])


class PackageLogEntry(object):
    def __init__(self, status: PackageStatus, sim_time: SimTime):
        self.status = status
        self.time = sim_time.get_now()

    def __str__(self):
        return f"{self.status} @ {self.time}"
