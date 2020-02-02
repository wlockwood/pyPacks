from typing import List
import time
from data_loader import read_packages, read_locations
from model.location import Location
from model.package import Package, PackageStatus
from model.package_group import PackageGroup
from model.routing_table import RoutingTable
from model.truck import Truck
from model.sim_time import SimTime, EventAdder, EventTypes
from load_builder import LoadBuilder
import status_printer
from route_optimizer import RouteOptimizer


def prompt_with_check(prompt_string: str, input_options: List[str], allow_blank=True) -> str:
    while True:  # Don't trust users to enter rational things.
        input_options = [str(x) for x in input_options]
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
    locations.extend(Location.generate_fake_locations(500))
    test_routing_table = RoutingTable(locations)  # Build location+location distance lookup hash table

    # Testing lots of locations

    for count in range(25, len(locations), 25):
        print(f"-- Optimization strategies with {count} locations --")
        this_pass_locations = locations[1:count]
        optimizer = RouteOptimizer(this_pass_locations, test_routing_table, locations[0])
        start = time.perf_counter()
        route = optimizer.get_optimized_nn()
        elapsed = time.perf_counter() - start
        optimizer.print_route_evaluation(f"Nearest Neighbor N={len(this_pass_locations)}", route, elapsed)

        start = time.perf_counter()
        route = optimizer.get_optimized_cpm()
        elapsed = time.perf_counter() - start
        optimizer.print_route_evaluation(f"AS Coproximity N={len(this_pass_locations)}", route, elapsed)
    exit(0)

def cli_truck_load(trucks: List[Truck]):
    tn_opt_array = [x.truck_num for x in trucks]
    tn_opt_array.append("")
    while True:
        user_input = prompt_with_check("Load which truck? (blank to stop)", tn_opt_array)
        if user_input == "":
            break
        chosen_truck_num = int(user_input)
        chosen_truck = (x for x in trucks if x.truck_num == chosen_truck_num)[0]
        if chosen_truck is None:
            print("Not a valid truck number.")
            continue
        load_builder.determine_truckload(chosen_truck)

def cli_address_change(packages: List[Package], locations: List[Location]):
    # Get package to change
    while True:
        user_string = input(f"Input package Id of the package you'd like to update:")
        try:
            user_int = int(user_string)
            user_package = ([p for p in packages if p.package_id == user_int])[0]
            if user_package:
                break
        except ValueError:
            print(f"String '{user_string}' is not a valid package Id. Try again.")

    # Show current address
    old_dest = user_package.dest_location
    print(f"Package Id {user_package.package_id} is currently destined for {old_dest.name} at {old_dest.address}.")

    # Ask for new address
    while True:
        user_string = input(f"Input new address for package Id {user_package.package_id}:")

        # Attempt to match to a location id, err if not
        user_locations = ([l for l in locations if user_string.__contains__(l.address)])
        if len(user_locations) > 1:
            print(f"String '{user_string}' matches multiple locations:")
            for ul in user_locations:
                print(f" - {ul.address}")
        if len(user_locations) == 0:
            print(f"String '{user_string}' matches no known location.")
        found_location = user_locations[0]
        if found_location:
            break

    # Recalculate package groups for this id
    pg = PackageGroup.get_owning_package_group(user_package.package_id)
    new_pgs = pg.rebuild_package_group()

    # Recalculate route














"""
######### MAIN #########
Basic strategy: wait for all packages to come in, start delivering everything with a deadline.
"""
# Profiling-only mode
if False:
    #profile_bfs_by_locs()
    profile_optimization_strategies()
    exit(0)

sim_time = SimTime(800, 1700)  # Global time tracker
EventAdder.add_events(sim_time)

# Initial data load
locations = read_locations("sample_locations.csv")
packages = read_packages("sample_packages.csv", locations, sim_time)
routing_table = RoutingTable(locations)  # Build location+location distance lookup hash table

# Build trucks. There's a third truck, but I think it's an error in the instructions.
trucks = [Truck(1, sim_time, locations[0]), Truck(2, sim_time, locations[0])]
load_builder = LoadBuilder(locations, packages, trucks, routing_table)

# Main Interaction Loop
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
            cli_truck_load(trucks)
        elif user_input == "status":
            status_printer.print_package_status(packages)
            input(continue_string)
        elif user_input == "address change":
            cli_address_change(packages, locations, trucks)
        else:
            print("Continuing...")

print("Day over!")

# Print final stats
status_printer.print_package_status(packages)
driven = []
for t in trucks:
    my_dist = t.calculate_miles_driven()
    driven.append(my_dist)
    print(f"Truck {t.truck_num} drove {my_dist} miles.")
print(f"Total distance driven: {sum(driven)} miles")

