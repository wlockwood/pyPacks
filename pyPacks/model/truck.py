"""
Trucks should keep a log of where they've been and the packages they contain.
Trucks should offer a method to calculate miles driven, packages delivered, and time spent driving.

"""
from enum import Enum, auto
from typing import List

from model.location import Location
from model.sim_time import SimTime
from model.package import Package,PackageStatus
from model.package_group import PackageGroup


class Truck(object):
    def __init__(self, truck_num, sim_time: SimTime):
        self.package_capacity = 16  # Defined in spec
        self.speed_mph = 18  # Defined in spec
        self.package_groups: List[PackageGroup] = []  # Packages currently on truck
        self.log = []  # Events involving this truck
        self.truck_num = truck_num
        self.current_location = 0  # All trucks start at hub / WGU
        self.sim_time = sim_time

    def load_package_group(self, package_group: PackageGroup):
        self.package_groups.append(package_group)
        self.log.append(TruckLogEntry.new_load_entry(package_group, self.sim_time))
        package_group.update_status(PackageStatus.LOADED_ON_TRUCK)
        package_listing: List[Package] = [x.package_id for x in package_group.packages]
        print(f"Loaded {package_group.get_count()} packages {package_listing} bound for '{package_group.destination.name}'"
              f" onto truck {self.truck_num}. "
              f"Now at {self.get_package_count()} packages on truck")

    def unload_package_group(self, package_group: PackageGroup):
        self.package_groups.remove(package_group)
        self.log.append(TruckLogEntry.new_unload_entry(package_group, self.sim_time))
        package_group.update_status(PackageStatus.DELIVERED)
        print(f"Unloaded {package_group.get_count()} packages from truck {self.truck_num}. "
              f"Now at {self.get_package_count()} package(s) on truck.")

    def get_package_count(self):
        return sum(pg.get_count() for pg in self.package_groups)

    def get_locations_on_route(self) -> List[Location]:
        return [pg.destination for pg in self.package_groups]

    def drive_to(self, destination_location_id):
        print("Do things to make truck go places.")
        # TODO: This should probably return an arrival time?

    def calculate_miles_driven(self):
        return sum(x.distance for x in self.log if x.entry_type == TruckLogEntryType.DROVE)


class TruckLogEntryType(Enum):
    LOADED = auto()
    UNLOADED = auto()
    DROVE = auto()


class TruckLogEntry(object):

    def __init__(self, time: SimTime):
        self.time: SimTime = time

    @staticmethod
    def new_load_entry(package, time):
        output = TruckLogEntry(time)
        output.entry_type = TruckLogEntryType.LOADED
        output.package = package
        return output

    @staticmethod
    def new_unload_entry(package, time):
        output = TruckLogEntry(time)
        output.entry_type = TruckLogEntryType.UNLOADED
        output.package = package
        return output

    @staticmethod
    def new_drove_entry(start, end, distance, time):
        output = TruckLogEntry(time)
        output.entry_type = TruckLogEntryType.DROVE
        output.start_location = start
        output.end_location = end
        output.distance = distance
        return output
