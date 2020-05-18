"""
Trucks should keep a log of where they've been and the packages they contain.
Trucks should offer a method to calculate miles driven, packages delivered, and time spent driving.

"""
from enum import Enum, auto
from typing import List, Dict

from model.location import Location
from model.i_routing_table import IRoutingTable
from model.sim_time import SimTime, SimEvent, EventTypes
from model.package import Package, PackageStatus, InvalidOperationFromStatusError
from model.package_group import PackageGroup
from route_optimizer import RouteOptimizer


class Truck(object):
    # Associates package groups to trucks for reverse lookup
    package_group_loading_dict: Dict[PackageGroup, 'Truck'] = {}

    def __init__(self, truck_num, sim_time: SimTime, hub: Location, routing_table: IRoutingTable):
        self.package_capacity = 16  # Defined in spec
        self.speed_mph = 18  # Defined in spec
        self.package_groups: List[PackageGroup] = []  # Packages currently on truck
        self.log = [TruckLogEntry(TruckLogEntryType.CREATED, sim_time)]  # Events involving this truck
        self.truck_num = truck_num
        self.current_location = hub  # All trucks start at hub / WGU
        self.sim_time = sim_time
        self.routing_table = routing_table
        self.route: List[Location] = []  # Unused until fully loaded

    def load_package_group(self, package_group: PackageGroup, note=""):
        # Don't load package group if it won't fit on the truck
        if self.get_package_count() + package_group.get_count() > self.package_capacity:
            raise OverflowError(f"ERROR: Truck {self.truck_num} can't fit {package_group} on it!")

        # Don't load the package group if any of its items aren't ready for pickup
        if package_group.get_status() != PackageStatus.READY_FOR_PICKUP:
            raise InvalidOperationFromStatusError(
                f"Can't load package group {package_group} because it's currently {package_group.get_status()}")

        self.package_groups.append(package_group)
        self.log.append(TruckLogEntry.new_load_entry(self.sim_time, package_group, note))
        package_group.update_status(PackageStatus.LOADED_ON_TRUCK)
        Truck.package_group_loading_dict[package_group] = self

    def unload_package_group(self, package_group: PackageGroup, note=""):
        self.package_groups.remove(package_group)
        self.log.append(TruckLogEntry.new_unload_entry(package_group, self.sim_time, note))
        package_group.update_status(PackageStatus.DELIVERED)
        # print(f"Unloaded {package_group.get_count()} packages from truck {self.truck_num}. "
        #      f"Now at {self.get_package_count()} package(s) on truck.")

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
        route_optimizer = RouteOptimizer(self.get_locations_on_route(), self.routing_table, Location.hub)
        self.route = route_optimizer.get_optimized_smart()
        print(f"Truck {self.truck_num} route loaded: {', '.join([l.shortname for l in self.route])}")

    def drive_to(self, location: Location):
        if location is None:
            raise TruckInvalidOperationError(f"Truck {self.truck_num} cannot drive to a null location.")
        if location not in self.route:
            raise TruckInvalidOperationError(f"Location '{location.name}' not on truck {self.truck_num}'s route.")
        if location == self.current_location:
            raise TruckInvalidOperationError(f"Truck {self.truck_num}'s is already at the "
                                             f"location {location.name} and cannot drive there.")
        if self.get_package_count() == 0 and location != self.route[-1]:
            raise TruckInvalidOperationError(f"Truck {self.truck_num} is empty and should be returning to hub.")

        distance = self.routing_table.lookup(self.current_location.loc_id, location.loc_id)
        self.log.append(TruckLogEntry.new_drove_entry(self.current_location, location, distance, self.sim_time))
        self.current_location = location
        arrival_time = distance / self.speed_mph * 100 + self.sim_time.get_now()  # This math is failure prone!
        self.sim_time.add_event(EventTypes.TRUCK_ARRIVAL, arrival_time, self.truck_num)

    def get_next_destination(self) -> Location:
        """Get a reference to the next location the truck will go to.
        Returns none if it's at the hub and the end of its route."""
        # Find index of current location in route
        i = 0
        while i < len(self.route):
            this_loc = self.route[i]
            #
            if i > 0 and this_loc == self.route[-1]:
                return None
            if this_loc == self.current_location:
                return self.route[i + 1]
            i += 1

    def unload_packages_for_here(self) -> List[PackageGroup]:
        here_pg = [pg for pg in self.package_groups if pg.destination == self.current_location]
        if len(here_pg) == 0:
            raise TruckInvalidOperationError(f"No package groups currently loaded on truck {self.truck_num} are "
                                             f"destined for '{self.current_location.name}'")
        for pg in here_pg:
            self.unload_package_group(pg)
        return here_pg

    def drive_to_next(self):
        if self.route is None or len(self.route) == 0:
            self.determine_route()
        self.drive_to(self.get_next_destination())



    @classmethod
    def get_truck_loaded_on(cls, package_group: PackageGroup):
        return Truck.package_group_loading_dict.get(package_group)

    def __repr__(self):
        return f"Truck {self.truck_num}"

    def __str__(self):
        return f"Truck {self.truck_num}"


class TruckInvalidOperationError(Exception):
    """An operation was attempted that isn't valid for this truck right now."""

    def __init__(self, message):
        self.message = message


class TruckLogEntryType(Enum):
    LOADED = "Loaded packages"
    UNLOADED = "Unloaded package(s)"
    DROVE = "Drove to location"
    CREATED = "Truck object created"


class TruckLogEntry(object):

    def __init__(self, entry_type: TruckLogEntryType, time: float):
        self.time: float = time
        self.entry_type = entry_type

    @staticmethod
    def new_load_entry(sim_time, package, note: str = ""):
        output = TruckLogEntry(TruckLogEntryType.LOADED, sim_time.get_now())
        output.package = package
        output.note = note
        return output

    @staticmethod
    def new_unload_entry(package, sim_time, note: str = ""):
        output = TruckLogEntry(TruckLogEntryType.UNLOADED, sim_time.get_now())
        output.package = package
        output.note = note
        return output

    @staticmethod
    def new_drove_entry(start: Location, end: Location, distance: float, arrival_time, note: str = ""):
        output = TruckLogEntry(TruckLogEntryType.DROVE, arrival_time)
        output.start_location = start
        output.end_location = end
        output.distance = distance
        output.note = note
        return output
