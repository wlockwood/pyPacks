""" Routing logic
 - Group undelivered packages by location and availability
 - Pick the farthest package from the hub with achievable constraints and the earliest deadline
 - Find nearest neighbor groups until truck is full (nearest-neighbor should use a heap)
 - - Make sure no location is partially loaded on a truck
 - Once truck is full, add "return to hub" to location node list and brute-force the best route.

 Constraints and requirements
 - Must be able to recalculate at an arbitrary time. Recalculation shouldn't interrupt package delivery.
 - Some packages must be delivered with other specified packages. "Linked packages"
 - Some packages will arrive late and can't be picked up until a specified time.
 - Some packages can only be on certain trucks.

Possible Upgrades:
 - If truck approaches within x miles of hub with less than y% capacity, pick up more packages.
    This could be implemented by checking to see if a route X->Y is longer than X->Hub. Only do this if packages
    that can be picked up are close to other routed nodes.
 - Maybe: If deadlines for special constraint packages can't be met reliably, add a "truck holding pattern"
    option that keeps it nearby or at the hub.
 - Maybe: Try alternate starting points to see if that results in a more optimal result.
 - Maybe: If X->Y is not significantly longer than X->M->Y, trim X->Y?
 - Maybe: Check if any nodes are closer to our nodes than the ones we have selected?

 Metrics:
 - Total miles driven
 - Total time taken
 - Miles per package and time per package
 - Time per location

"""
from itertools import groupby
from typing import List, Set
from model.package_group import PackageGroup
from model.package import Package, PackageStatus
from model.routing_table import RoutingTable
from model.truck import Truck
from model.location import Location


class LoadBuilder(object):

    def __init__(self, locations, packages, trucks, routing_table: RoutingTable):
        self.locations = locations
        self.packages = packages
        self.package_groups = self.group_packages(packages)
        self.build_pg_object_links(self.package_groups)

        self.trucks = trucks
        self.routing_table = routing_table

    @staticmethod
    def group_packages(packages):
        """Group undelivered packages by location and availability."""
        # Group package by location and status
        keyfunc = lambda x: x.dest_location.id + "-" + x.status.value
        sorted_packs = sorted(packages, key=keyfunc)
        grouped_packs = groupby(sorted_packs, keyfunc)

        # Turn Grouper objects into PackageGroups
        package_groups = []
        for k, v in grouped_packs:
            this_pg = PackageGroup(list(v))
            package_groups.append(this_pg)
            # print(f"Location {k} has {sum(1 for x in this_pg.packages)} packages")
        return package_groups

    @staticmethod
    def build_pg_object_links(package_groups: List[PackageGroup]):
        for pg in package_groups:
            link_ids = pg.get_linked_package_ids()
            for a_linked_id in link_ids:
                linked_pg = PackageGroup.get_owning_package_group(a_linked_id)
                pg.linked_package_groups.append(linked_pg)

    def choose_starting_group(self) -> PackageGroup:
        """Pick the farthest unconstrained package from the hub, prioritizing earlier deadlines."""
        # TODO: Add priority for packages with early deliver deadlines
        available_packages = [x for x in self.package_groups if x.get_status() == PackageStatus.READY_FOR_PICKUP]
        farthest_package_group = max(available_packages, key=lambda x: self.routing_table.lookup(1, x.destination.id))
        print(farthest_package_group)
        return farthest_package_group

    def determine_truckload(self, truck: Truck):
        """Loads a truck's worth of packages.
        Starts with farthest valid package and picks nearest neighbors from there until full."""
        # TODO: Seriously, prioritize package groups with deadlines
        available_pgroups: List[PackageGroup] = [x for x in self.package_groups if
                                                 x.get_status() == PackageStatus.READY_FOR_PICKUP]
        location_skip_list: List[Location] = []  # Locations that need too many packages delivered to fit in what's left
        last = self.choose_starting_group()
        truck.load_package_group(last)

        while truck.get_package_count() < truck.package_capacity:
            # Find the next nearest place that needs a delivery
            # valid_locations is available_pgroups less already loaded locations
            valid_locations = \
                [pg.destination for pg in available_pgroups if pg.destination not in truck.get_locations_on_route()
                 and pg.destination not in location_skip_list]
            try:
                nn_loc: Location = self.routing_table.get_nearest_neighbor_of_set(last.destination, valid_locations)
            except ValueError:
                print("No more packages available for this truck at this time.")
                break
            nn_pg: PackageGroup = [x for x in available_pgroups if x.destination == nn_loc][0]

            # Check for linked packages/groups
            linked_pgs = nn_pg.get_linked_package_groups()

            linked_count = sum([x.get_count() for x in linked_pgs])
            if len(linked_pgs) > 1:
                print(f"Attempting to load {linked_count} linked packages: {linked_pgs}")

            # Check to see if this PackageGroup will fit
            can_fit = truck.get_package_count() + linked_count <= truck.package_capacity
            allowed_on_truck = len(nn_pg.packages[0].valid_truck_ids) == 0 or \
                               truck.truck_num in nn_pg.packages[0].valid_truck_ids
            if can_fit and allowed_on_truck:  # Allowed to be on this truck
                for pg in linked_pgs:
                    truck.load_package_group(pg)
            else:
                location_skip_list.append(nn_loc)  # Bypass this location next time

        # Determine rough stats using nearest neighbor routing.
        locations = [x.destination for x in truck.package_groups]
        i = 0
        distances: List[float] = []
        while i < (len(locations) - 1):
            distances.append(self.routing_table.lookup(locations[i].id, locations[i + 1].id))
            i += 1
        total = sum(distances)
        ids_string = ', '.join([str(x) for x in truck.get_loaded_ids()])
        print("Final loaded IDs: " + ids_string)
        print("Distances:", distances)
        print(f"Total: {total:.1f}")
        print(f"Time to drive: {(total / 18):.1f}h")
        return None

    # TODO: Create method for optimizing routes.
