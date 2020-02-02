"""
Trucks should keep a log of where they've been and the packages they contain.
Trucks should offer a method to calculate miles driven, packages delivered, and time spent driving.

"""
from enum import Enum, auto
from typing import List, Dict

from model.location import Location
from model.routing_table import RoutingTable
from model.sim_time import SimTime
from model.package import Package, PackageStatus, InvalidOperationFromStatusError
from model.package_group import PackageGroup
from route_optimizer import RouteOptimizer


class Truck(object):
    # Associates package groups to trucks for reverse lookup
    package_group_loading_dict: Dict[PackageGroup, 'Truck'] = {}

    def __init__(self, truck_num, sim_time: SimTime, hub: Location, routing_table: RoutingTable):
        self.package_capacity = 16  # Defined in spec
        self.speed_mph = 18  # Defined in spec
        self.package_groups: List[PackageGroup] = []  # Packages currently on truck
        self.log = [TruckLogEntry(sim_time)]  # Events involving this truck
        self.truck_num = truck_num
        self.current_location = hub  # All trucks start at hub / WGU
        self.sim_time = sim_time
        self.routing_table = routing_table
        self.route: List[Location] = []  # Unused until fully loaded

    def load_package_group(self, package_group: PackageGroup):
        # Don't load package group if it won't fit on the truck
        if self.get_package_count() + package_group.get_count() > self.package_capacity:
            raise OverflowError(f"ERROR: Truck {self.truck_num} can't fit {package_group} on it!")

        # Don't load the package group if any of its items aren't ready for pickup
        if package_group.get_status() != PackageStatus.READY_FOR_PICKUP:
            raise InvalidOperationFromStatusError(
                f"Can't load package group {package_group} because it's currently {package_group.get_status()}")

        self.package_groups.append(package_group)
        self.log.append(TruckLogEntry.new_load_entry(package_group, self.sim_time))
        package_group.update_status(PackageStatus.LOADED_ON_TRUCK)
        Truck.package_group_loading_dict[package_group] = self

    def unload_package_group(self, package_group: PackageGroup, note = ""):
        self.package_groups.remove(package_group)
        self.log.append(TruckLogEntry.new_unload_entry(package_group, self.sim_time))
        package_group.update_status(PackageStatus.DELIVERED)
        print(f"Unloaded {package_group.get_count()} packages from truck {self.truck_num}. "
              f"Now at {self.get_package_count()} package(s) on truck.")

    def get_package_count(self):
        return sum(pg.get_count() for pg in self.package_groups)

    def get_locations_on_route(self) -> List[Location]:
        return [pg.destination for pg in self.package_groups]

    def calculate_miles_driven(self):
        return sum(x.distance for x in self.log if x.entry_type == TruckLogEntryType.DROVE)

    def get_loaded_ids(self):
        output = []
        for pg in self.package_groups:
            output.extend(pg.get_ids())
        return output

    def get_last_log_entry(self):
        return self.log[-1]

    def determine_route(self):
        route_optimizer = RouteOptimizer(self.get_locations_on_route())
        self.route = route_optimizer.get_optimized_smart()
        print(f"Truck {self.truck_num} route loaded: {', '.join([l.shortname for l in self.route])}")

    def drive_to(self, location: Location):
        if location not in self.route:
            raise ValueError(f"Location '{location.name}' not on truck {self.truck_num}'s route.")
        if location == self.current_location:
            raise ValueError(f"Truck {self.truck_num}'s is already at the "
                             f"location {location.name} and cannot drive there.")

        distance = self.routing_table.lookup(self.current_location.loc_id, location.loc_id)
        self.log.append(TruckLogEntry.new_drove_entry(self.current_location, location, distance, self.sim_time))
        self.current_location = location

    def unload_packages_for_here(self):
        here_pg = [pg for pg in self.package_groups if pg.destination == self.current_location]
        if len(here_pg) == 0:
            raise ValueError(f"No package groups currently loaded on truck {self.truck_num} are "
                             f"destined for '{self.current_location.name}'")
        for pg in here_pg:
            self.unload_package_group(pg)

    @classmethod
    def get_truck_loaded_on(cls, package_group: PackageGroup):
        return Truck.package_group_loading_dict.get(package_group)

class TruckLogEntryType(Enum):
    LOADED = "Loaded packages"
    UNLOADED = "Unloaded package(s)"
    DROVE = "Drove to location"
    CREATED = "Truck object created"


class TruckLogEntry(object):

    def __init__(self, sim_time: SimTime):
        self.time: float = sim_time.get_now()

    @staticmethod
    def new_load_entry(package, time, note: str = ""):
        output = TruckLogEntry(time)
        output.entry_type = TruckLogEntryType.LOADED
        output.package = package
        output.note = note
        return output

    @staticmethod
    def new_unload_entry(package, time, note: str = ""):
        output = TruckLogEntry(time)
        output.entry_type = TruckLogEntryType.UNLOADED
        output.package = package
        output.note = note
        return output

    @staticmethod
    def new_drove_entry(start: Location, end: Location, distance: float, time: SimTime, note: str = ""):
        output = TruckLogEntry(time)
        output.entry_type = TruckLogEntryType.DROVE
        output.start_location = start
        output.end_location = end
        output.distance = distance
        output.note = note
        return output
