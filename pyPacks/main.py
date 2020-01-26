from typing import List
from data_loader import read_packages, read_locations
from model.package import Package, PackageStatus
from model.routing_table import RoutingTable
from model.truck import Truck
from model.sim_time import SimTime, EventAdder, EventTypes
from load_builder import LoadBuilder


def prompt_with_check(prompt_string: str, input_options: List[str], allow_blank=True) -> str:
    while True:  # Don't trust users to enter rational things.
        user_string = input(f"{prompt_string} ({', '.join(input_options)})\n").lower()
        if (user_string == "" and allow_blank) or user_string in input_options:
            return user_string
        else:
            print(f"'{user_string}' isn't a valid option.")

def delayed_packages_arrive(packages: List[Package]):
    for p in [x for x in packages if x.status == PackageStatus.DELAYED]:
        p.update_status(PackageStatus.READY_FOR_PICKUP)


"""
######### MAIN #########
Basic strategy: wait for all packages to come in, start delivering everything with a deadline.
"""
sim_time = SimTime(800, 1700)  # Global time tracker
EventAdder.add_events(sim_time)

# Initial data load
locations = read_locations("sample_locations.csv")
packages = read_packages("sample_packages.csv", locations, sim_time)
routing_table = RoutingTable(locations)  # Build location+location distance lookup hash table

# Build trucks. There's a third truck, but I think it's an error in the instructions.
trucks = [Truck(1, sim_time), Truck(2, sim_time), Truck(3, sim_time)]
load_builder = LoadBuilder(locations, packages, trucks, routing_table)

print("\n-------- Truck 1 --------")
load_builder.determine_truckload(trucks[0])
print("\n-------- Truck 2 --------")
load_builder.determine_truckload(trucks[1])
print("\n-------- Truck 3 --------")
load_builder.determine_truckload(trucks[2])
exit(0)

while sim_time.in_business_hours():
    events_triggered_this_minute = sim_time.increment()
    if sim_time.get_now() % 100 == 0 or any(events_triggered_this_minute):
        print("Time: ", sim_time.get_now())
    if any(events_triggered_this_minute):
        for e in events_triggered_this_minute:
            print(e)
            if e.event_type == EventTypes.DELAYED_PACKAGES_ARRIVED:
                delayed_packages_arrive(packages)
        user_input = prompt_with_check("Input command:", ["load", "status", "address change"])
        if user_input == "load":
            print("TODO: Just load a truck? Not sure.")
        elif user_input == "status":
            print("TODO: write package status display code")
        elif user_input == "address change":
            print("TODO: write address change code")
        else:
            print("Continuing...")

print("Day over!")

"""
Flow:
Build suggested delivery pattern
Execute delivery pattern until delayed package time is hit
"""

# TODO: Print snapshots of current package status
# TODO: Print snapshots of truck location
