from typing import List
from data_loader import read_packages, read_locations
from model.location import Location
from model.package import Package, PackageStatus
from model.routing_table import RoutingTable
from model.truck import Truck
from model.sim_time import SimTime, EventAdder, EventTypes
from load_builder import LoadBuilder
import status_printer
from route_optimizer import RouteOptimizer


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


def profile_optimization_strategies():
    # Initial data load
    locations = read_locations("sample_locations.csv")
    test_routing_table = RoutingTable(locations)  # Build location+location distance lookup hash table

    # Testing lots of locations
    print("All standard locations")
    optimizer = RouteOptimizer(locations[1:5], test_routing_table, locations[0])
    optimizer.get_optimized_bfs()
    exit(0)

    optimizer.run_time_tests(100)


    print("Extra locations +50")
    locations.extend(Location.generate_fake_locations(50))
    test_routing_table = RoutingTable(locations)  # Build location+location distance lookup hash table

    optimizer = RouteOptimizer(locations[1:], test_routing_table, locations[0])
    optimizer.run_time_tests(100)

    print("Extra locations +500")
    locations.extend(Location.generate_fake_locations(500))
    test_routing_table = RoutingTable(locations)  # Build location+location distance lookup hash table
    optimizer = RouteOptimizer(locations[1:], test_routing_table, locations[0])
    optimizer.run_time_tests(100)


"""
######### MAIN #########
Basic strategy: wait for all packages to come in, start delivering everything with a deadline.
"""
# Profiling-only mode
if True:
    profile_optimization_strategies()
    exit(0)

sim_time = SimTime(800, 1700)  # Global time tracker
EventAdder.add_events(sim_time)

# Initial data load
locations = read_locations("sample_locations.csv")
packages = read_packages("sample_packages.csv", locations, sim_time)
routing_table = RoutingTable(locations)  # Build location+location distance lookup hash table

# Build trucks. There's a third truck, but I think it's an error in the instructions.
trucks = [Truck(1, sim_time), Truck(2, sim_time), Truck(3, sim_time)]
load_builder = LoadBuilder(locations, packages, trucks, routing_table)

total_dists = []
for truck in trucks:
    print(f"\n-------- Truck {truck.truck_num} --------")
    load_builder.determine_truckload(truck)
    route = RouteOptimizer(truck.get_locations_on_route(), routing_table, locations[0])
    nn_route = route.get_optimized_nn()
    cpm_route = route.get_optimized_cpm()

    route.print_route_evaluation("Unoptimized", route.route_locs)
    route.print_route_evaluation("Nearest neighbor", nn_route)
    route.print_route_evaluation("Antisocial Coproximity", cpm_route)

    route.run_time_tests(1000)

print("All locations, test only")
all_locations_route = RouteOptimizer(locations[1:], routing_table, locations[0])

all_locations_route.run_time_tests()

continue_string = "Press enter to continue"  # I hate this, but "any key" is apparently platform dependent
while sim_time.in_business_hours():
    events_triggered_this_minute = sim_time.increment()
    if sim_time.get_now() % 100 == 0 or any(events_triggered_this_minute):
        print("Time: ", sim_time.get_now())
    if any(events_triggered_this_minute):
        for e in events_triggered_this_minute:
            print(e)
            if e.event_type == EventTypes.DELAYED_PACKAGES_ARRIVED:
                delayed_packages_arrive(packages)
            if e.event_type == EventTypes.REQ_STATUS_CHECK:
                status_printer.print_package_status(packages)
                input(continue_string)
        user_input = prompt_with_check("Input command:", ["load", "status", "address change"])
        if user_input == "load":
            load_builder.determine_truckload(trucks[0])
        elif user_input == "status":
            status_printer.print_package_status(packages)
            input(continue_string)
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
