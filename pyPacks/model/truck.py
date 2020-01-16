"""
Trucks should keep a log of where they've been and the packages they contain.
Trucks should offer a method to calculate miles driven, packages delivered, and time spent driving.

"""
from enum import Enum, auto


class Truck(object):
    def __init__(self, truck_num):
        self.package_capacity = 16  # Defined in spec
        self.speed_mph = 18  # Defined in spec
        self.packages = []  # Packages currently on truck
        self.log = []  # Events involving this truck
        self.truck_num = truck_num
        self.current_location = 0  # All trucks start at hub / WGU

    def load_package(self, package):
        self.packages += package
        self.log.append(TruckLogEntry.new_load_entry(package))
        print(f"Loaded package {package.package_id} onto truck {self.truck_num}. "
              f"Now at {len(self.packages)} on truck")

    def load_packages(self, packages):
        for package in packages:
            self.load_package(package)

    def unload_package(self, package):
        self.packages.remove(package)
        self.log.append(TruckLogEntry.new_unload_entry(package))
        print(f"Unloaded package {package.package_id} from truck {self.truck_num}. "
              f"Now at {len(self.packages)} on truck.")

    def unload_packages(self, packages):
        for package in packages:
            self.unload_package(package)

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

    @staticmethod
    def new_load_entry(package, time):
        output = TruckLogEntry()
        output.entry_type = TruckLogEntryType.LOADED
        output.package = package
        return output

    @staticmethod
    def new_unload_entry(package, time):
        output = TruckLogEntry()
        output.entry_type = TruckLogEntryType.UNLOADED
        output.package = package
        return output

    @staticmethod
    def new_drove_entry(start, end, distance):
        output = TruckLogEntry()
        output.entry_type = TruckLogEntryType.DROVE
        output.start_location = start
        output.end_location = end
        output.distance = distance
        return output
